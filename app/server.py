import os
import json
import logging
import asyncio
from functools import partial
from datetime import datetime, timezone, timedelta
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import tornado.ioloop
import tornado.web
from tornado.websocket import WebSocketHandler
from dotenv import load_dotenv
import numpy as np
from statsmodels.tsa.seasonal import STL

from app.db import (
    create_pool,
    init_schema,
    upsert_ohlc_bars,
    fetch_ohlc_bars,
    fetch_ohlc_bars_range,
    ohlc_range,
    set_pref,
    get_pref,
    latest_bar_ts,
    set_prefs,
    get_prefs,
    create_stl_run,
    insert_stl_components,
    list_stl_runs,
    get_stl_run,
    delete_stl_run,
    fetch_stl_run_data,
)
from app.mt5_client import client as mt5_client
from app.strategy import crossover_strategy
from app.news_fetcher import fetch_symbol_digest

try:
    from llm_model.echomind.mixed_ai_request import MixedAIRequestJSONBase  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    MixedAIRequestJSONBase = None  # type: ignore


EXECUTOR = ThreadPoolExecutor(max_workers=2)
logger = logging.getLogger("mt5app")

WS_CLIENTS: set = set()


NEWS_MICRO_QUESTIONS: list[dict[str, str]] = [
    {
        "id": "fed_hawkish_language",
        "label": "Fed hawkish tone",
        "question": "Does the article describe the Federal Reserve's latest communication as hawkish compared to recent statements?",
    },
    {
        "id": "rate_hike_currency_strength",
        "label": "Rate hikes strengthen currency",
        "question": "Does the article state that a central bank rate hike is strengthening its domestic currency?",
    },
    {
        "id": "ecb_data_tightening",
        "label": "ECB data-dependent tightening",
        "question": "Does the article portray the ECB as emphasizing inflation risks and data-dependent tightening?",
    },
    {
        "id": "fed_dual_mandate",
        "label": "Fed dual mandate mentioned",
        "question": "Does the article mention the Federal Reserve's dual mandate of maximum employment and price stability?",
    },
    {
        "id": "qe_money_supply",
        "label": "QE increases money supply",
        "question": "Does the article state that quantitative easing increases the money supply?",
    },
    {
        "id": "boe_vote_hawkish",
        "label": "BoE split is hawkish",
        "question": "Does the article state that a split Bank of England vote (with dissenters for hikes) is more hawkish than a unanimous hold?",
    },
    {
        "id": "cpi_rate_hike_probability",
        "label": "High CPI boosts hike odds",
        "question": "Does the article claim that higher-than-expected CPI increases the probability of a rate hike?",
    },
    {
        "id": "nfp_usd_strength",
        "label": "Strong NFP boosts USD",
        "question": "Does the article state that a strong Non-Farm Payrolls report strengthens the USD?",
    },
    {
        "id": "pmi_above_50_expansion",
        "label": "PMI > 50 means expansion",
        "question": "Does the article confirm that a PMI reading above 50 indicates economic expansion?",
    },
    {
        "id": "gdp_two_quarter_recession",
        "label": "Two negative GDP = recession",
        "question": "Does the article note that two consecutive quarters of negative GDP constitute a recession?",
    },
    {
        "id": "retail_sales_strength",
        "label": "Retail sales imply demand",
        "question": "Does the article say that stronger retail sales imply stronger consumer demand?",
    },
    {
        "id": "trade_surplus_supports_currency",
        "label": "Trade surplus supports FX",
        "question": "Does the article claim that a trade surplus supports the domestic currency?",
    },
    {
        "id": "low_unemployment_inflation_pressure",
        "label": "Low jobless rate lifts inflation",
        "question": "Does the article state that unemployment below the natural rate creates upward inflation pressure?",
    },
    {
        "id": "eurusd_usdchf_negative_corr",
        "label": "EUR/USD vs USD/CHF inverse",
        "question": "Does the article mention EUR/USD and USD/CHF moving in opposite directions?",
    },
    {
        "id": "aud_nzd_risk_on",
        "label": "AUD & NZD are risk-on",
        "question": "Does the article describe AUD or NZD as risk-on currencies?",
    },
    {
        "id": "jpy_chf_safe_haven",
        "label": "JPY & CHF safe havens",
        "question": "Does the article call JPY or CHF safe-haven currencies during market stress?",
    },
    {
        "id": "audusd_commodity_link",
        "label": "AUD/USD tied to commodities",
        "question": "Does the article link AUD/USD performance to commodity prices?",
    },
    {
        "id": "gbpusd_eurusd_positive_corr",
        "label": "GBP/USD mirrors EUR/USD",
        "question": "Does the article note GBP/USD and EUR/USD moving together?",
    },
    {
        "id": "dxy_rises_with_usd",
        "label": "DXY rises with USD",
        "question": "Does the article state that the US Dollar Index rises when the USD strengthens?",
    },
    {
        "id": "risk_on_high_yield",
        "label": "Risk-on favors carry FX",
        "question": "Does the article say that risk-on periods favor high-yielding currencies like AUD or NZD?",
    },
    {
        "id": "gold_safe_haven",
        "label": "Gold strengthens in risk-off",
        "question": "Does the article describe gold strengthening during risk-off market conditions?",
    },
    {
        "id": "equity_rally_risk_on",
        "label": "Equity rally = risk-on",
        "question": "Does the article associate strong equity rallies with risk-on sentiment?",
    },
    {
        "id": "vix_spike_risk_off",
        "label": "VIX spike = risk-off",
        "question": "Does the article claim that a spike in the VIX signals risk-off sentiment?",
    },
    {
        "id": "em_fx_weakens_crisis",
        "label": "EM FX weakens in crises",
        "question": "Does the article report emerging-market currencies weakening during geopolitical crises?",
    },
    {
        "id": "carry_trade_borrow_low",
        "label": "Carry trade borrow low",
        "question": "Does the article explain that carry traders borrow low-yield currencies and buy high-yield ones?",
    },
    {
        "id": "widening_diff_strengthens_currency",
        "label": "Wider differentials boost FX",
        "question": "Does the article say widening interest-rate differentials strengthen the higher-yield currency?",
    },
    {
        "id": "fed_vs_boj_usdjpy",
        "label": "Fed vs BoJ lifts USD/JPY",
        "question": "Does the article state that Fed hikes versus BoJ easing strengthen USD/JPY?",
    },
    {
        "id": "inflation_erodes_power",
        "label": "Inflation erodes purchasing power",
        "question": "Does the article state that higher inflation weakens a currency's purchasing power?",
    },
    {
        "id": "positive_surprise_strengthens_currency",
        "label": "Positive surprises lift FX",
        "question": "Does the article report that better-than-expected economic data strengthens the referenced currency?",
    },
    {
        "id": "rate_cut_depreciation",
        "label": "Rate cuts weaken currency",
        "question": "Does the article say an unexpected rate cut leads to currency depreciation?",
    },
]

_NEWS_QUESTION_IDS = [item["id"] for item in NEWS_MICRO_QUESTIONS]
NEWS_ANALYSIS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "answers": {
            "type": "array",
            "minItems": len(_NEWS_QUESTION_IDS),
            "maxItems": len(_NEWS_QUESTION_IDS),
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "enum": _NEWS_QUESTION_IDS},
                    "answer": {"type": "string", "enum": ["yes", "no"]},
                },
                "required": ["id", "answer"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["answers"],
    "additionalProperties": False,
}

AI_CLIENT = None


def _compose_article_payload(article: dict[str, Any]) -> tuple[str, str]:
    """Return article_id, combined text from the incoming payload."""
    parts: list[str] = []
    title = str(article.get("title") or article.get("headline") or "").strip()
    summary = str(article.get("summary") or article.get("description") or "").strip()
    body = str(
        article.get("body")
        or article.get("content")
        or article.get("text")
        or ""
    ).strip()
    url = str(article.get("url") or "").strip()
    if title:
        parts.append(f"Title: {title}")
    if summary and summary.lower() != title.lower():
        parts.append(f"Summary: {summary}")
    if body:
        parts.append(f"Body: {body}")
    if url:
        parts.append(f"Source URL: {url}")
    article_text = "\n\n".join(parts).strip()
    article_id = str(
        article.get("article_id")
        or article.get("id")
        or url
        or f"{hash(title + summary) & 0xFFFFFFFF:X}"
    )
    return article_id, article_text


def _build_news_prompt(article_text: str) -> str:
    question_lines = []
    for idx, item in enumerate(NEWS_MICRO_QUESTIONS, start=1):
        question_lines.append(f"{idx}. {item['id']}: {item['question']}")
    questions_block = "\n".join(question_lines)
    return (
        "You are an analyst that only answers with JSON. "
        "Read the news article and answer each question with \"yes\" or \"no\". "
        "If the article does not provide enough evidence, answer \"no\". "
        "Base answers solely on the article provided.\n\n"
        f"Article:\n---\n{article_text}\n---\n\n"
        "Questions:\n"
        f"{questions_block}\n\n"
        "Respond using the provided JSON schema."
    )


def _run_news_analysis(ai_client: MixedAIRequestJSONBase, article_text: str) -> dict[str, Any]:
    prompt = _build_news_prompt(article_text)
    return ai_client.send_request_with_json_schema(
        prompt,
        NEWS_ANALYSIS_SCHEMA,
        system_content="You are a precise analyst. Reply only with JSON that matches the schema.",
        schema_name="news_micro_answers",
    )


async def _broadcast_ws(event: dict[str, object]) -> None:
    """Send an event to all connected websocket clients."""
    if not WS_CLIENTS:
        return
    msg = json.dumps(event)
    dead = []
    futures = []
    for client in list(WS_CLIENTS):
        try:
            fut = client.write_message(msg)
            if fut is not None:
                futures.append(fut)
        except Exception:
            dead.append(client)
    for client in dead:
        WS_CLIENTS.discard(client)
    if futures:
        await asyncio.gather(*futures, return_exceptions=True)


async def emit_fetch_event(
    *,
    symbol: str,
    timeframe: str,
    mode: str,
    fetch_mode: str | None,
    inserted: int,
    fetched: int,
    scope: str | None,
    background: bool,
    status: str,
    note: str | None = None,
    error: str | None = None,
) -> None:
    """Broadcast a standardized fetch-complete event to connected clients."""
    event = {
        "type": "fetch_complete",
        "ts": datetime.now(timezone.utc).isoformat(),
        "symbol": symbol.upper(),
        "timeframe": timeframe.upper(),
        "mode": mode,
        "fetch_mode": fetch_mode,
        "inserted": inserted,
        "fetched": fetched,
        "scope": scope,
        "background": background,
        "status": status,
    }
    if note:
        event["note"] = note
    if error:
        event["error"] = error
    await _broadcast_ws(event)


async def emit_stl_event(
    *,
    symbol: str,
    timeframe: str,
    period: int | None,
    status: str,
    scope: str | None,
    background: bool,
    points: int | None = None,
    note: str | None = None,
    run_id: int | None = None,
    start_ts: str | None = None,
    end_ts: str | None = None,
    created_at: str | None = None,
    error: str | None = None,
) -> None:
    event = {
        "type": "stl_complete",
        "ts": datetime.now(timezone.utc).isoformat(),
        "symbol": symbol.upper(),
        "timeframe": timeframe.upper(),
        "period": period,
        "status": status,
        "scope": scope,
        "background": background,
    }
    if run_id is not None:
        event["run_id"] = run_id
    if points is not None:
        event["points"] = points
    if start_ts:
        event["start_ts"] = start_ts
    if end_ts:
        event["end_ts"] = end_ts
    if created_at:
        event["created_at"] = created_at
    if note:
        event["note"] = note
    if error:
        event["error"] = error
    await _broadcast_ws(event)


ALL_TIMEFRAMES = ["M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1", "MN1", "Y1"]
PREF_KEYS = ["last_symbol", "last_tf", "last_count", "chart_type", "last_volume", "last_sl", "last_tp", "last_fast", "last_slow"]

def _default_backfill_days(tf: str) -> int:
    tf = (tf or "").upper()
    if tf == "Y1":
        return 3650  # ~10 years
    if tf.startswith("MN"):
        return 1825  # ~5 years
    if tf.startswith("W"):
        return 1000
    if tf.startswith("D"):
        return 2000
    if tf.startswith("H"):
        return 365
    return 30


STL_PERIOD_MAP = {
    "M1": 1440,
    "M5": 288,
    "M15": 96,
    "M30": 48,
    "H1": 24,
    "H4": 6,
    "D1": 30,
    "W1": 26,
    "MN1": 12,
    "Y1": 10,
}


def _stl_period_for_tf(tf: str) -> int:
    return STL_PERIOD_MAP.get((tf or "").upper(), 30)


def _normalize_dt(value):
    if value is None:
        return None
    if isinstance(value, str):
        value = datetime.fromisoformat(value)
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value


def _dt_to_iso(value):
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat()


def _serialize_run(run: dict | None) -> dict | None:
    if not run:
        return None
    return {
        "id": run["id"],
        "symbol": run["symbol"],
        "timeframe": run["timeframe"],
        "period": run["period"],
        "start_ts": _dt_to_iso(run.get("start_ts")),
        "end_ts": _dt_to_iso(run.get("end_ts")),
        "rows_count": run.get("rows_count"),
        "created_at": _dt_to_iso(run.get("created_at")),
    }


async def _compute_and_store_stl(
    pool,
    symbol: str,
    timeframe: str,
    *,
    period: int | None = None,
    start_dt: datetime | None = None,
    end_dt: datetime | None = None,
) -> dict:
    range_info = await ohlc_range(pool, symbol, timeframe)
    if not range_info:
        raise ValueError("No bar data available for STL decomposition")
    dataset_start = range_info["start_ts"]
    dataset_end = range_info["end_ts"]
    start_dt = _normalize_dt(start_dt) or dataset_start
    end_dt = _normalize_dt(end_dt) or dataset_end
    if start_dt < dataset_start:
        start_dt = dataset_start
    if end_dt > dataset_end:
        end_dt = dataset_end
    if end_dt < start_dt:
        raise ValueError("End timestamp precedes start timestamp for STL computation")
    rows = await fetch_ohlc_bars_range(
        pool,
        symbol,
        timeframe,
        start_ts=start_dt,
        end_ts=end_dt,
    )
    if not rows:
        raise ValueError("No bar data found in requested range for STL decomposition")
    times: list[datetime] = []
    closes: list[float] = []
    for row in rows:
        close = row.get("close")
        ts_raw = row.get("ts")
        if close is None or ts_raw is None:
            continue
        try:
            ts = datetime.fromisoformat(ts_raw)
        except Exception as exc:  # pragma: no cover - defensive
            raise ValueError(f"Invalid timestamp encountered: {ts_raw}") from exc
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        times.append(ts)
        closes.append(float(close))
    if len(closes) < 12:
        raise ValueError(f"Not enough samples ({len(closes)}) for STL decomposition")
    base_period = period or _stl_period_for_tf(timeframe)
    base_period = max(3, int(base_period))
    adjusted_period = min(base_period, max(3, len(closes) // 2))
    if adjusted_period < 3:
        raise ValueError("Unable to determine a valid STL period for the available data")
    series = np.asarray(closes, dtype=float)
    if not np.isfinite(series).all():
        mask = np.isfinite(series)
        series = series[mask]
        times = [t for t, keep in zip(times, mask, strict=False) if keep]
    if len(series) < 3:
        raise ValueError("Insufficient finite values for STL decomposition")
    stl = STL(series, period=adjusted_period, robust=True)
    res = stl.fit()
    records: list[dict] = []
    for ts, close_val, trend_val, seasonal_val, resid_val in zip(
        times,
        series,
        res.trend,
        res.seasonal,
        res.resid,
        strict=False,
    ):
        records.append(
            {
                "ts": ts,
                "close": float(close_val),
                "trend": float(trend_val),
                "seasonal": float(seasonal_val),
                "resid": float(resid_val),
            }
        )
    run_meta = await create_stl_run(
        pool,
        symbol=symbol,
        timeframe=timeframe,
        period=adjusted_period,
        start_ts=times[0],
        end_ts=times[-1],
        rows_count=len(series),
    )
    inserted = await insert_stl_components(pool, run_meta["id"], records)
    created_at = run_meta.get("created_at")
    return {
        "run_id": run_meta["id"],
        "inserted": inserted,
        "points": len(records),
        "period": adjusted_period,
        "start_ts": times[0].isoformat(),
        "end_ts": times[-1].isoformat(),
        "created_at": created_at.isoformat() if created_at else None,
    }


def _aggregate_yearly_from_monthly(symbol: str, monthly_bars: list[dict]) -> list[dict]:
    if not monthly_bars:
        return []
    # Ensure chronological order
    sorted_bars = sorted(
        (bar for bar in monthly_bars if bar.get("ts")),
        key=lambda b: b["ts"],
    )
    buckets: dict[int, dict] = {}
    for bar in sorted_bars:
        ts = bar["ts"]
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts)
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        year = ts.year
        high = bar.get("high")
        low = bar.get("low")
        tick_vol = int(bar.get("tick_volume") or 0)
        real_vol = int(bar.get("real_volume") or 0)
        spread = bar.get("spread")

        entry = buckets.get(year)
        if entry is None:
            entry = {
                "symbol": symbol,
                "timeframe": "Y1",
                "ts": ts,
                "open": float(bar.get("open") or 0),
                "high": float(high) if high is not None else float(bar.get("open") or 0),
                "low": float(low) if low is not None else float(bar.get("open") or 0),
                "close": float(bar.get("close") or 0),
                "tick_volume": tick_vol,
                "spread": int(spread or 0),
                "real_volume": real_vol,
            }
            buckets[year] = entry
        else:
            # Preserve earliest open
            entry["ts"] = ts
            entry["close"] = float(bar.get("close") or entry["close"])
            entry["tick_volume"] += tick_vol
            entry["real_volume"] += real_vol
            if spread:
                entry["spread"] = int(spread)

        entry = buckets[year]
        if high is not None:
            entry["high"] = max(entry["high"], float(high))
        if low is not None:
            entry["low"] = min(entry["low"], float(low))

    # Normalize lows/highs just in case
    for entry in buckets.values():
        if entry["low"] > entry["high"]:
            entry["low"], entry["high"] = entry["high"], entry["low"]

    return sorted(buckets.values(), key=lambda b: b["ts"])


async def _compute_yearly_bars(symbol: str, *, count: int | None = None, since: datetime | None = None) -> list[dict]:
    loop = tornado.ioloop.IOLoop.current()
    months_to_fetch = max((count or 20) * 12, 120)
    months_to_fetch = min(months_to_fetch, 1200)
    monthly_bars: list[dict] = []
    if since:
        since_dt = since
        if since_dt.tzinfo is None:
            since_dt = since_dt.replace(tzinfo=timezone.utc)
        # Go back an extra year to ensure full aggregation windows
        since_dt = since_dt - timedelta(days=370)
        fetch_fn = partial(mt5_client.fetch_bars_since, symbol, "MN1", since_dt)
        monthly_bars = await loop.run_in_executor(EXECUTOR, fetch_fn)
    else:
        fetch_fn = partial(mt5_client.fetch_bars, symbol, "MN1", months_to_fetch)
        monthly_bars = await loop.run_in_executor(EXECUTOR, fetch_fn)

    yearly = _aggregate_yearly_from_monthly(symbol, monthly_bars)
    if count and count > 0:
        yearly = yearly[-count:]
    return yearly


def schedule_symbol_backfill(pool, symbol: str, *, timeframes: list[str] | None = None):
    """Kick off a lightweight background job to enrich history for a symbol across timeframes."""
    tfs = timeframes or ALL_TIMEFRAMES
    loop = tornado.ioloop.IOLoop.current()
    logger.info("[backfill] scheduling %s across %d timeframes", symbol, len(tfs))

    async def _runner():
        now = datetime.now(timezone.utc)
        for tf in tfs:
            fetch_mode_name = "since"
            try:
                days = _default_backfill_days(tf)
                since = now - timedelta(days=days)
                if tf == "Y1":
                    bars = await _compute_yearly_bars(symbol, since=since)
                    fetch_mode_name = "derived_yearly"
                else:
                    fetch_fn = partial(mt5_client.fetch_bars_since, symbol, tf, since)
                    bars = await loop.run_in_executor(EXECUTOR, fetch_fn)
                    fetch_mode_name = "since"
                if bars:
                    inserted = await upsert_ohlc_bars(pool, bars)
                    logger.info("[backfill] %s %s +%d bars (inserted=%d)", symbol, tf, len(bars), inserted)
                    await emit_fetch_event(
                        symbol=symbol,
                        timeframe=tf,
                        mode="backfill",
                        fetch_mode=fetch_mode_name,
                        inserted=inserted,
                        fetched=len(bars),
                        scope="symbol_backfill",
                        background=True,
                        status="completed",
                        note=f"~{days}d window",
                    )
                else:
                    await emit_fetch_event(
                        symbol=symbol,
                        timeframe=tf,
                        mode="backfill",
                        fetch_mode=fetch_mode_name,
                        inserted=0,
                        fetched=0,
                        scope="symbol_backfill",
                        background=True,
                        status="completed",
                        note=f"~{days}d window (no new bars)",
                    )
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning("[backfill] %s %s failed: %s", symbol, tf, exc)
                await emit_fetch_event(
                    symbol=symbol,
                    timeframe=tf,
                    mode="backfill",
                    fetch_mode=fetch_mode_name,
                    inserted=0,
                    fetched=0,
                    scope="symbol_backfill",
                    background=True,
                    status="error",
                    error=str(exc),
                )
            await asyncio.sleep(0.1)

    loop.spawn_callback(_runner)


async def _perform_fetch(
    pool,
    symbol: str,
    timeframe: str,
    count: int,
    mode: str,
    *,
    schedule_backfill: bool = False,
    persist_selection: bool = False,
    event_scope: str | None = None,
    background: bool = False,
) -> dict:
    """Unified fetch routine used by both the interactive handler and bulk/background jobs."""
    loop = tornado.ioloop.IOLoop.current()
    info: dict[str, object] = {
        "ok": False,
        "symbol": symbol,
        "timeframe": timeframe,
        "mode": mode,
    }

    try:
        bars: list[dict] = []
        fetch_mode = None
        if timeframe == "Y1":
            fetch_mode = "derived_yearly"
            yearly_count = count if count and count > 0 else None
            bars = await _compute_yearly_bars(symbol, count=yearly_count)
            info["source_timeframe"] = "MN1"
        elif mode == "inc":
            last = await latest_bar_ts(pool, symbol, timeframe)
            if last:
                try:
                    fetch_mode = "inc"
                    fetch_fn = partial(mt5_client.fetch_bars_since, symbol, timeframe, last)
                    bars = await loop.run_in_executor(EXECUTOR, fetch_fn)
                    info["since"] = last.isoformat()
                except Exception as exc:
                    logger.warning("incremental fetch failed for %s %s: %s; retrying with full=%s", symbol, timeframe, exc, count)
                    fetch_mode = "full"
                    fetch_fn = partial(mt5_client.fetch_bars, symbol, timeframe, count)
                    bars = await loop.run_in_executor(EXECUTOR, fetch_fn)
            else:
                fetch_mode = "full"
                fetch_fn = partial(mt5_client.fetch_bars, symbol, timeframe, count)
                bars = await loop.run_in_executor(EXECUTOR, fetch_fn)
        elif mode == "full_async":
            days = _default_backfill_days(timeframe)

            async def _bg():
                since = datetime.now(timezone.utc) - timedelta(days=days)
                fetch_fn = partial(mt5_client.fetch_bars_since, symbol, timeframe, since)
                try:
                    new_bars = await loop.run_in_executor(EXECUTOR, fetch_fn)
                    if new_bars:
                        await upsert_ohlc_bars(pool, new_bars)
                        logger.info("/api/fetch full_async backfill %s %s: +%d", symbol, timeframe, len(new_bars))
                        await emit_fetch_event(
                            symbol=symbol,
                            timeframe=timeframe,
                            mode=mode,
                            fetch_mode="since",
                            inserted=len(new_bars),
                            fetched=len(new_bars),
                            scope=event_scope,
                            background=True,
                            status="completed",
                            note=f"backfill ~{days}d",
                        )
                    else:
                        await emit_fetch_event(
                            symbol=symbol,
                            timeframe=timeframe,
                            mode=mode,
                            fetch_mode="since",
                            inserted=0,
                            fetched=0,
                            scope=event_scope,
                            background=True,
                            status="completed",
                            note=f"backfill ~{days}d (no new bars)",
                        )
                except Exception as exc:  # pragma: no cover - logging only
                    logger.exception("full_async backfill failed for %s %s: %s", symbol, timeframe, exc)
                    await emit_fetch_event(
                        symbol=symbol,
                        timeframe=timeframe,
                        mode=mode,
                        fetch_mode="since",
                        inserted=0,
                        fetched=0,
                        scope=event_scope,
                        background=True,
                        status="error",
                        error=str(exc),
                    )

            loop.add_callback(_bg)
            info.update({"ok": True, "scheduled": True, "note": f"backfill ~{days}d", "inserted": 0, "fetched": 0})
            if persist_selection:
                try:
                    await set_prefs(pool, {
                        "last_symbol": symbol.upper(),
                        "last_tf": timeframe,
                        "last_count": str(count),
                    })
                except Exception:  # pragma: no cover
                    logger.debug("failed to persist last selection")
            await emit_fetch_event(
                symbol=symbol,
                timeframe=timeframe,
                mode=mode,
                fetch_mode="since",
                inserted=0,
                fetched=0,
                scope=event_scope,
                background=True,
                status="scheduled",
                note=f"backfill ~{days}d",
            )
            return info
        else:
            fetch_mode = "full"
            fetch_fn = partial(mt5_client.fetch_bars, symbol, timeframe, count)
            bars = await loop.run_in_executor(EXECUTOR, fetch_fn)

        inserted = 0
        fetched = len(bars)
        if bars:
            inserted = await upsert_ohlc_bars(pool, bars)
        if persist_selection:
                try:
                    await set_prefs(pool, {
                        "last_symbol": symbol.upper(),
                        "last_tf": timeframe,
                        "last_count": str(count),
                    })
                except Exception:  # pragma: no cover
                    logger.debug("failed to persist last selection")

        info.update({
            "ok": True,
            "inserted": inserted,
            "fetched": fetched,
            "fetch_mode": fetch_mode,
        })

        if schedule_backfill:
            schedule_symbol_backfill(pool, symbol)

        await emit_fetch_event(
            symbol=symbol,
            timeframe=timeframe,
            mode=mode,
            fetch_mode=fetch_mode,
            inserted=inserted,
            fetched=fetched,
            scope=event_scope,
            background=background or (mode == "full_async"),
            status="ok",
            note=info.get("since"),
        )

        return info

    except Exception as exc:
        info["error"] = str(exc)
        logger.exception("fetch error %s %s (%s): %s", symbol, timeframe, mode, exc)
        await emit_fetch_event(
            symbol=symbol,
            timeframe=timeframe,
            mode=mode,
            fetch_mode=None,
            inserted=0,
            fetched=0,
            scope=event_scope,
            background=background or (mode == "full_async"),
            status="error",
            error=str(exc),
        )
        return info


def _parse_supported_symbols():
    raw = (
        os.getenv("MT5_SYMBOL_LIST")
        or os.getenv("SUPPORTED_SYMBOLS")
        or os.getenv("SYMBOL_LIST")
        or "XAUUSD, XAGUSD, EURUSD, GBPUSD, USDJPY, USDCHF, USDCAD, AUDUSD, NZDUSD, MSFT, NVDA, TSLA, AAPL, AMZN, GOOGL, META, NFLX"
    )
    symbols = []
    for item in raw.split(","):
        sym = item.strip().upper()
        if sym and sym not in symbols:
            symbols.append(sym)
    return symbols or ["XAUUSD"]


SUPPORTED_SYMBOLS = _parse_supported_symbols()


def default_symbol():
    return SUPPORTED_SYMBOLS[0] if SUPPORTED_SYMBOLS else "XAUUSD"


def refresh_supported_symbols():
    global SUPPORTED_SYMBOLS
    SUPPORTED_SYMBOLS = _parse_supported_symbols()
    return SUPPORTED_SYMBOLS


class MainHandler(tornado.web.RequestHandler):
    async def get(self):
        # Read last selection from prefs if available
        pool = self.settings.get("pool")
        last_sym = None
        last_tf = None
        extras = {}
        if pool is not None:
            try:
                last_sym = await get_pref(pool, "last_symbol")
                last_tf = await get_pref(pool, "last_tf")
                extras = await get_prefs(pool, ["last_count", "chart_type", "last_volume", "last_sl", "last_tp", "last_fast", "last_slow", "stl_auto_period", "stl_manual_period"])
            except Exception:
                extras = {}
                logger.debug("no prefs yet for last_symbol/last_tf")

        sym = (last_sym or default_symbol()).upper()
        if sym not in SUPPORTED_SYMBOLS:
            sym = default_symbol()
        tf = (last_tf or "H1").upper()
        if tf not in ALL_TIMEFRAMES:
            tf = "H1"
        extras = extras or {}
        count_pref = extras.get("last_count") or "500"
        chart_pref = (extras.get("chart_type") or "candlestick").lower()
        volume_pref = extras.get("last_volume") or "0.10"
        sl_pref = extras.get("last_sl") or ""
        tp_pref = extras.get("last_tp") or ""
        fast_pref = extras.get("last_fast") or "20"
        slow_pref = extras.get("last_slow") or "50"
        stl_auto_pref = extras.get("stl_auto_period") or "1"
        stl_manual_pref = extras.get("stl_manual_period") or "30"

        logger.debug("Render index with symbols=%s default=%s tf=%s", SUPPORTED_SYMBOLS, sym, tf)
        try:
            _sym_json = json.dumps(SUPPORTED_SYMBOLS)
            _def_json = json.dumps(sym)
            logger.debug("index config JSON sizes: symbols=%d default=%d", len(_sym_json), len(_def_json))
        except Exception:
            logger.exception("failed to serialize symbols/default for template")
        self.render(
            "index.html",
            symbols=SUPPORTED_SYMBOLS,
            default_symbol=sym,
            symbols_json=json.dumps(SUPPORTED_SYMBOLS),
            default_symbol_json=json.dumps(sym),
            symbols_csv=",".join(SUPPORTED_SYMBOLS),
            default_symbol_plain=sym,
            default_count=count_pref,
            default_chart_type=chart_pref,
            default_volume=volume_pref,
            default_sl=sl_pref,
            default_tp=tp_pref,
            default_fast=fast_pref,
            default_slow=slow_pref,
            default_tf=tf,
            default_stl_auto_period=stl_auto_pref,
            default_stl_manual_period=stl_manual_pref,
        )


class FetchHandler(tornado.web.RequestHandler):
    def initialize(self, pool):
        self.pool = pool

    async def get(self):
        symbol = self.get_argument("symbol", default=default_symbol())
        timeframe = self.get_argument("tf", default="H1").upper()
        count = int(self.get_argument("count", default="500"))
        mode = self.get_argument("mode", default="inc")  # inc | full_async | full
        logger.info("/api/fetch symbol=%s tf=%s count=%s mode=%s", symbol, timeframe, count, mode)
        schedule_backfill = (mode == "inc")
        info = await _perform_fetch(
            self.pool,
            symbol,
            timeframe,
            count,
            mode,
            schedule_backfill=schedule_backfill,
            persist_selection=True,
            event_scope="interactive",
            background=(mode != "inc"),
        )
        if info.get("ok"):
            logger.info(
                "/api/fetch ok symbol=%s tf=%s fetched=%s inserted=%s mode=%s",
                symbol,
                timeframe,
                info.get("fetched", 0),
                info.get("inserted", 0),
                info.get("fetch_mode"),
            )
        else:
            logger.warning("/api/fetch error symbol=%s tf=%s: %s", symbol, timeframe, info.get("error"))
        self.set_header("Content-Type", "application/json")
        self.finish(json.dumps(info))


class DataHandler(tornado.web.RequestHandler):
    def initialize(self, pool):
        self.pool = pool

    async def get(self):
        symbol = self.get_argument("symbol", default=default_symbol())
        timeframe = self.get_argument("tf", default="H1").upper()
        limit = int(self.get_argument("limit", default="500"))
        logger.debug("/api/data symbol=%s tf=%s limit=%s", symbol, timeframe, limit)
        rows = await fetch_ohlc_bars(self.pool, symbol, timeframe, limit)
        self.set_header("Content-Type", "application/json")
        self.finish(json.dumps({"symbol": symbol, "timeframe": timeframe, "rows": rows}))


class BulkFetchHandler(tornado.web.RequestHandler):
    def initialize(self, pool):
        self.pool = pool

    async def post(self):
        payload: dict[str, object] = {}
        if self.request.body:
            ctype = self.request.headers.get("Content-Type", "")
            if "json" in ctype:
                try:
                    payload = json.loads(self.request.body.decode() or "{}")
                except Exception:
                    payload = {}
        # Query params override defaults if provided
        for k, v in self.request.arguments.items():
            if v:
                payload[k] = v[0].decode() if isinstance(v[0], (bytes, bytearray)) else v[0]

        symbol = str(payload.get("symbol") or default_symbol()).upper()
        timeframe = str(payload.get("timeframe") or payload.get("tf") or "H1").upper()
        mode = str(payload.get("mode") or "inc")
        scope = str(payload.get("scope") or "symbol_all_tf")
        count = int(payload.get("count") or 500)

        timeframes = payload.get("timeframes")
        if isinstance(timeframes, str):
            timeframes = [tf.strip().upper() for tf in timeframes.split(",") if tf.strip()]
        elif isinstance(timeframes, list):
            timeframes = [str(tf).strip().upper() for tf in timeframes if str(tf).strip()]
        else:
            timeframes = None

        symbols_param = payload.get("symbols")
        if isinstance(symbols_param, str):
            symbols_list = [s.strip().upper() for s in symbols_param.split(",") if s.strip()]
        elif isinstance(symbols_param, list):
            symbols_list = [str(s).strip().upper() for s in symbols_param if str(s).strip()]
        else:
            symbols_list = None

        tasks: list[tuple[str, str]] = []
        if scope == "symbol_tf":
            tasks = [(symbol, timeframe)]
        elif scope == "symbol_all_tf":
            tfs = timeframes or ALL_TIMEFRAMES
            tasks = [(symbol, tf) for tf in tfs]
        elif scope == "all_symbols":
            syms = symbols_list or SUPPORTED_SYMBOLS
            tfs = timeframes or ALL_TIMEFRAMES
            tasks = [(sym, tf) for sym in syms for tf in tfs]
        else:
            self.set_status(400)
            self.set_header("Content-Type", "application/json")
            self.finish(json.dumps({"ok": False, "error": f"unknown scope {scope}"}))
            return

        if not tasks:
            self.set_status(400)
            self.set_header("Content-Type", "application/json")
            self.finish(json.dumps({"ok": False, "error": "no tasks scheduled"}))
            return

        async def runner():
            logger.info("[bulk] starting %d fetch jobs scope=%s mode=%s count=%s", len(tasks), scope, mode, count)
            total_inserted = 0
            total_fetched = 0
            errors = 0
            for sym, tf in tasks:
                info = await _perform_fetch(
                    self.pool,
                    sym,
                    tf,
                    count,
                    mode,
                    schedule_backfill=False,
                    persist_selection=False,
                    event_scope=scope,
                    background=True,
                )
                if info.get("ok"):
                    logger.info("[bulk] %s %s ok fetched=%s inserted=%s", sym, tf, info.get("fetched"), info.get("inserted"))
                    total_inserted += int(info.get("inserted") or 0)
                    total_fetched += int(info.get("fetched") or 0)
                else:
                    logger.warning("[bulk] %s %s error: %s", sym, tf, info.get("error"))
                    errors += 1
                await asyncio.sleep(0.1)
            logger.info("[bulk] completed scope=%s jobs=%d inserted=%d fetched=%d errors=%d", scope, len(tasks), total_inserted, total_fetched, errors)

        tornado.ioloop.IOLoop.current().spawn_callback(runner)

        self.set_header("Content-Type", "application/json")
        self.finish(
            json.dumps(
                {
                    "ok": True,
                    "scheduled": True,
                    "jobs": len(tasks),
                    "scope": scope,
                    "mode": mode,
                }
            )
        )

    async def get(self):
        return await self.post()


class UpdatesSocket(WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        WS_CLIENTS.add(self)
        self.set_nodelay(True)
        logger.debug("[ws] client connected (total=%d)", len(WS_CLIENTS))
        try:
            self.write_message(
                json.dumps(
                    {
                        "type": "hello",
                        "ts": datetime.now(timezone.utc).isoformat(),
                        "symbols": SUPPORTED_SYMBOLS,
                    }
                )
            )
        except Exception:
            logger.debug("[ws] hello send failed")

    def on_message(self, message):
        # Clients may send lightweight pings or acknowledgements; log at debug level only.
        logger.debug("[ws] received message: %s", message)

    def on_close(self):
        WS_CLIENTS.discard(self)
        logger.debug("[ws] client disconnected (total=%d)", len(WS_CLIENTS))


GLOBAL_POOL = None


async def make_app():
    pool = await create_pool()
    await init_schema(pool)
    global GLOBAL_POOL
    GLOBAL_POOL = pool

    settings = dict(
        debug=True,
        template_path=os.path.join(os.path.dirname(__file__), "..", "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "..", "static"),
        pool=pool,
    )
    return tornado.web.Application(
        [
            (r"/", MainHandler),
            (r"/api/fetch", FetchHandler, dict(pool=pool)),
            (r"/api/fetch_bulk", BulkFetchHandler, dict(pool=pool)),
            (r"/api/data", DataHandler, dict(pool=pool)),
            (r"/api/strategy/run", StrategyHandler, dict(pool=pool)),
            (r"/api/trade", TradeHandler),
            (r"/api/close", CloseHandler),
            (r"/api/positions", PositionsHandler),
            (r"/api/tick", TickHandler),
            (r"/api/stl", STLHandler, dict(pool=pool)),
            (r"/api/stl/run/([0-9]+)", STLDeleteHandler, dict(pool=pool)),
            (r"/api/stl/compute", STLComputeHandler, dict(pool=pool)),
            (r"/api/news", NewsHandler),
            (r"/api/news/analyze", NewsAnalysisHandler, dict(ai_client=AI_CLIENT, questions=NEWS_MICRO_QUESTIONS)),
            (r"/api/preferences", PreferencesHandler, dict(pool=pool)),
            (r"/api/config", ConfigHandler),
            (r"/ws/updates", UpdatesSocket),
        ],
        **settings,
    )


class StrategyHandler(tornado.web.RequestHandler):
    def initialize(self, pool):
        self.pool = pool

    async def get(self):
        symbol = self.get_argument("symbol", default=default_symbol())
        timeframe = self.get_argument("tf", default="H1").upper()
        fast = int(self.get_argument("fast", default="20"))
        slow = int(self.get_argument("slow", default="50"))
        limit = max(slow + 5, 200)
        logger.info("/api/strategy/run symbol=%s tf=%s fast=%s slow=%s", symbol, timeframe, fast, slow)
        rows = await fetch_ohlc_bars(self.pool, symbol, timeframe, limit)
        closes = [r["close"] for r in rows if r.get("close") is not None]
        sig = crossover_strategy(closes, fast=fast, slow=slow)

        # Optional trading
        enabled = (os.getenv("TRADING_ENABLED", "0").lower() in ("1", "true", "yes"))
        volume = float(os.getenv("TRADING_VOLUME", "0.1"))
        trade_result = None
        if enabled and sig["signal"] in ("buy", "sell"):
            # Very conservative: close existing positions first
            try:
                mt5_client.close_all_for(symbol)
                trade_result = mt5_client.place_market(symbol, sig["signal"], volume)
            except Exception as e:
                logger.exception("trade failed: %s", e)
                trade_result = {"ok": False, "error": str(e)}

        self.set_header("Content-Type", "application/json")
        self.finish(json.dumps({
            "symbol": symbol,
            "timeframe": timeframe,
            "fast": fast,
            "slow": slow,
            "signal": sig,
            "trade": trade_result,
            "trading_enabled": enabled,
        }))


class TradeHandler(tornado.web.RequestHandler):
    async def get(self):
        enabled = (os.getenv("TRADING_ENABLED", "0").lower() in ("1", "true", "yes"))
        if not enabled:
            self.set_status(403)
            self.set_header("Content-Type", "application/json")
            self.set_header("Cache-Control", "no-store")
            self.finish(json.dumps({"ok": False, "error": "trading_disabled (set TRADING_ENABLED=1)"}))
            return
        symbol = self.get_argument("symbol", default=default_symbol())
        side = self.get_argument("side", default="buy").lower()
        volume = float(self.get_argument("volume", default="0.1"))
        # Optional absolute SL/TP prices
        sl = self.get_argument("sl", default=None)
        tp = self.get_argument("tp", default=None)
        sl_val = float(sl) if sl not in (None, "", "null") else None
        tp_val = float(tp) if tp not in (None, "", "null") else None
        logger.info("/api/trade symbol=%s side=%s volume=%s", symbol, side, volume)
        try:
            res = mt5_client.place_market(symbol, side, volume, sl=sl_val, tp=tp_val)
        except Exception as e:
            logger.exception("trade failed: %s", e)
            self.set_status(500)
            self.set_header("Content-Type", "application/json")
            self.set_header("Cache-Control", "no-store")
            self.finish(json.dumps({"ok": False, "error": str(e)}))
            return
        logger.info("/api/trade result=%s", res)
        self.set_header("Content-Type", "application/json")
        self.set_header("Cache-Control", "no-store")
        # Include a quick snapshot of positions after trade
        try:
            positions = mt5_client.list_positions(symbol)
        except Exception:
            positions = []
        self.finish(json.dumps({"ok": res.get("ok", False), "result": res, "positions": positions}))

    async def post(self):
        # Allow POST to avoid any client/proxy caching issues with GET
        return await self.get()


class CloseHandler(tornado.web.RequestHandler):
    async def get(self):
        enabled = (os.getenv("TRADING_ENABLED", "0").lower() in ("1", "true", "yes"))
        if not enabled:
            self.set_status(403)
            self.set_header("Content-Type", "application/json")
            self.set_header("Cache-Control", "no-store")
            self.finish(json.dumps({"ok": False, "error": "trading_disabled (set TRADING_ENABLED=1)"}))
            return
        symbol = self.get_argument("symbol", default=default_symbol())
        logger.info("/api/close symbol=%s", symbol)
        try:
            res = mt5_client.close_all_for(symbol)
        except Exception as e:
            logger.exception("close positions failed: %s", e)
            self.set_status(500)
            self.set_header("Content-Type", "application/json")
            self.set_header("Cache-Control", "no-store")
            self.finish(json.dumps({"ok": False, "error": str(e)}))
            return
        self.set_header("Content-Type", "application/json")
        self.set_header("Cache-Control", "no-store")
        self.finish(json.dumps({"ok": True, "closed": res}))

    async def post(self):
        return await self.get()


class PositionsHandler(tornado.web.RequestHandler):
    async def get(self):
        symbol = self.get_argument("symbol", default=default_symbol())
        logger.debug("/api/positions symbol=%s", symbol)
        try:
            positions = mt5_client.list_positions(symbol)
        except Exception as e:
            logger.exception("list positions failed: %s", e)
            self.set_status(500)
            self.set_header("Content-Type", "application/json")
            self.set_header("Cache-Control", "no-store")
            self.finish(json.dumps({"ok": False, "error": str(e)}))
            return
        self.set_header("Content-Type", "application/json")
        self.set_header("Cache-Control", "no-store")
        self.finish(json.dumps({"ok": True, "positions": positions}))


class TickHandler(tornado.web.RequestHandler):
    async def get(self):
        symbol = self.get_argument("symbol", default=default_symbol())
        try:
            t = mt5_client.get_tick(symbol)
        except Exception as e:
            self.set_status(500)
            self.set_header("Content-Type", "application/json")
            self.finish(json.dumps({"ok": False, "error": str(e)}))
            return
        self.set_header("Content-Type", "application/json")
        self.set_header("Cache-Control", "no-store")
        self.finish(json.dumps({"ok": True, "tick": t}))


class STLHandler(tornado.web.RequestHandler):
    def initialize(self, pool):
        self.pool = pool

    async def get(self):
        symbol = self.get_argument("symbol", default=default_symbol()).upper()
        timeframe = self.get_argument("tf", default="H1").upper()
        run_id_arg = self.get_argument("run_id", default=None)
        start_arg = self.get_argument("start", default=None)
        end_arg = self.get_argument("end", default=None)
        all_data_flag = self.get_argument("all_data", "1").lower() not in ("0", "false", "no", "off")
        include_runs = self.get_argument("include_runs", "1").lower() not in ("0", "false", "no", "off")
        include_data = self.get_argument("include_data", "1").lower() not in ("0", "false", "no", "off")
        limit_arg = self.get_argument("limit", default=None)
        limit = int(limit_arg) if limit_arg else None

        run_id = None
        if run_id_arg:
            try:
                run_id = int(run_id_arg)
            except ValueError:
                run_id = None

        start_dt = _normalize_dt(start_arg) if start_arg else None
        end_dt = _normalize_dt(end_arg) if end_arg else None

        dataset_range = await ohlc_range(self.pool, symbol, timeframe)
        if not dataset_range:
            self.set_header("Content-Type", "application/json")
            self.set_header("Cache-Control", "no-store")
            self.finish(
                json.dumps(
                    {
                        "ok": True,
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "runs": [],
                        "rows": [],
                        "selected_run_id": None,
                        "needs_compute": False,
                        "dataset": None,
                        "target_range": None,
                        "reason": "no_data",
                    }
                )
            )
            return

        target_start = start_dt if (not all_data_flag and start_dt) else dataset_range["start_ts"]
        target_end = end_dt if (not all_data_flag and end_dt) else dataset_range["end_ts"]
        if target_start and target_start < dataset_range["start_ts"]:
            target_start = dataset_range["start_ts"]
        if target_end and target_end > dataset_range["end_ts"]:
            target_end = dataset_range["end_ts"]

        runs = await list_stl_runs(self.pool, symbol, timeframe) if include_runs else []
        selected_run = None

        if run_id is not None:
            selected_run = await get_stl_run(self.pool, run_id)
            if selected_run and (
                selected_run["symbol"].upper() != symbol
                or selected_run["timeframe"].upper() != timeframe
            ):
                selected_run = None
        if not selected_run and runs:
            for run in runs:
                if run["start_ts"] <= target_start and run["end_ts"] >= target_end:
                    selected_run = run
                    break
            if not selected_run:
                selected_run = runs[0]
        if selected_run and include_runs and all(run["id"] != selected_run["id"] for run in runs):
            runs = [selected_run, *runs]

        needs_compute = False
        reason = None
        if target_start and target_end:
            if selected_run is None:
                needs_compute = True
                reason = "missing_run"
            else:
                start_ok = selected_run["start_ts"] <= target_start
                end_ok = selected_run["end_ts"] >= target_end
                if not all_data_flag:
                    start_ok = abs((selected_run["start_ts"] - target_start).total_seconds()) < 1
                    end_ok = abs((selected_run["end_ts"] - target_end).total_seconds()) < 1
                if not (start_ok and end_ok):
                    needs_compute = True
                    reason = "range_mismatch"
                elif all_data_flag:
                    dataset_start = dataset_range["start_ts"]
                    dataset_end = dataset_range["end_ts"]
                    if (
                        selected_run["start_ts"] > dataset_start
                        or selected_run["end_ts"] < dataset_end
                        or selected_run["rows_count"] < dataset_range["rows_count"]
                    ):
                        needs_compute = True
                        reason = "dataset_extended"

        rows = []
        selected_run_serialized = None
        if selected_run and include_data:
            run_data = await fetch_stl_run_data(self.pool, selected_run["id"])
            if run_data:
                rows = run_data["rows"]
                if limit and limit > 0:
                    rows = rows[-limit:]
                selected_run = run_data["run"]
        selected_run_serialized = _serialize_run(selected_run)

        response_runs = [_serialize_run(run) for run in runs] if include_runs else []
        dataset_payload = {
            "start_ts": _dt_to_iso(dataset_range["start_ts"]),
            "end_ts": _dt_to_iso(dataset_range["end_ts"]),
            "rows_count": dataset_range["rows_count"],
        }
        target_payload = {
            "start_ts": _dt_to_iso(target_start),
            "end_ts": _dt_to_iso(target_end),
            "all_data": all_data_flag,
        }

        self.set_header("Content-Type", "application/json")
        self.set_header("Cache-Control", "no-store")
        self.finish(
            json.dumps(
                {
                    "ok": True,
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "runs": response_runs,
                    "rows": rows,
                    "selected_run_id": selected_run_serialized["id"] if selected_run_serialized else None,
                    "selected_run": selected_run_serialized,
                    "dataset": dataset_payload,
                    "target_range": target_payload,
                    "needs_compute": needs_compute,
                    "reason": reason,
                }
            )
        )


class STLComputeHandler(tornado.web.RequestHandler):
    def initialize(self, pool):
        self.pool = pool

    async def post(self):
        payload: dict[str, object] = {}
        if self.request.body:
            ctype = self.request.headers.get("Content-Type", "")
            if "json" in ctype:
                try:
                    payload = json.loads(self.request.body.decode() or "{}")
                except Exception:
                    payload = {}
        for key, values in self.request.arguments.items():
            if not values:
                continue
            payload[key] = values[0].decode() if isinstance(values[0], (bytes, bytearray)) else values[0]

        symbol = str(payload.get("symbol") or default_symbol()).upper()
        timeframe = str(payload.get("timeframe") or payload.get("tf") or "H1").upper()
        scope = str(payload.get("scope") or "current")
        limit = int(payload.get("limit") or 1500)

        period_override = payload.get("period")
        try:
            period_override = int(period_override) if period_override is not None else None
        except (TypeError, ValueError):
            period_override = None

        all_data_flag = str(payload.get("all_data", "1")).lower() not in ("0", "false", "no", "off")
        start_dt = None if all_data_flag else _normalize_dt(payload.get("start") or payload.get("start_ts"))
        end_dt = None if all_data_flag else _normalize_dt(payload.get("end") or payload.get("end_ts"))

        timeframes = payload.get("timeframes")
        if isinstance(timeframes, str):
            timeframes = [tf.strip().upper() for tf in timeframes.split(",") if tf.strip()]
        elif isinstance(timeframes, list):
            timeframes = [str(tf).strip().upper() for tf in timeframes if str(tf).strip()]
        else:
            timeframes = None

        symbols_param = payload.get("symbols")
        if isinstance(symbols_param, str):
            symbols_list = [s.strip().upper() for s in symbols_param.split(",") if s.strip()]
        elif isinstance(symbols_param, list):
            symbols_list = [str(s).strip().upper() for s in symbols_param if str(s).strip()]
        else:
            symbols_list = None

        tasks: list[tuple[str, str]] = []
        if scope in ("current", "single"):
            tasks = [(symbol, timeframe)]
        elif scope == "symbol_all_tf":
            tfs = timeframes or ALL_TIMEFRAMES
            tasks = [(symbol, tf) for tf in tfs]
        elif scope in ("timeframe_all_symbols", "tf_all_symbols"):
            syms = symbols_list or SUPPORTED_SYMBOLS
            tasks = [(sym, timeframe) for sym in syms]
        elif scope in ("all", "all_symbols"):
            syms = symbols_list or SUPPORTED_SYMBOLS
            tfs = timeframes or ALL_TIMEFRAMES
            tasks = [(sym, tf) for sym in syms for tf in tfs]
        else:
            self.set_status(400)
            self.set_header("Content-Type", "application/json")
            self.finish(json.dumps({"ok": False, "error": f"unknown scope {scope}"}))
            return

        if not tasks:
            self.set_status(400)
            self.set_header("Content-Type", "application/json")
            self.finish(json.dumps({"ok": False, "error": "no tasks scheduled"}))
            return

        loop = tornado.ioloop.IOLoop.current()

        async def runner():
            logger.info("[stl] starting %d jobs scope=%s period=%s", len(tasks), scope, period_override)
            for sym, tf in tasks:
                event_start = _dt_to_iso(start_dt) if scope in ("current", "single") else None
                event_end = _dt_to_iso(end_dt) if scope in ("current", "single") else None
                await emit_stl_event(
                    symbol=sym,
                    timeframe=tf,
                    period=period_override,
                    status="scheduled",
                    scope=scope,
                    background=True,
                    start_ts=event_start,
                    end_ts=event_end,
                )
                try:
                    result = await _compute_and_store_stl(
                        self.pool,
                        sym,
                        tf,
                        period=period_override,
                        start_dt=start_dt if scope in ("current", "single") else None,
                        end_dt=end_dt if scope in ("current", "single") else None,
                    )
                    logger.info(
                        "[stl] %s %s completed period=%s points=%s inserted=%s",
                        sym,
                        tf,
                        result.get("period"),
                        result.get("points"),
                        result.get("inserted"),
                    )
                    await emit_stl_event(
                        symbol=sym,
                        timeframe=tf,
                        period=result.get("period"),
                        status="completed",
                        scope=scope,
                        background=True,
                        points=result.get("points"),
                        note=f"inserted={result.get('inserted')}",
                        run_id=result.get("run_id"),
                        start_ts=result.get("start_ts"),
                        end_ts=result.get("end_ts"),
                        created_at=result.get("created_at"),
                    )
                except Exception as exc:
                    logger.warning("[stl] %s %s failed: %s", sym, tf, exc)
                    await emit_stl_event(
                        symbol=sym,
                        timeframe=tf,
                        period=period_override,
                        status="error",
                        scope=scope,
                        background=True,
                        start_ts=event_start,
                        end_ts=event_end,
                        error=str(exc),
                    )
                await asyncio.sleep(0.05)

        loop.spawn_callback(runner)

        self.set_header("Content-Type", "application/json")
        self.set_header("Cache-Control", "no-store")
        self.finish(
            json.dumps(
                {
                    "ok": True,
                    "scheduled": len(tasks),
                    "scope": scope,
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "period": period_override,
                }
            )
        )


class STLDeleteHandler(tornado.web.RequestHandler):
    def initialize(self, pool):
        self.pool = pool

    async def delete(self, run_id: str):
        try:
            run_id_int = int(run_id)
        except (TypeError, ValueError):
            self.set_status(400)
            self.finish(json.dumps({"ok": False, "error": "invalid run id"}))
            return
        deleted = await delete_stl_run(self.pool, run_id_int)
        if deleted == 0:
            self.set_status(404)
            self.finish(json.dumps({"ok": False, "error": "run not found"}))
            return
        self.set_header("Content-Type", "application/json")
        self.set_header("Cache-Control", "no-store")
        self.finish(json.dumps({"ok": True, "run_id": run_id_int}))


class PreferencesHandler(tornado.web.RequestHandler):
    def initialize(self, pool):
        self.pool = pool

    async def get(self):
        keys_arg = self.get_argument("keys", default=None)
        if keys_arg:
            keys = [k.strip() for k in keys_arg.split(',') if k.strip()]
        else:
            keys = PREF_KEYS
        prefs = await get_prefs(self.pool, keys)
        self.set_header("Content-Type", "application/json")
        self.set_header("Cache-Control", "no-store")
        self.finish(json.dumps({"ok": True, "prefs": prefs}))

    async def post(self):
        raw = self.request.body or b"{}"
        try:
            payload = json.loads(raw.decode("utf-8"))
        except Exception:
            self.set_status(400)
            self.set_header("Content-Type", "application/json")
            self.finish(json.dumps({"ok": False, "error": "invalid JSON"}))
            return
        updates = {}
        if isinstance(payload, dict):
            for key, value in payload.items():
                if key in PREF_KEYS and value is not None:
                    updates[key] = str(value)
        if updates:
            await set_prefs(self.pool, updates)
        self.set_header("Content-Type", "application/json")
        self.set_header("Cache-Control", "no-store")
        self.finish(json.dumps({"ok": True, "updated": sorted(updates.keys())}))


class ConfigHandler(tornado.web.RequestHandler):
    async def get(self):
        enabled = (os.getenv("TRADING_ENABLED", "0").lower() in ("1", "true", "yes"))
        self.set_header("Content-Type", "application/json")
        self.set_header("Cache-Control", "no-store")
        self.finish(
            json.dumps(
                {
                    "ok": True,
                    "trading_enabled": enabled,
                    "symbols": SUPPORTED_SYMBOLS,
                    "default_symbol": default_symbol(),
                }
            )
        )


class NewsHandler(tornado.web.RequestHandler):
    async def get(self):
        symbol = self.get_argument("symbol", default=default_symbol())
        loop = tornado.ioloop.IOLoop.current()
        try:
            digest = await loop.run_in_executor(EXECUTOR, lambda: fetch_symbol_digest(symbol, limit=25))
            self.set_header("Content-Type", "application/json")
            self.set_header("Cache-Control", "no-store")
            self.finish(
                json.dumps(
                    {
                        "ok": True,
                        "symbol": symbol,
                        "news": digest.get("news", []),
                        "snapshot": digest.get("snapshot", {}),
                    }
                )
            )
        except Exception as e:
            self.set_status(500)
            self.set_header("Content-Type", "application/json")
            self.set_header("Cache-Control", "no-store")
            self.finish(json.dumps({"ok": False, "error": str(e), "news": [], "snapshot": {}}))


class NewsAnalysisHandler(tornado.web.RequestHandler):
    def initialize(self, ai_client, questions: list[dict[str, str]]):
        self.ai_client = ai_client
        self.questions = questions

    async def post(self):
        if not self.ai_client:
            self.set_status(503)
            self.set_header("Content-Type", "application/json")
            self.finish(json.dumps({"ok": False, "error": "LLM analysis unavailable"}))
            return
        try:
            payload = json.loads(self.request.body or "{}")
        except json.JSONDecodeError:
            self.set_status(400)
            self.set_header("Content-Type", "application/json")
            self.finish(json.dumps({"ok": False, "error": "Invalid JSON body"}))
            return

        article_id, article_text = _compose_article_payload(payload)
        if not article_text:
            self.set_status(400)
            self.set_header("Content-Type", "application/json")
            self.finish(json.dumps({"ok": False, "error": "Article text required"}))
            return

        loop = tornado.ioloop.IOLoop.current()
        try:
            raw = await loop.run_in_executor(
                EXECUTOR, lambda: _run_news_analysis(self.ai_client, article_text)
            )
        except Exception as exc:  # pragma: no cover - network/LLM failure
            logger.warning("news analysis failed: %s", exc)
            self.set_status(502)
            self.set_header("Content-Type", "application/json")
            self.finish(json.dumps({"ok": False, "error": "AI analysis failed"}))
            return

        answers_raw = raw.get("answers", []) if isinstance(raw, dict) else []
        answer_map = {}
        for item in answers_raw:
            if not isinstance(item, dict):
                continue
            qid = str(item.get("id", "")).strip()
            ans = str(item.get("answer", "")).strip().lower()
            if qid in _NEWS_QUESTION_IDS and ans in {"yes", "no"}:
                answer_map[qid] = ans

        structured = []
        for q in self.questions:
            qid = q["id"]
            ans = answer_map.get(qid, "no")
            structured.append(
                {
                    "id": qid,
                    "label": q["label"],
                    "question": q["question"],
                    "answer": ans,
                }
            )

        self.set_header("Content-Type", "application/json")
        self.set_header("Cache-Control", "no-store")
        self.finish(json.dumps({"ok": True, "article_id": article_id, "answers": structured}))


def main():
    # Load .env automatically if present (handy on Windows)
    # Allow .env to override any previously-set variables in this process
    load_dotenv(override=True)
    symbols = refresh_supported_symbols()
    # Configure logging
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    logger.info("Supported symbols: %s", ", ".join(symbols))
    global AI_CLIENT
    if MixedAIRequestJSONBase is not None:
        cache_root = Path(__file__).resolve().parents[1] / "cache"
        try:
            AI_CLIENT = MixedAIRequestJSONBase(use_cache=True, max_retries=2, cache_dir=str(cache_root))
            providers = ", ".join(AI_CLIENT.providers)
            logger.info("News AI providers initialized: %s", providers)
        except Exception as exc:  # pragma: no cover - optional dependency failure
            AI_CLIENT = None
            logger.warning("News AI client initialization failed: %s", exc)
    else:
        logger.info("MixedAIRequestJSONBase not available; news analysis endpoint disabled.")
    port = int(os.getenv("PORT", "8888"))
    loop = tornado.ioloop.IOLoop.current()

    async def start():
        app = await make_app()
        app.listen(port)
        mt5_path = os.getenv("MT5_PATH")
        logger.info("Tornado running on http://localhost:%s", port)
        logger.info("MT5_PATH=%r", mt5_path)

    loop.run_sync(start)

    # Optional periodic auto-fetch
    auto = (os.getenv("AUTO_FETCH", "0").lower() in ("1", "true", "yes"))
    if auto:
        sym = os.getenv("AUTO_FETCH_SYMBOL", "XAUUSD")
        tf = os.getenv("AUTO_FETCH_TF", "H1").upper()
        cnt = int(os.getenv("AUTO_FETCH_COUNT", "500"))
        interval_ms = int(float(os.getenv("AUTO_FETCH_SEC", "60")) * 1000)

        async def do_fetch():
            loop = tornado.ioloop.IOLoop.current()
            fetch_fn = partial(mt5_client.fetch_bars, sym, tf, cnt)
            try:
                bars = await loop.run_in_executor(EXECUTOR, fetch_fn)
                if GLOBAL_POOL is not None:
                    await upsert_ohlc_bars(GLOBAL_POOL, bars)
            except Exception as e:
                logger.exception("auto-fetch error: %s", e)

        # Store pool on app for use above
        def attach_pool_to_app(fut):
            pass

        # Hack: create a small wrapper to capture pool from handlers
        # Instead, stash via closure when creating application
        # Simpler approach: re-create pool each call is overkill; so stash here
        # We'll set it after app construction in 'start' but we don't keep a handle.
        # Workaround: place pool in settings during make_app (already attached when created)

        def _schedule_fetch():
            # Schedule the async fetch without blocking the running IOLoop
            tornado.ioloop.IOLoop.current().add_callback(do_fetch)

        cb = tornado.ioloop.PeriodicCallback(_schedule_fetch, interval_ms)
        cb.start()

    loop.start()


if __name__ == "__main__":
    main()








