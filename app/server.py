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
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.log import access_log
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
    insert_health_run,
    list_health_runs,
    upsert_news_articles,
    fetch_news_db,
    upsert_account_balance,
    fetch_account_balances,
    upsert_closed_deals,
    fetch_closed_deals_between,
    latest_balance_before,
    insert_signal_trade,
    list_signal_trades,
)
from app.mt5_client import client as mt5_client
from app.strategy import crossover_strategy
from app.news_fetcher import fetch_symbol_digest
from app.news_fetcher import fetch_fmp_snapshot
from app.news_fetcher import fetch_fmp_forex_latest
from app.news_fetcher import fetch_news_for_symbol

try:
    from llm_model.echomind.mixed_ai_request import MixedAIRequestJSONBase  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    MixedAIRequestJSONBase = None  # type: ignore


EXECUTOR = ThreadPoolExecutor(max_workers=2)
logger = logging.getLogger("mt5app")

WS_CLIENTS: set = set()
NEWS_BACKFILL_CB = None
BALANCE_CB = None
CLOSED_ORDERS_CB = None


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


# --- Health-check helpers (LLM per-question boolean answers) ---

def _load_strategy_json(filename: str) -> dict[str, Any]:
    root = Path(__file__).resolve().parents[1]
    path = root / "strategies" / "llm" / filename
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("failed to load strategy json %s: %s", filename, exc)
        return {}


HEALTH_BOOL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "answer": {"type": "boolean"},
        "explanation": {"type": "string"},
    },
    "required": ["answer", "explanation"],
    "additionalProperties": False,
}

# Trade plan output schema for AI Buy/Sell planning
TRADE_PLAN_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "position": {"type": "string", "enum": ["BUY", "SELL"]},
        "stop_loss": {"type": "number"},
        "take_profit": {"type": "number"},
        "explanation": {"type": "string"},
    },
    "required": ["position", "stop_loss", "take_profit", "explanation"],
    "additionalProperties": False,
}


def _articles_to_text(items: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for i, it in enumerate(items, 1):
        title = str(it.get("title") or it.get("headline") or "").strip()
        # Prefer full body when available (FMP 'text' is passed as 'body')
        summary = str(
            it.get("body")
            or it.get("summary")
            or it.get("description")
            or it.get("text")
            or ""
        ).strip()
        url = str(it.get("url") or "")
        blk = []
        if title:
            blk.append(f"Title: {title}")
        if summary and summary.lower() != title.lower():
            blk.append(f"Body: {summary}")
        if url:
            blk.append(f"URL: {url}")
        if blk:
            parts.append(f"[{i}]\n" + "\n".join(blk))
    return "\n\n".join(parts)


DEFAULT_STRATEGIES: dict[str, str] = {
    "forex_pair": "forex_pair_compact_10q_position.json",
    "stock": "stocks_compact_10q_position.json",
}

ALLOWED_STRATEGIES: dict[str, set[str]] = {
    "forex_pair": {
        # Compact 10Q + Position (default) and plain 10Q
        "forex_pair_compact_10q_position.json",
        "forex_pair_compact_10q.json",
        # Metals variants used for XAU/XAG within forex_pair kind
        "metal_pair_compact_10q_position.json",
        "metal_pair_compact_10q.json",
        # Tech snapshot remains available for Tech+AI flows
        "tech_snapshot_10q.json",
    },
    "stock": {
        # Compact 10Q + Position (default) and plain 10Q
        "stocks_compact_10q_position.json",
        "stocks_compact_10q.json",
        # Tech snapshot remains available for Tech+AI flows
        "tech_snapshot_10q.json",
    },
}


def _strategy_answer_type(strategy: dict[str, Any]) -> str:
    options = strategy.get("answer_options") or []
    if not options:
        return "bool"
    normalized = {str(opt).strip().upper() for opt in options}
    if normalized.issubset({"YES", "NO"}):
        return "bool"
    if normalized.issubset({"BULLISH", "BEARISH"}):
        return "choice"
    lowered = [str(opt).lower() for opt in options]
    if any("${base_currency" in opt or "${quote_currency" in opt for opt in lowered):
        return "choice"
    return "unknown"


def _substitute_currency_tokens(text: str, base_ccy: str, quote_ccy: str) -> str:
    if not text:
        return ""
    replacements = {
        "${base_currency}": base_ccy,
        "${BASE_CURRENCY}": base_ccy,
        "${quote_currency}": quote_ccy,
        "${QUOTE_CURRENCY}": quote_ccy,
        "${BASE}": base_ccy,
        "${QUOTE}": quote_ccy,
    }
    for token, value in replacements.items():
        text = text.replace(token, value)
    return text


def _make_choice_schema(options: list[str]) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "answer": {"type": "string", "enum": options},
            "explanation": {"type": "string"},
        },
        "required": ["answer", "explanation"],
        "additionalProperties": False,
    }


def _build_tech_prompt(question_text: str, symbol: str, timeframe: str | None, snapshot: str, options: list[str]) -> str:
    tf_line = f"Timeframe: {timeframe}" if timeframe else ""
    allowed = ", ".join(options)
    return (
        "You are a technical analyst. Answer strictly with JSON that matches the schema: {answer:string, explanation:string}. "
        f"Choose exactly one from: {allowed}. Be decisive and cite the strongest evidence from the snapshot.\\n\\n"
        f"Symbol: {symbol}\\n{tf_line}\\n\\n"
        f"Snapshot (recent technical readings):\\n---\\n{snapshot}\\n---\\n\\n"
        f"Question: {question_text}\\n"
    )


def _is_fx_symbol(sym: str | None) -> bool:
    if not sym:
        return False
    s = str(sym).upper().strip()
    if len(s) in (6, 7) and s[:3].isalpha() and s[3:6].isalpha():
        return True
    return s.startswith(("XAU", "XAG", "XPT", "XPD"))


def _build_pair_position_prompt(pair_symbol: str, items: list[dict], timeframe: str | None) -> str:
    blk = _articles_to_text(items)
    tf_line = f"Timeframe: {timeframe}" if timeframe else ""
    return (
        "You are an FX analyst. Return only valid JSON that matches the schema.\n\n"
        "Schema: {position: 'BUY'|'SELL', sl: number, tp: number, explanation: string}.\n"
        "Use uppercase BUY/SELL for 'position'. Explanation cites strongest evidence.\n\n"
        f"Pair: {pair_symbol}\n{tf_line}\n\n"
        f"Articles:\n---\n{blk}\n---\n\n"
        "Task: Based on the evidence above, provide the trade orientation JSON."
    )

def _build_pair_prompt_position_question(question_text: str, pair_symbol: str, items: list[dict], timeframe: str | None) -> str:
    blk = _articles_to_text(items)
    tf_line = f"Timeframe: {timeframe}" if timeframe else ""
    return (
        "You are an FX analyst. Return only valid JSON that matches the schema.\n\n"
        "Schema: {position: 'BUY'|'SELL', sl: number, tp: number, explanation: string}.\n"
        "Use uppercase BUY/SELL for 'position'. Explanation cites strongest evidence.\n\n"
        f"Pair: {pair_symbol}\n{tf_line}\n\n"
        f"Articles:\n---\n{blk}\n---\n\n"
        f"Question: {question_text}\n"
    )


def _build_stock_position_prompt(ticker: str, items: list[dict], timeframe: str | None) -> str:
    blk = _articles_to_text(items)
    tf_line = f"Timeframe: {timeframe}" if timeframe else ""
    return (
        "You are a precise equity analyst. Return only valid JSON that matches the schema.\n\n"
        "Schema: {position: 'BUY'|'SELL', sl: number, tp: number, explanation: string}.\n"
        "Use uppercase BUY/SELL for 'position'. Explanation cites strongest evidence.\n\n"
        f"Ticker: {ticker}\n{tf_line}\n\n"
        f"Articles:\n---\n{blk}\n---\n\n"
        "Task: Based on the evidence above, provide the trade orientation JSON."
    )

def _build_stock_prompt_position_question(question_text: str, ticker: str, items: list[dict], timeframe: str | None) -> str:
    blk = _articles_to_text(items)
    tf_line = f"Timeframe: {timeframe}" if timeframe else ""
    return (
        "You are a precise equity analyst. Return only valid JSON that matches the schema.\n\n"
        "Schema: {position: 'BUY'|'SELL', sl: number, tp: number, explanation: string}.\n"
        "Use uppercase BUY/SELL for 'position'. Explanation cites strongest evidence.\n\n"
        f"Ticker: {ticker}\n{tf_line}\n\n"
        f"Articles:\n---\n{blk}\n---\n\n"
        f"Question: {question_text}\n"
    )

def _build_pair_prompt_one_combined(question_text: str, pair_symbol: str, items: list[dict], timeframe: str | None) -> str:
    blk = _articles_to_text(items)
    tf_line = f"Timeframe: {timeframe}" if timeframe else ""
    return (
        "You are an FX analyst. Answer strictly with JSON that matches the schema: {answer:boolean, explanation:string}. "
        "Be decisive: choose YES (true) or NO (false). Provide a brief one-sentence explanation citing the most relevant evidence.\n\n"
        f"Pair: {pair_symbol}\n{tf_line}\n\n"
        f"Articles:\n---\n{blk}\n---\n\n"
        f"Question: {question_text}\n"
    )


def _build_pair_prompt_choice_combined(
    question_text: str,
    pair_symbol: str,
    items: list[dict[str, Any]],
    timeframe: str | None,
    options: list[str],
) -> str:
    blk = _articles_to_text(items)
    allowed = ", ".join(options)
    tf_line = f"Timeframe: {timeframe}" if timeframe else ""
    return (
        "You are an FX analyst. Answer strictly with JSON that matches the schema: {answer:string, explanation:string}. "
        f"Choose exactly one from: {allowed}. Be decisive and cite the strongest evidence.\n\n"
        f"Pair: {pair_symbol}\n{tf_line}\n\n"
        f"Articles:\n---\n{blk}\n---\n\n"
        f"Question: {question_text}\n"
    )


async def run_news_backfill(days: int = 7) -> dict:
    if GLOBAL_POOL is None:
        return {"ok": False, "error": "no_pool"}
    now = datetime.now(timezone.utc)
    since = (now - timedelta(days=max(1, days))).date().isoformat()
    to = now.date().isoformat()
    total = 0
    stored = 0
    page = 0
    updated_symbols: dict[str, int] = {}
    logger.info("[news] backfill start days=%d since=%s to=%s", days, since, to)
    while page < 5:
        try:
            items = await tornado.ioloop.IOLoop.current().run_in_executor(
                EXECUTOR, lambda: fetch_fmp_forex_latest(since=since, to=to, page=page, limit=200)
            )
        except Exception:
            items = []
        if not items:
            break
        total += len(items)
        symbol_counts: dict[str, int] = {}
        for it in items:
            sym = (it.get("symbol") or "").upper()
            if sym:
                symbol_counts[sym] = symbol_counts.get(sym, 0) + 1
        try:
            inserted = await upsert_news_articles(GLOBAL_POOL, items)
            stored += inserted
            logger.info("[news] forex-latest page=%d fetched=%d inserted=%d", page, len(items), inserted)
            if inserted > 0:
                for sym, cnt in symbol_counts.items():
                    updated_symbols[sym] = updated_symbols.get(sym, 0) + cnt
        except Exception:
            logger.exception("[news] forex-latest upsert failed (page=%d)", page)
        page += 1
        await asyncio.sleep(0.05)
    from app.news_fetcher import fetch_fmp_news as _fetch_fmp_news
    for sym in SUPPORTED_SYMBOLS:
        if _is_fx_symbol(sym):
            continue
        try:
            items = await tornado.ioloop.IOLoop.current().run_in_executor(
                EXECUTOR, lambda: _fetch_fmp_news(sym, limit=50)
            )
        except Exception:
            items = []
        filt = []
        for it in items:
            pub = it.get("published") or it.get("publishedAt") or it.get("publishedDate") or ""
            try:
                dt = datetime.fromisoformat(str(pub))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
            except Exception:
                dt = None
            if dt is None or (now - dt).days > days:
                continue
            it["symbol"] = sym
            filt.append(it)
        if filt:
            try:
                inserted = await upsert_news_articles(GLOBAL_POOL, filt)
                stored += inserted
                logger.info("[news] equities %s fetched=%d within_%dd=%d inserted=%d", sym, len(items), days, len(filt), inserted)
                if inserted > 0:
                    key = sym.upper()
                    updated_symbols[key] = updated_symbols.get(key, 0) + len(filt)
            except Exception:
                logger.exception("[news] equities upsert failed for %s", sym)
        await asyncio.sleep(0.05)
    for sym, cnt in updated_symbols.items():
        await emit_news_event(
            symbol=sym,
            status="updated",
            scope="backfill",
            background=True,
            items=cnt,
            note=f"days={days}",
        )
    logger.info("[news] backfill complete fetched=%d inserted=%d days=%d symbols=%s", total, stored, days, sorted(updated_symbols))
    return {"ok": True, "fetched": total, "inserted": stored, "days": days, "symbols": sorted(updated_symbols)}


def _seconds_until_next_boundary_minutes(interval_min: int, *, use_utc: bool = True) -> float:
    """Seconds until the next wall-clock boundary for the given minute interval.

    Example: interval_min=30 → schedule at HH:00 and HH:30, aligned to real time
    rather than relative to when the app started.
    """
    if interval_min <= 0:
        interval_min = 30
    now = datetime.now(timezone.utc) if use_utc else datetime.now()
    rem = now.minute % interval_min
    add_min = (interval_min - rem) % interval_min
    # If we're exactly on a boundary (second==0), jump to the next boundary
    if add_min == 0:
        add_min = interval_min
    target = (now.replace(second=0, microsecond=0) + timedelta(minutes=add_min))
    delta = (target - now).total_seconds()
    if delta <= 0:
        delta = float(interval_min * 60)
    return float(delta)


def schedule_news_backfill_aligned(interval_min: int = 30):
    """Schedule news backfill aligned to wall clock (e.g., at :00 and :30)."""
    global NEWS_BACKFILL_CB
    loop = tornado.ioloop.IOLoop.current()

    async def _tick():
        try:
            await run_news_backfill()
        finally:
            # Schedule the next aligned run
            delay = _seconds_until_next_boundary_minutes(max(1, int(interval_min)))
            try:
                if NEWS_BACKFILL_CB is not None:
                    loop.remove_timeout(NEWS_BACKFILL_CB)
            except Exception:
                pass
            # Store the timeout handle so we can cancel later if needed
            globals()['NEWS_BACKFILL_CB'] = loop.call_later(delay, lambda: loop.add_callback(_tick))

    # Cancel any previously scheduled timeout
    try:
        if NEWS_BACKFILL_CB is not None:
            loop.remove_timeout(NEWS_BACKFILL_CB)
    except Exception:
        pass
    # Schedule initial run at the next boundary
    initial_delay = _seconds_until_next_boundary_minutes(max(1, int(interval_min)))
    NEWS_BACKFILL_CB = loop.call_later(initial_delay, lambda: loop.add_callback(_tick))


def _build_pair_prompt_one(question_text: str, base_ccy: str, quote_ccy: str, base_items: list[dict], quote_items: list[dict], timeframe: str | None) -> str:
    base_blk = _articles_to_text(base_items)
    quote_blk = _articles_to_text(quote_items)
    tf_line = f"Timeframe: {timeframe}" if timeframe else ""
    return (
        "You are an FX analyst. Answer strictly with JSON that matches the schema: {answer:boolean, explanation:string}. "
        "Be decisive: choose YES (true) or NO (false). Provide a brief one-sentence explanation citing the most relevant evidence.\n\n"
        f"Pair: {base_ccy}/{quote_ccy}\n{tf_line}\n\n"
        f"BASE ({base_ccy}) articles:\n---\n{base_blk}\n---\n\n"
        f"QUOTE ({quote_ccy}) articles:\n---\n{quote_blk}\n---\n\n"
        f"Question: {question_text}\n"
    )


def _build_pair_prompt_choice(
    question_text: str,
    base_ccy: str,
    quote_ccy: str,
    base_items: list[dict[str, Any]],
    quote_items: list[dict[str, Any]],
    timeframe: str | None,
    options: list[str],
) -> str:
    base_blk = _articles_to_text(base_items)
    quote_blk = _articles_to_text(quote_items)
    tf_line = f"Timeframe: {timeframe}" if timeframe else ""
    allowed = ", ".join(options)
    return (
        "You are an FX analyst. Answer strictly with JSON that matches the schema: {answer:string, explanation:string}. "
        f"Choose exactly one currency code from this list: {allowed}. Be decisive and cite the strongest evidence.\n\n"
        f"Pair: {base_ccy}/{quote_ccy}\n{tf_line}\n\n"
        f"{base_ccy} articles:\n---\n{base_blk}\n---\n\n"
        f"{quote_ccy} articles:\n---\n{quote_blk}\n---\n\n"
        f"Question: {question_text}\n"
    )


def _build_stock_prompt_one(question_text: str, ticker: str, items: list[dict], timeframe: str | None) -> str:
    blk = _articles_to_text(items)
    tf_line = f"Timeframe: {timeframe}" if timeframe else ""
    return (
        "You are an equity analyst. Answer strictly with JSON that matches the schema: {answer:boolean, explanation:string}. "
        "Be decisive: choose YES (true) or NO (false). Provide a brief one-sentence explanation citing the most relevant evidence.\n\n"
        f"Ticker: {ticker}\n{tf_line}\n\n"
        f"Articles:\n---\n{blk}\n---\n\n"
        f"Question: {question_text}\n"
    )

def _build_stock_prompt_choice(question_text: str, ticker: str, items: list[dict], timeframe: str | None, options: list[str]) -> str:
    blk = _articles_to_text(items)
    tf_line = f"Timeframe: {timeframe}" if timeframe else ""
    allowed = ", ".join(options)
    return (
        "You are an equity analyst. Answer strictly with JSON that matches the schema: {answer:string, explanation:string}. "
        f"Choose exactly one from: {allowed}. Be decisive and cite the strongest evidence.\n\n"
        f"Ticker: {ticker}\n{tf_line}\n\n"
        f"Articles:\n---\n{blk}\n---\n\n"
        f"Question: {question_text}\n"
    )


def _build_news_prompt(article_text: str) -> str:
    question_lines = []
    for idx, item in enumerate(NEWS_MICRO_QUESTIONS, start=1):
        question_lines.append(f"{idx}. {item['id']}: {item['question']}")
    questions_block = "\n".join(question_lines)
    return (
        "You are an analyst that only answers with JSON. "
        "Read the news article and answer each question with \"yes\" or \"no\". "
        "If the article does not provide enough evidence, answer \"no\".\n\n"
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


async def emit_news_event(
    *,
    symbol: str,
    status: str,
    scope: str | None = None,
    background: bool = False,
    items: int | None = None,
    note: str | None = None,
) -> None:
    event = {
        "type": "news_update",
        "ts": datetime.now(timezone.utc).isoformat(),
        "symbol": symbol.upper(),
        "status": status,
        "scope": scope,
        "background": background,
    }
    if items is not None:
        event["items"] = items
    if note:
        event["note"] = note
    await _broadcast_ws(event)


async def emit_balance_event(*, user: str, account_id: int, balance: float | None = None) -> None:
    event = {
        "type": "balance_update",
        "ts": datetime.now(timezone.utc).isoformat(),
        "user": user,
        "account": int(account_id),
    }
    if balance is not None:
        event["balance"] = float(balance)
    await _broadcast_ws(event)


async def emit_closed_deals_event() -> None:
    event = {
        "type": "closed_deals_update",
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    await _broadcast_ws(event)


ALL_TIMEFRAMES = ["M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1", "MN1", "Y1"]
PREF_KEYS = [
    "last_symbol",
    "last_tf",
    "last_count",
    "chart_type",
    "last_volume",
    "last_sl",
    "last_tp",
    "last_fast",
    "last_slow",
    "chart_shift",
    "trade_ai_model",
    "balance_poll_min",
    "closed_orders_poll_min",
]

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
    deferred: bool = False,
) -> dict[str, object]:
    """Unified fetch routine used by both the interactive handler and bulk/background jobs."""
    loop = tornado.ioloop.IOLoop.current()
    event_background = background or (mode == "full_async") or deferred
    base_info: dict[str, object] = {
        "ok": False,
        "symbol": symbol,
        "timeframe": timeframe,
        "mode": mode,
    }

    async def _run_fetch() -> dict[str, object]:
        info = dict(base_info)
        try:
            bars: list[dict] = []
            fetch_mode: str | None = None
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
                    except Exception as exc:  # pragma: no cover - fallback handled below
                        logger.warning(
                            "incremental fetch failed for %s %s: %s; retrying with full=%s",
                            symbol,
                            timeframe,
                            exc,
                            count,
                        )
                        fetch_mode = "full"
                        fetch_fn = partial(mt5_client.fetch_bars, symbol, timeframe, count)
                        bars = await loop.run_in_executor(EXECUTOR, fetch_fn)
                else:
                    fetch_mode = "full"
                    fetch_fn = partial(mt5_client.fetch_bars, symbol, timeframe, count)
                    bars = await loop.run_in_executor(EXECUTOR, fetch_fn)
            elif mode == "full_async":
                days = _default_backfill_days(timeframe)

                async def _bg() -> None:
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
                        await set_prefs(
                            pool,
                            {
                                "last_symbol": symbol.upper(),
                                "last_tf": timeframe,
                                "last_count": str(count),
                            },
                        )
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
                    await set_prefs(
                        pool,
                        {
                            "last_symbol": symbol.upper(),
                            "last_tf": timeframe,
                            "last_count": str(count),
                        },
                    )
                except Exception:  # pragma: no cover
                    logger.debug("failed to persist last selection")

            info.update(
                {
                    "ok": True,
                    "inserted": inserted,
                    "fetched": fetched,
                    "fetch_mode": fetch_mode,
                }
            )

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
                background=event_background,
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
                background=event_background,
                status="error",
                error=str(exc),
            )
            return info

    if deferred and mode != "full_async":
        async def _bg_job() -> None:
            await _run_fetch()

        loop.spawn_callback(_bg_job)
        scheduled_info = dict(base_info)
        scheduled_info.update(
            {
                "ok": True,
                "scheduled": True,
                "inserted": 0,
                "fetched": 0,
                "fetch_mode": mode if mode in {"inc", "full"} else None,
            }
        )
        if persist_selection:
            try:
                await set_prefs(
                    pool,
                    {
                        "last_symbol": symbol.upper(),
                        "last_tf": timeframe,
                        "last_count": str(count),
                    },
                )
            except Exception:  # pragma: no cover
                logger.debug("failed to persist last selection")
        await emit_fetch_event(
            symbol=symbol,
            timeframe=timeframe,
            mode=mode,
            fetch_mode=scheduled_info.get("fetch_mode"),
            inserted=0,
            fetched=0,
            scope=event_scope,
            background=True,
            status="scheduled",
            note="background fetch",
        )
        return scheduled_info

    return await _run_fetch()


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
        # Optional overrides: reset query flag, or pin defaults via env
        def _truthy(v: str | None) -> bool:
            if v is None:
                return False
            return str(v).strip().lower() in {"1", "true", "yes", "y", "on"}

        reset_flag = _truthy(self.get_argument("reset", default=None))
        # Optional: pin defaults to XAUUSD/H1 when enabled via env
        pin_defaults = _truthy(os.getenv("PIN_DEFAULTS_TO_XAU_H1", "0"))

        # Read last selection from prefs if available
        pool = self.settings.get("pool")
        last_sym = None
        last_tf = None
        extras = {}
        if pool is not None and not reset_flag and not pin_defaults:
            try:
                last_sym = await get_pref(pool, "last_symbol")
                last_tf = await get_pref(pool, "last_tf")
                extras = await get_prefs(pool, [
                    "last_count",
                    "chart_type",
                    "last_volume",
                    "last_sl",
                    "last_tp",
                    "last_fast",
                    "last_slow",
                    "stl_auto_period",
                    "stl_manual_period",
                    "chart_shift",
                ])
            except Exception:
                extras = {}
                logger.debug("no prefs yet for last_symbol/last_tf")

        # Determine initial symbol/timeframe
        if pin_defaults:
            sym = "XAUUSD"
            tf = "H1"
        else:
            sym = (last_sym or default_symbol()).upper()
            tf = (last_tf or "H1").upper()
        if sym not in SUPPORTED_SYMBOLS:
            sym = default_symbol()
        if tf not in ALL_TIMEFRAMES:
            tf = "H1"

        # If we are pinning defaults or using reset flag, persist the chosen defaults to DB
        if (pin_defaults or reset_flag) and pool is not None:
            try:
                await set_prefs(pool, {"last_symbol": sym, "last_tf": tf})
            except Exception:
                logger.debug("failed to persist pinned defaults")
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
        auto_news_pref = extras.get("auto_news_backfill") or "1"
        chart_shift_pref = extras.get("chart_shift") or "1"
        closed_orders_poll_pref = extras.get("closed_orders_poll_min") or os.getenv("CLOSED_ORDERS_POLL_MIN", "30")
        balance_poll_pref = extras.get("balance_poll_min") or os.getenv("BALANCE_POLL_MIN", "60")

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
            news_ai_available=bool(AI_CLIENT),
            default_stl_auto_period=stl_auto_pref,
            default_stl_manual_period=stl_manual_pref,
            default_chart_shift=chart_shift_pref,
            default_auto_news=auto_news_pref,
            default_balance_poll_min=balance_poll_pref,
            default_closed_orders_poll_min=closed_orders_poll_pref,
        )


class FetchHandler(tornado.web.RequestHandler):
    def initialize(self, pool):
        self.pool = pool

    async def get(self):
        symbol = self.get_argument("symbol", default=default_symbol())
        timeframe = self.get_argument("tf", default="H1").upper()
        count = int(self.get_argument("count", default="500"))
        mode = self.get_argument("mode", default="inc")  # inc | full_async | full
        background_param = self.get_argument("background", default=None)
        background_requested: bool | None = None
        if background_param is not None:
            flag = str(background_param).strip().lower()
            if flag in {"1", "true", "yes", "on"}:
                background_requested = True
            elif flag in {"0", "false", "no", "off"}:
                background_requested = False
        if background_requested is None:
            background_flag = mode != "inc"
        else:
            background_flag = background_requested
        deferred = bool(background_requested) and mode in {"inc", "full"}
        persist_arg = self.get_argument("persist", default=None)
        def _truthy(v: str | None) -> bool:
            if v is None:
                return False
            return str(v).strip().lower() in {"1", "true", "yes", "on"}
        persist_flag = _truthy(persist_arg)
        logger.info("/api/fetch symbol=%s tf=%s count=%s mode=%s persist=%s", symbol, timeframe, count, mode, persist_flag)
        schedule_backfill = (mode == "inc")
        info = await _perform_fetch(
            self.pool,
            symbol,
            timeframe,
            count,
            mode,
            schedule_backfill=schedule_backfill,
            persist_selection=persist_flag,
            event_scope="interactive",
            background=background_flag,
            deferred=deferred,
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


async def poll_and_store_account_balance(user: str = "lachlan") -> dict:
    """Fetch current MT5 account info and store balance snapshot."""
    if GLOBAL_POOL is None:
        return {"ok": False, "error": "no_pool"}
    try:
        info = mt5_client.account_info()
    except Exception as exc:
        logger.warning("[balance] account_info failed: %s", exc)
        return {"ok": False, "error": str(exc)}
    login = int(info.get("login") or 0)
    bal = float(info.get("balance") or 0.0)
    eq = float(info.get("equity") or 0.0)
    mar = float(info.get("margin") or 0.0)
    free = float(info.get("margin_free") or 0.0)
    ccy = str(info.get("currency") or "")
    now = datetime.now(timezone.utc)
    try:
        await upsert_account_balance(GLOBAL_POOL, user_name=user, account_id=login, ts=now, balance=bal, equity=eq, margin=mar, free_margin=free, currency=ccy)
        await emit_balance_event(user=user, account_id=login, balance=bal)
        return {"ok": True, "user": user, "account": login, "balance": bal}
    except Exception as exc:
        logger.exception("[balance] upsert failed: %s", exc)
        return {"ok": False, "error": str(exc)}


GLOBAL_POOL = None


async def make_app():
    pool = await create_pool()
    await init_schema(pool)
    global GLOBAL_POOL
    GLOBAL_POOL = pool

    def _log_request(handler: tornado.web.RequestHandler) -> None:
        try:
            path = handler.request.path
        except Exception:
            path = ""
        # Suppress noisy tick polling
        if path == "/api/tick":
            return
        try:
            status = handler.get_status()
            summary = handler._request_summary()  # type: ignore[attr-defined]
            ip = handler.request.remote_ip
            req_ms = 1000.0 * handler.request.request_time()
            access_log.info("%d %s (%s) %.2fms", status, summary, ip, req_ms)
        except Exception:
            # Fallback to default logging if something unexpected occurs
            pass

    settings = dict(
        debug=True,
        template_path=os.path.join(os.path.dirname(__file__), "..", "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "..", "static"),
        pool=pool,
        log_function=_log_request,
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
            (r"/api/health/freshness", HealthFreshnessHandler, dict(pool=pool)),
            (r"/api/tech/freshness", TechFreshnessHandler, dict(pool=pool)),
            (r"/api/account/balance_series", AccountBalanceHandler, dict(pool=pool)),
            (r"/api/account/closed_deals_sync", ClosedDealsSyncHandler),
            (r"/api/stl", STLHandler, dict(pool=pool)),
            (r"/api/stl/run/([0-9]+)", STLDeleteHandler, dict(pool=pool)),
            (r"/api/stl/compute", STLComputeHandler, dict(pool=pool)),
            (r"/api/news", NewsHandler, dict(pool=pool)),
            (r"/api/account/closed_deals", ClosedDealsHandler),
            # Backfill latest forex + equities news into DB
            (r"/api/news/backfill_forex", NewsBackfillHandler, dict(pool=pool)),
            (r"/api/news/analyze", NewsAnalysisHandler, dict(ai_client=AI_CLIENT, questions=NEWS_MICRO_QUESTIONS)),
            (r"/api/health/runs", HealthRunsHandler, dict(pool=pool)),
            (r"/api/health/run", HealthRunHandler, dict(pool=pool)),
            (r"/api/preferences", PreferencesHandler, dict(pool=pool)),
            (r"/api/ai/trade_plan", TradePlanHandler, dict(pool=pool)),
            (r"/api/config", ConfigHandler),
            (r"/ws/updates", UpdatesSocket),
            (r"/api/trades/signal", SignalTradesHandler, dict(pool=pool)),
            # Duplicate route removed (was registered twice)
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
        # Optional context for signal logging
        timeframe = self.get_argument("tf", default=None)
        strategy = self.get_argument("strategy", default=None)
        fast = self.get_argument("fast", default=None)
        slow = self.get_argument("slow", default=None)
        reason = self.get_argument("reason", default=None)
        source = self.get_argument("source", default=None)
        try:
            fast_i = int(fast) if fast not in (None, "") else None
        except Exception:
            fast_i = None
        try:
            slow_i = int(slow) if slow not in (None, "") else None
        except Exception:
            slow_i = None
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
        # Best-effort insert into signal_trades log
        try:
            if GLOBAL_POOL is not None:
                await insert_signal_trade(
                    GLOBAL_POOL,
                    symbol=symbol,
                    timeframe=timeframe,
                    action=side,
                    strategy=strategy,
                    fast=fast_i,
                    slow=slow_i,
                    volume=volume,
                    sl=sl_val,
                    tp=tp_val,
                    order_id=int(res.get("order") or 0) if isinstance(res, dict) else None,
                    deal_id=int(res.get("deal") or 0) if isinstance(res, dict) else None,
                    retcode=int(res.get("retcode") or 0) if isinstance(res, dict) else None,
                    source=source,
                    reason=reason,
                    result=res if isinstance(res, dict) else None,
                )
        except Exception as exc:
            logger.warning("signal trade log insert failed: %s", exc)
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


class SignalTradesHandler(tornado.web.RequestHandler):
    def initialize(self, pool):
        self.pool = pool

    async def get(self):
        symbol = self.get_argument("symbol", default=None)
        timeframe = self.get_argument("tf", default=None)
        limit = int(self.get_argument("limit", default="5"))
        offset = int(self.get_argument("offset", default="0"))
        try:
            rows = await list_signal_trades(self.pool, symbol=symbol, timeframe=timeframe, limit=limit, offset=offset)
            self.set_header("Content-Type", "application/json")
            self.set_header("Cache-Control", "no-store")
            self.finish(json.dumps({"ok": True, "rows": rows}))
        except Exception as exc:
            logger.exception("list signal trades failed: %s", exc)
            self.set_status(500)
            self.set_header("Content-Type", "application/json")
            self.set_header("Cache-Control", "no-store")
            self.finish(json.dumps({"ok": False, "error": str(exc)}))


class CloseHandler(tornado.web.RequestHandler):
    async def get(self):
        # Allow closing positions regardless of TRADING_ENABLED for safety
        scope = self.get_argument("scope", default="current").lower()
        symbol = self.get_argument("symbol", default=default_symbol())
        side = self.get_argument("side", default="both").lower()
        if side not in {"both", "long", "short"}:
            side = "both"
        logger.info("/api/close scope=%s symbol=%s side=%s", scope, symbol, side)
        try:
            if scope == "all":
                res = mt5_client.close_all(side=None if side == "both" else side)
            else:
                res = mt5_client.close_all_for(symbol, side=None if side == "both" else side)
        except Exception as e:
            logger.exception("close positions failed: %s", e)
            self.set_status(500)
            self.set_header("Content-Type", "application/json")
            self.set_header("Cache-Control", "no-store")
            self.finish(json.dumps({"ok": False, "error": str(e)}))
            return
        self.set_header("Content-Type", "application/json")
        self.set_header("Cache-Control", "no-store")
        try:
            closed_count = len(res) if isinstance(res, list) else 0
        except Exception:
            closed_count = 0
        # Log retcodes summary
        try:
            codes = [int(x.get("retcode", -1)) for x in (res or []) if isinstance(x, dict)]
            ok = sum(1 for c in codes if c == getattr(mt5_client.mt5, "TRADE_RETCODE_DONE", 10009)) if hasattr(mt5_client, 'mt5') else sum(1 for c in codes if c == 10009)
            logger.info("/api/close done scope=%s symbol=%s side=%s closed=%d ok=%d/%d codes=%s", scope, symbol, side, closed_count, ok, len(codes), codes[:10])
        except Exception:
            logger.info("/api/close done scope=%s symbol=%s side=%s closed=%d", scope, symbol, side, closed_count)
        self.finish(json.dumps({"ok": True, "closed": res, "closed_count": closed_count, "scope": scope, "side": side}))

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


class AccountBalanceHandler(tornado.web.RequestHandler):
    def initialize(self, pool):
        self.pool = pool

    async def get(self):
        user = self.get_argument("user", default=os.getenv("DEFAULT_USER", "lachlan"))
        acct_arg = self.get_argument("account", default=None)
        limit = int(self.get_argument("limit", default="500"))
        refresh_flag = self.get_argument("refresh", default="0").lower() in ("1", "true", "yes")
        # Resolve account id
        account_id = None
        if acct_arg:
            try:
                account_id = int(acct_arg)
            except Exception:
                account_id = None
        if account_id is None:
            try:
                info = mt5_client.account_info()
                account_id = int(info.get("login") or 0)
            except Exception:
                account_id = 0
        if account_id == 0:
            self.set_status(503)
            self.set_header("Content-Type", "application/json")
            self.finish(json.dumps({"ok": False, "error": "account unavailable"}))
            return
        if refresh_flag:
            try:
                await poll_and_store_account_balance(user=user)
            except Exception as exc:
                logger.warning("/api/account/balance_series refresh failed: %s", exc)
        rows = await fetch_account_balances(self.pool, user_name=user, account_id=account_id, limit=limit)
        self.set_header("Content-Type", "application/json")
        self.set_header("Cache-Control", "no-store")
        self.finish(json.dumps({"ok": True, "user": user, "account": account_id, "rows": rows}))


class ClosedDealsHandler(tornado.web.RequestHandler):
    async def get(self):
        # Optional time window
        days = int(self.get_argument("days", default="90"))
        start_arg = self.get_argument("from", default=None)
        end_arg = self.get_argument("to", default=None)
        debug_flag = self.get_argument("debug", default="0").lower() in ("1", "true", "yes")
        source = self.get_argument("source", default="auto").lower()  # auto|db|mt5
        comment_filters = [c for c in self.get_arguments("comment") if c]
        user = self.get_argument("user", default=os.getenv("DEFAULT_USER", "lachlan"))
        start_dt = _normalize_dt(start_arg) if start_arg else None
        end_dt = _normalize_dt(end_arg) if end_arg else None
        if not end_dt:
            end_dt = datetime.now(timezone.utc)
        if not start_dt:
            start_dt = end_dt - timedelta(days=max(1, days))
        # Resolve account id
        try:
            info = mt5_client.account_info()
            account_id = int(info.get("login") or 0)
        except Exception:
            account_id = 0
        try:
            logger.info("/api/account/closed_deals from=%s to=%s days=%s source=%s comment_filters=%s", start_dt, end_dt, days, source, comment_filters)
            deals = []
            from_db = False
            if source in ("auto", "db"):
                deals = await fetch_closed_deals_between(GLOBAL_POOL, account_id=account_id, start_ts=start_dt, end_ts=end_dt)
                from_db = bool(deals)
            if source == "mt5" or (source == "auto" and not from_db):
                deals = mt5_client.closed_deals(start_dt, end_dt)
                if debug_flag:
                    try:
                        sample = [
                            {
                                "ts": d.get("ts"),
                                "symbol": d.get("symbol"),
                                "profit": d.get("profit"),
                                "entry": d.get("entry"),
                                "deal": d.get("deal"),
                                "order": d.get("order"),
                                "comment": d.get("comment"),
                            }
                            for d in (deals[:5] + deals[-5:] if len(deals) > 10 else deals)
                        ]
                        logger.info("[closed_deals debug] mt5 sample=%s", sample)
                    except Exception:
                        pass
                # Best-effort persist to DB for future queries
                try:
                    if deals:
                        await upsert_closed_deals(GLOBAL_POOL, account_id=account_id, rows=deals)
                except Exception as exc:
                    logger.warning("/api/account/closed_deals upsert failed: %s", exc)
        except Exception as e:
            self.set_status(500)
            self.set_header("Content-Type", "application/json")
            self.set_header("Cache-Control", "no-store")
            self.finish(json.dumps({"ok": False, "error": str(e)}))
            return
        if comment_filters:
            lf = [c.lower() for c in comment_filters]
            deals = [d for d in deals if any(f in str(d.get("comment", "")).lower() for f in lf)]
        # Build cumulative PnL series over time
        cum = 0.0
        cum_points: list[dict] = []
        for d in deals:
            p = float(d.get("profit") or 0.0)
            c = float(d.get("commission") or 0.0)
            s = float(d.get("swap") or 0.0)
            cum += (p + c + s)
            cum_points.append({"ts": d.get("ts"), "value": cum})
        # Synthetic overlay: baseline balance + cumulative deals
        synthetic_points: list[dict] = []
        try:
            base_row = await latest_balance_before(GLOBAL_POOL, user_name=user, account_id=account_id, ts=start_dt)
            base_val = float(base_row.get("balance")) if base_row else None
            if base_val is not None:
                for pt in cum_points:
                    synthetic_points.append({"ts": pt.get("ts"), "value": base_val + float(pt.get("value") or 0.0)})
        except Exception:
            synthetic_points = []
        try:
            logger.info("/api/account/closed_deals ok deals=%d cum_points=%d synthetic=%d (from_db=%s)", len(deals), len(cum_points), len(synthetic_points), from_db)
        except Exception:
            pass
        self.set_header("Content-Type", "application/json")
        self.set_header("Cache-Control", "no-store")
        self.finish(json.dumps({
            "ok": True,
            "from": start_dt.isoformat(),
            "to": end_dt.isoformat(),
            "deals": deals,
            "deals_count": len(deals),
            "cum": cum_points,
            "cum_count": len(cum_points),
            "synthetic": synthetic_points,
            "source": ("db" if from_db else "mt5") if source == "auto" else source,
            "comment_filters": comment_filters,
        }))


class ClosedDealsSyncHandler(tornado.web.RequestHandler):
    async def post(self):
        # Full or ranged sync; default from 5 years ago to now
        start_arg = self.get_argument("from", default=None)
        end_arg = self.get_argument("to", default=None)
        step_days = int(self.get_argument("step", default="90"))
        start_dt = _normalize_dt(start_arg) if start_arg else datetime.now(timezone.utc) - timedelta(days=5*365)
        end_dt = _normalize_dt(end_arg) if end_arg else datetime.now(timezone.utc)
        # Resolve account id
        try:
            info = mt5_client.account_info()
            account_id = int(info.get("login") or 0)
        except Exception as e:
            self.set_status(503)
            self.set_header("Content-Type", "application/json")
            self.finish(json.dumps({"ok": False, "error": f"account unavailable: {e}"}))
            return
        logger.info("/api/account/closed_deals_sync from=%s to=%s step=%sd", start_dt, end_dt, step_days)
        async def runner():
            try:
                total = 0
                cur = start_dt
                while cur < end_dt:
                    nxt = min(end_dt, cur + timedelta(days=step_days))
                    deals = mt5_client.closed_deals(cur, nxt)
                    if deals:
                        try:
                            await upsert_closed_deals(GLOBAL_POOL, account_id=account_id, rows=deals)
                            total += len(deals)
                            logger.info("[closed_sync] %s-%s inserted=%d total=%d", cur, nxt, len(deals), total)
                        except Exception as exc:
                            logger.warning("[closed_sync] upsert failed: %s", exc)
                    cur = nxt
                await emit_closed_deals_event()
                logger.info("[closed_sync] completed total=%d", total)
            except Exception as exc:
                logger.exception("[closed_sync] failed: %s", exc)
        tornado.ioloop.IOLoop.current().spawn_callback(runner)
        self.set_header("Content-Type", "application/json")
        self.finish(json.dumps({"ok": True, "scheduled": True}))


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
                if value is None:
                    continue
                allowed = False
                if key in PREF_KEYS:
                    allowed = True
                # Allow per-symbol×timeframe STL auto compute preferences
                elif isinstance(key, str) and key.startswith("stl_auto_compute:"):
                    allowed = True
                # Allow per-symbol×timeframe auto health/tech checks
                elif isinstance(key, str) and (
                    key.startswith("auto_check:") or
                    key.startswith("auto_check_basic:") or
                    key.startswith("auto_check_tech:")
                ):
                    allowed = True
                if allowed:
                    updates[key] = str(value)
        if updates:
            await set_prefs(self.pool, updates)
            # Handle auto news backfill scheduler toggle dynamically
            if "auto_news_backfill" in updates:
                val = str(updates.get("auto_news_backfill") or "1").lower() not in ("0", "false", "no", "off")
                global NEWS_BACKFILL_CB
                try:
                    interval_min = int(os.getenv("NEWS_BACKFILL_MIN", "30"))
                except Exception:
                    interval_min = 30
                loop = tornado.ioloop.IOLoop.current()
                if val:
                    schedule_news_backfill_aligned(max(1, interval_min))
                else:
                    try:
                        if NEWS_BACKFILL_CB is not None:
                            loop.remove_timeout(NEWS_BACKFILL_CB)
                    except Exception:
                        pass
                    NEWS_BACKFILL_CB = None
            # Handle closed orders polling interval
            if "closed_orders_poll_min" in updates:
                try:
                    minutes = int(str(updates.get("closed_orders_poll_min") or "30"))
                except Exception:
                    minutes = 30
                minutes = max(1, minutes)
                from tornado.ioloop import PeriodicCallback
                global CLOSED_ORDERS_CB
                try:
                    if CLOSED_ORDERS_CB is not None:
                        CLOSED_ORDERS_CB.stop()
                except Exception:
                    pass
                try:
                    CLOSED_ORDERS_CB = PeriodicCallback(lambda: tornado.ioloop.IOLoop.current().add_callback(emit_closed_deals_event), minutes * 60 * 1000)
                    CLOSED_ORDERS_CB.start()
                except Exception:
                    CLOSED_ORDERS_CB = None
            # Handle balance snapshot polling interval
            if "balance_poll_min" in updates:
                try:
                    minutes = int(str(updates.get("balance_poll_min") or "60"))
                except Exception:
                    minutes = 60
                minutes = max(1, minutes)
                from tornado.ioloop import PeriodicCallback
                global BALANCE_CB
                try:
                    if BALANCE_CB is not None:
                        BALANCE_CB.stop()
                except Exception:
                    pass
                try:
                    BALANCE_CB = PeriodicCallback(lambda: tornado.ioloop.IOLoop.current().add_callback(poll_and_store_account_balance), minutes * 60 * 1000)
                    BALANCE_CB.start()
                except Exception:
                    BALANCE_CB = None
        self.set_header("Content-Type", "application/json")
        self.set_header("Cache-Control", "no-store")
        self.finish(json.dumps({"ok": True, "updated": sorted(updates.keys())}))


class HealthFreshnessHandler(tornado.web.RequestHandler):
    def initialize(self, pool):
        self.pool = pool

    async def get(self):
        symbol = str(self.get_argument("symbol", default=default_symbol())).upper()
        strategy = self.get_argument("strategy", default=None)

        # Determine kind and defaults
        if _is_fx_symbol(symbol):
            kind = "forex_pair"
            base = symbol[:3]
            quote = symbol[3:6]
        else:
            kind = "stock"
            base = None
            quote = None
        if not strategy:
            strategy = DEFAULT_STRATEGIES.get(kind)

        # Find latest run for this symbol/strategy
        try:
            if kind == "stock":
                runs = await list_health_runs(self.pool, kind=kind, symbol=symbol, limit=1, strategy=str(strategy) if strategy else None)
            else:
                runs = await list_health_runs(self.pool, kind=kind, base_ccy=base, quote_ccy=quote, limit=1, strategy=str(strategy) if strategy else None)
            # Fallback: if no run found for the requested strategy, use the latest non-tech run
            if not runs:
                if kind == "stock":
                    runs = await list_health_runs(self.pool, kind=kind, symbol=symbol, limit=1, exclude_strategy="tech_snapshot_10q.json")
                else:
                    runs = await list_health_runs(self.pool, kind=kind, base_ccy=base, quote_ccy=quote, limit=1, exclude_strategy="tech_snapshot_10q.json")
        except Exception:
            runs = []
        last_run = runs[0] if runs else None
        last_run_at_dt = last_run.get("created_at") if last_run else None
        last_run_at = last_run_at_dt.isoformat() if last_run_at_dt else None
        last_news_used = int(last_run.get("news_count") or 0) if last_run else 0

        # Determine the latest published time among the news actually used in the run
        base_url_list: list[str] = []
        used_symbols: set[str] = set()
        try:
            raw_ids = list((last_run or {}).get("news_ids") or [])
        except Exception:
            raw_ids = []
        if raw_ids:
            for ident in raw_ids:
                try:
                    s = str(ident)
                    # Forex runs store "CCY:url"; stocks store plain URL
                    if len(s) > 4 and s[:3].isalpha() and s[3] == ":":
                        used_symbols.add(s[:3].upper())
                        base_url_list.append(s[4:])
                    else:
                        base_url_list.append(s)
                except Exception:
                    continue
        # For stocks, ensure symbol is counted even if news_ids had plain URLs
        if kind == "stock" and symbol:
            used_symbols.add(symbol)
        # For forex, include explicit base/quote as fallbacks
        if kind == "forex_pair":
            if base: used_symbols.add(base)
            if quote: used_symbols.add(quote)

        baseline_ts = None
        baseline_iso = None
        baseline_src = None
        # 1) Prefer explicit meta timestamp if present on the run (newer runs store this)
        try:
            if last_run:
                ans = last_run.get("answers_json") or last_run.get("answers") or {}
                meta = ans.get("meta") or {}
                val = meta.get("last_used_news_ts")
                if isinstance(val, str) and val:
                    from datetime import datetime as _dt
                    from datetime import timezone as _tz
                    v = val.strip()
                    if v.endswith('Z'):
                        v = v[:-1] + '+00:00'
                    baseline_ts = _dt.fromisoformat(v)
                    if baseline_ts.tzinfo is None:
                        baseline_ts = baseline_ts.replace(tzinfo=_tz.utc)
                    baseline_iso = baseline_ts.isoformat()
                    baseline_src = "meta"
        except Exception:
            baseline_ts = None
            baseline_iso = None
        # 2) If meta missing, resolve via DB using the used URLs
        if baseline_ts is None:
            try:
                if base_url_list:
                    async with self.pool.acquire() as conn:
                        db_ts = await conn.fetchval(
                            "SELECT MAX(COALESCE(published_at, created_at)) FROM news_articles WHERE url = ANY($1::text[])",
                            base_url_list,
                        )
                    if db_ts is not None and hasattr(db_ts, "isoformat"):
                        baseline_ts = db_ts
                        baseline_iso = db_ts.isoformat()
                        baseline_src = "urls_db"
            except Exception:
                baseline_ts = None
                baseline_iso = None
        # 3) Fallback to run creation time if still unresolved
        if baseline_ts is None and last_run_at_dt is not None:
            baseline_ts = last_run_at_dt
            baseline_iso = last_run_at
            baseline_src = "run_created_at"

        # Latest news timestamp and count since last run (match the News panel: per current symbol)
        latest_news_iso = None
        new_count = None
        try:
            async with self.pool.acquire() as conn:
                latest_ts = await conn.fetchval(
                    "SELECT MAX(COALESCE(published_at, created_at)) FROM news_articles WHERE symbol=$1",
                    symbol,
                )
                if latest_ts is not None and hasattr(latest_ts, "isoformat"):
                    latest_news_iso = latest_ts.isoformat()
                # Count newer items strictly after the baseline used for that run
                if 'baseline_ts' in locals() and baseline_ts is not None:
                    new_count_val = await conn.fetchval(
                        "SELECT COUNT(*)::INT FROM news_articles WHERE symbol=$1 AND COALESCE(published_at, created_at) > $2",
                        symbol,
                        baseline_ts,
                    )
                    new_count = int(new_count_val or 0)
                else:
                    # If never ran, report total as 'new'
                    new_count_val = await conn.fetchval(
                        "SELECT COUNT(*)::INT FROM news_articles WHERE symbol=$1",
                        symbol,
                    )
                    new_count = int(new_count_val or 0)
        except Exception:
            pass

        # Emit a concise trace to help diagnose freshness calcs
        try:
            logger.info(
                "[freshness.basic] symbol=%s kind=%s strat=%s run_id=%s last_run_at=%s meta_last=%s urls=%d baseline_at=%s baseline_src=%s latest_at=%s new_count=%s used_syms=%s",
                symbol,
                kind,
                str(strategy) if strategy else None,
                (last_run.get("id") if last_run else None),
                last_run_at,
                ((last_run.get("answers_json") or {}).get("meta", {}).get("last_used_news_ts") if last_run else None),
                len(base_url_list),
                baseline_iso,
                baseline_src,
                latest_news_iso,
                new_count,
                sorted(list(used_symbols)) if used_symbols else [],
            )
        except Exception:
            logger.debug("[freshness.basic] trace logging failed", exc_info=True)

        status = "unknown"
        if last_run_at_dt is not None:
            status = "fresh" if (new_count or 0) == 0 else "stale"
        elif (new_count or 0) > 0:
            status = "stale"

        self.set_header("Content-Type", "application/json")
        self.set_header("Cache-Control", "no-store")
        self.finish(
            json.dumps(
                {
                    "ok": True,
                    "symbol": symbol,
                    "kind": kind,
                    "strategy": strategy,
                    "status": status,
                    "latest_news_at": latest_news_iso,
                    "last_run_at": last_run_at,
                    "baseline_at": baseline_iso,
                    "new_count": new_count,
                    "last_run_news_count": last_news_used,
                }
            )
        )


class TechFreshnessHandler(tornado.web.RequestHandler):
    def initialize(self, pool):
        self.pool = pool

    async def get(self):
        symbol = str(self.get_argument("symbol", default=default_symbol())).upper()
        timeframe = str(self.get_argument("tf", default="H1")).upper()

        # Determine kind and get latest tech snapshot run for this symbol
        if _is_fx_symbol(symbol):
            kind = "forex_pair"
            base = symbol[:3]
            quote = symbol[3:6]
            runs = await list_health_runs(self.pool, kind=kind, base_ccy=base, quote_ccy=quote, limit=5, strategy="tech_snapshot_10q.json")
        else:
            kind = "stock"
            runs = await list_health_runs(self.pool, kind=kind, symbol=symbol, limit=5, strategy="tech_snapshot_10q.json")

        # Prefer a run that matches the requested timeframe in its meta
        def _match_tf(run: dict) -> bool:
            try:
                ans = run.get("answers_json") or run.get("answers") or {}
                meta = ans.get("meta") or {}
                tfv = str(meta.get("timeframe") or "").upper()
                return tfv == timeframe
            except Exception:
                return False
        matching = [r for r in runs if _match_tf(r)]
        # Prefer matching timeframe; otherwise fall back to most recent tech run
        runs = (matching or runs)[:1]

        last_run = runs[0] if runs else None
        last_run_at = last_run.get("created_at").isoformat() if last_run and last_run.get("created_at") else None
        meta = (last_run.get("answers") or last_run.get("answers_json") or {}).get("meta") if last_run else None
        last_bar_ts_used = None
        if isinstance(meta, dict):
            val = meta.get("last_bar_ts")
            if isinstance(val, str) and val:
                last_bar_ts_used = val

        latest_bar_iso = None
        outdated = None
        try:
            async with self.pool.acquire() as conn:
                latest_ts = await conn.fetchval(
                    "SELECT MAX(ts) FROM ohlc_bars WHERE symbol=$1 AND timeframe=$2",
                    symbol,
                    timeframe,
                )
                if latest_ts is not None and hasattr(latest_ts, "isoformat"):
                    latest_bar_iso = latest_ts.isoformat()
                # Count bars in requested timeframe strictly after the bar used by the last Tech+AI run
                from datetime import datetime as _dt
                base_ts = None
                if last_bar_ts_used:
                    try:
                        base_ts = _dt.fromisoformat(last_bar_ts_used)
                    except Exception:
                        base_ts = None
                # Fallback to the run's created_at time if meta is missing (older runs)
                if base_ts is None and last_run and last_run.get("created_at"):
                    base_ts = last_run.get("created_at")
                if base_ts is not None:
                    cnt = await conn.fetchval(
                        "SELECT COUNT(*)::INT FROM ohlc_bars WHERE symbol=$1 AND timeframe=$2 AND ts > $3",
                        symbol,
                        timeframe,
                        base_ts,
                    )
                    outdated = int(cnt or 0)
        except Exception:
            pass

        status = "unknown"
        if outdated is not None:
            status = "fresh" if outdated == 0 else "stale"

        self.set_header("Content-Type", "application/json")
        self.set_header("Cache-Control", "no-store")
        self.finish(
            json.dumps(
                {
                    "ok": True,
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "kind": kind,
                    "status": status,
                    "outdated_bars": outdated,
                    "last_run_at": last_run_at,
                    "last_bar_ts_used": last_bar_ts_used,
                    "latest_bar_ts": latest_bar_iso,
                }
            )
        )
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
    def initialize(self, pool):
        self.pool = pool

    async def get(self):
        symbol = self.get_argument("symbol", default=default_symbol())
        refresh_flag = self.get_argument("refresh", default="0").lower() in ("1", "true", "yes")
        loop = tornado.ioloop.IOLoop.current()
        one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        logger.info("/api/news symbol=%s (since %s) refresh=%s", symbol, one_week_ago.date().isoformat(), refresh_flag)
        rows = []
        if refresh_flag:
            try:
                digest = await loop.run_in_executor(EXECUTOR, lambda: fetch_symbol_digest(symbol, limit=50))
                live = digest.get("news", [])
                for it in live:
                    it["symbol"] = symbol.upper()
                if live:
                    try:
                        inserted = await upsert_news_articles(self.pool, live)
                        logger.info("[news] refresh fetched=%d inserted=%d for %s", len(live), inserted, symbol)
                        if inserted:
                            await emit_news_event(
                                symbol=symbol,
                                status="refreshed",
                                scope="manual",
                                background=False,
                                items=inserted,
                                note="refresh",
                            )
                    except Exception:
                        logger.exception("[news] refresh upsert failed for %s", symbol)
            except Exception as e:
                logger.warning("[news] refresh fetch failed for %s: %s", symbol, e)
        try:
            rows = await fetch_news_db(self.pool, symbol.upper(), since=one_week_ago, limit=30)
        except Exception:
            rows = []
        logger.info("[news] DB rows=%d for %s", len(rows), symbol)
        snapshot = {}
        if not rows:
            logger.info("[news] DB empty for %s, fetching live digest", symbol)
            try:
                digest = await loop.run_in_executor(EXECUTOR, lambda: fetch_symbol_digest(symbol, limit=25))
                snapshot = digest.get("snapshot", {})
                live = digest.get("news", [])
                for it in live:
                    it["symbol"] = symbol.upper()
                try:
                    inserted = await upsert_news_articles(self.pool, live)
                    logger.info("[news] live fetched=%d inserted=%d for %s", len(live), inserted, symbol)
                    if inserted:
                        await emit_news_event(
                            symbol=symbol,
                            status="refreshed",
                            scope="manual",
                            background=False,
                            items=inserted,
                            note="digest",
                        )
                except Exception:
                    logger.exception("[news] upsert live failed for %s", symbol)
                rows = live
            except Exception as e:
                logger.exception("[news] live fetch failed for %s: %s", symbol, e)
                self.set_status(500)
                self.set_header("Content-Type", "application/json")
                self.set_header("Cache-Control", "no-store")
                self.finish(json.dumps({"ok": False, "error": str(e), "news": [], "snapshot": {}}))
                return
        if not snapshot:
            try:
                snapshot = await loop.run_in_executor(EXECUTOR, lambda: fetch_fmp_snapshot(symbol))
            except Exception as exc:
                logger.warning("[news] snapshot fallback failed for %s: %s", symbol, exc)
                snapshot = {}
        self.set_header("Content-Type", "application/json")
        self.set_header("Cache-Control", "no-store")
        logger.info("[news] respond symbol=%s count=%d snapshot=%s", symbol, len(rows), bool(snapshot))
        self.finish(json.dumps({"ok": True, "symbol": symbol, "news": rows, "snapshot": snapshot}))


class NewsBackfillHandler(tornado.web.RequestHandler):
    def initialize(self, pool):
        self.pool = pool

    async def _run(self):
        try:
            # Allow days to be provided via JSON body or query arg; default 7
            days = 7
            try:
                # Query param has priority for quick manual triggering
                if self.get_argument("days", None) is not None:
                    days = int(self.get_argument("days"))
            except Exception:
                pass
            try:
                if self.request.body:
                    payload = json.loads(self.request.body or "{}")
                    d = payload.get("days")
                    if d is not None:
                        days = int(d)
            except Exception:
                # Ignore malformed bodies; keep default
                pass

            logger.info("/api/news/backfill_forex requested days=%d", days)
            result = await run_news_backfill(days=days)
            self.set_header("Content-Type", "application/json")
            self.set_header("Cache-Control", "no-store")
            self.finish(json.dumps(result))
        except Exception as e:
            self.set_status(500)
            self.set_header("Content-Type", "application/json")
            self.set_header("Cache-Control", "no-store")
            self.finish(json.dumps({"ok": False, "error": str(e)}))

    async def post(self):
        await self._run()

    async def get(self):
        # Convenience: allow GET to trigger backfill for manual testing
        await self._run()
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


class HealthRunsHandler(tornado.web.RequestHandler):
    def initialize(self, pool):
        self.pool = pool

    async def get(self):
        raw_kind = self.get_argument("kind", default="").lower()
        symbol = self.get_argument("symbol", default=None)
        base = self.get_argument("base", default=None)
        quote = self.get_argument("quote", default=None)
        limit = int(self.get_argument("limit", default="5"))
        offset = int(self.get_argument("offset", default="0"))
        strategy_filter = self.get_argument("strategy", default=None)
        exclude_strategy = self.get_argument("exclude_strategy", default=None)
        tf_filter = self.get_argument("tf", default=None)
        group_filter = self.get_argument("group", default=None)

        # Auto-detect kind if not explicitly provided
        kind = raw_kind
        if not kind:
            if base and quote:
                kind = "forex_pair"
            elif _is_fx_symbol(symbol):
                kind = "forex_pair"
            else:
                kind = "stock"

        if kind == "forex_pair":
            if (not base or not quote) and symbol:
                sym = str(symbol).upper()
                if len(sym) >= 6:
                    base = sym[:3]
                    quote = sym[3:6]
            if not base or not quote:
                self.set_status(400)
                self.set_header("Content-Type", "application/json")
                self.finish(json.dumps({"ok": False, "error": "base/quote required for forex_pair"}))
                return
            # When grouping, fetch a larger pool then filter in-memory
            if group_filter:
                fetch_limit = max(40, limit * 6)
                runs = await list_health_runs(
                    self.pool,
                    kind="forex_pair",
                    base_ccy=base.upper(),
                    quote_ccy=quote.upper(),
                    limit=fetch_limit,
                    offset=0,
                    strategy=None,
                    exclude_strategy=None,
                )
            else:
                runs = await list_health_runs(
                    self.pool,
                    kind="forex_pair",
                    base_ccy=base.upper(),
                    quote_ccy=quote.upper(),
                    limit=limit,
                    offset=offset,
                    strategy=(strategy_filter or None) if strategy_filter else None,
                    exclude_strategy=(exclude_strategy or None) if exclude_strategy else None,
                )
        else:
            if not symbol:
                symbol = default_symbol()
            if group_filter:
                fetch_limit = max(40, limit * 6)
                runs = await list_health_runs(
                    self.pool,
                    kind="stock",
                    symbol=str(symbol).upper(),
                    limit=fetch_limit,
                    offset=0,
                    strategy=None,
                    exclude_strategy=None,
                )
            else:
                runs = await list_health_runs(
                    self.pool,
                    kind="stock",
                    symbol=str(symbol).upper(),
                    limit=limit,
                    offset=offset,
                    strategy=(strategy_filter or None) if strategy_filter else None,
                    exclude_strategy=(exclude_strategy or None) if exclude_strategy else None,
                )

        def _ser(run: dict) -> dict:
            created_at = run.get("created_at")
            if created_at and hasattr(created_at, "isoformat"):
                created_at = created_at.isoformat()
            return {
                "id": run.get("id"),
                "kind": run.get("kind"),
                "symbol": run.get("symbol"),
                "base_ccy": run.get("base_ccy"),
                "quote_ccy": run.get("quote_ccy"),
                "news_count": run.get("news_count"),
                "news_ids": run.get("news_ids") or [],
                "answers": run.get("answers_json") or {},
                "created_at": created_at,
            }

        # Optional timeframe filter based on answers_json.meta.timeframe
        if tf_filter:
            tf_up = str(tf_filter).upper()
            filtered = []
            for r in runs:
                try:
                    ans = r.get("answers_json") or {}
                    meta = ans.get("meta") or {}
                    tfv = str(meta.get("timeframe") or "").upper()
                    if tfv == tf_up:
                        filtered.append(r)
                except Exception:
                    continue
            runs = filtered

        # Optional group filter. Newer runs carry answers_json.group.
        # Backfill for older rows using strategy name.
        if group_filter:
            g = str(group_filter).lower()
            def derive_group(r: dict) -> str:
                ans = r.get("answers_json") or {}
                grp = str((ans.get("group") or "")).lower()
                if grp:
                    return grp
                strat = str((ans.get("strategy") or "")).lower()
                if strat == "tech_snapshot_10q.json":
                    return "tech"
                if strat == "ai_trade_plan":
                    return "plan"
                return "basic"
            grouped = [r for r in runs if derive_group(r) == g]
            # Apply offset/limit after grouping
            start = max(0, offset)
            end = start + max(1, limit)
            runs = grouped[start:end]

        payload = {"ok": True, "runs": [_ser(r) for r in runs]}
        self.set_header("Content-Type", "application/json")
        self.set_header("Cache-Control", "no-store")
        self.finish(json.dumps(payload))


class HealthRunHandler(tornado.web.RequestHandler):
    def initialize(self, pool):
        self.pool = pool

    async def post(self):
        global AI_CLIENT
        if AI_CLIENT is None:
            self.set_status(503)
            self.set_header("Content-Type", "application/json")
            self.finish(json.dumps({"ok": False, "error": "LLM unavailable"}))
            return
        try:
            payload = json.loads(self.request.body or "{}")
        except Exception:
            payload = {}

        kind = str(payload.get("kind") or "").lower()
        # Optional template override coming from the UI select (e.g. forex_pair_neutral_30q.json)
        strategy_override = str(payload.get("strategy") or payload.get("template") or "").strip()
        timeframe = str(payload.get("timeframe") or "30d")
        news_count = int(payload.get("news_count") or 10)
        # Optional model override for health checks (basic and tech)
        model_override = str(payload.get("model") or "").strip() or None
        def _infer_provider(model_name: str | None) -> str | None:
            if not model_name:
                return None
            low = str(model_name).strip().lower()
            if low.startswith("deepseek"):
                return "deepseek"
            return None
        provider_override = _infer_provider(model_override)

        loop = tornado.ioloop.IOLoop.current()

        # Auto-detect kind when omitted
        symbol_raw = str(payload.get("symbol") or payload.get("ticker") or "").upper()
        if not kind:
            if payload.get("base_currency") and payload.get("quote_currency"):
                kind = "forex_pair"
            elif _is_fx_symbol(symbol_raw):
                kind = "forex_pair"
            else:
                kind = "stock"

        # Special strategy: technical snapshot analysis (10Q), uses client-provided snapshot text
        if strategy_override == "tech_snapshot_10q.json":
            symbol = (payload.get("symbol") or payload.get("ticker") or default_symbol()).upper()
            timeframe = str(payload.get("timeframe") or payload.get("tf") or "H1").upper()
            snapshot_text = str(payload.get("tech_snapshot") or "").strip()
            if not snapshot_text:
                self.set_status(400)
                self.set_header("Content-Type", "application/json")
                self.finish(json.dumps({"ok": False, "error": "tech_snapshot text required"}))
                return
            strat = _load_strategy_json("tech_snapshot_10q.json")
            questions = [q for q in (strat.get("questions") or []) if isinstance(q, dict)]
            choice_options = ["BULLISH", "BEARISH"]

            loop = tornado.ioloop.IOLoop.current()
            def _call_one(qobj: dict) -> tuple[str, str, str]:
                qid = str(qobj.get("id") or "")
                raw_text = str(qobj.get("text") or "")
                prompt = _build_tech_prompt(raw_text, symbol, timeframe, snapshot_text, choice_options)
                out = AI_CLIENT.send_request_with_json_schema(
                    prompt,
                    _make_choice_schema(choice_options),
                    system_content="You are a decisive technical analyst. Reply only with JSON that matches the schema.",
                    schema_name="tech_choice_answer",
                    model=model_override,
                    provider=provider_override,
                )
                ans_raw = str((out or {}).get("answer") or "").strip().upper()
                if ans_raw not in choice_options:
                    ans_raw = choice_options[1]
                expl = str((out or {}).get("explanation") or "").strip()
                return (qid, ans_raw, expl)

            from concurrent.futures import ThreadPoolExecutor as _TPE
            local_workers = min(8, max(1, len(questions)))
            answers: list[tuple[str, str, str]] = []
            if questions:
                with _TPE(max_workers=local_workers) as ex:
                    futs = [loop.run_in_executor(ex, _call_one, q) for q in questions]
                    answers = await asyncio.gather(*futs, return_exceptions=False)

            a_map: dict[str, tuple[str, str]] = {qid: (val, expl) for qid, val, expl in answers}
            ans_struct: list[dict[str, Any]] = []
            bullish = 0
            bearish = 0
            for q in questions:
                qid = str(q.get("id"))
                val, expl = a_map.get(qid, ("BEARISH", ""))
                if isinstance(val, str) and val.upper() == "BULLISH":
                    bullish += 1
                elif isinstance(val, str) and val.upper() == "BEARISH":
                    bearish += 1
                ans_struct.append({"id": qid, "answer": str(val).upper(), "explanation": str(expl)})

            score_value = bullish - bearish
            # Determine signal via thresholds in JSON if present
            signal = "NEUTRAL"
            thresholds = (strat.get("scoring") or {}).get("thresholds", [])
            for th in thresholds:
                try:
                    if int(th.get("min")) <= score_value <= int(th.get("max")):
                        signal = str(th.get("signal") or signal)
                        break
                except Exception:
                    continue

            # Persist as generic run under detected kind
            is_fx = _is_fx_symbol(symbol)
            base_ccy = symbol[:3] if is_fx else None
            quote_ccy = symbol[3:6] if is_fx else None
            # Capture the latest bar timestamp used as reference for freshness
            last_bar_ts_iso = None
            try:
                rows_latest = await fetch_ohlc_bars(self.pool, symbol, timeframe, 1)
                if rows_latest:
                    last_bar_ts_iso = rows_latest[-1].get("ts")
            except Exception:
                last_bar_ts_iso = None
            ins = await insert_health_run(
                self.pool,
                kind="forex_pair" if is_fx else "stock",
                symbol=symbol,
                base_ccy=base_ccy,
                quote_ccy=quote_ccy,
                news_count=0,
                news_ids=[],
                answers_json={
                    "questions": ans_struct,
                    "score": score_value,
                    "signal": signal,
                    "strategy": "tech_snapshot_10q.json",
                    "group": "tech",
                    "scores": {"BULLISH": bullish, "BEARISH": bearish, "NET": score_value},
                    "meta": {"timeframe": timeframe, "symbol": symbol, "source": "snapshot", "last_bar_ts": last_bar_ts_iso},
                },
            )

            self.set_header("Content-Type", "application/json")
            self.set_header("Cache-Control", "no-store")
            self.finish(
                json.dumps(
                    {
                        "ok": True,
                        "kind": "forex_pair" if is_fx else "stock",
                        "symbol": symbol,
                        "answers": ans_struct,
                        "score": score_value,
                        "scores": {"BULLISH": bullish, "BEARISH": bearish, "NET": score_value},
                        "signal": signal,
                        "strategy": "tech_snapshot_10q.json",
                        "run_id": ins.get("id"),
                        "created_at": ins.get("created_at").isoformat() if ins.get("created_at") else None,
                    }
                )
            )
            return

        if kind == "forex_pair":
            # Derive pair symbol
            sym = str(payload.get("symbol") or symbol_raw or "").upper()
            base = str(payload.get("base_currency") or payload.get("base") or "").upper()
            quote = str(payload.get("quote_currency") or payload.get("quote") or "").upper()
            if (not sym or len(sym) < 6) and base and quote:
                sym = f"{base}{quote}"
            if not sym or len(sym) < 6:
                self.set_status(400)
                self.set_header("Content-Type", "application/json")
                self.finish(json.dumps({"ok": False, "error": "symbol (pair) required e.g. XAUUSD"}))
                return
            base, quote = sym[:3], sym[3:6]

            # Read from DB newest-first (7d window). No provider fetch here.
            one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)
            try:
                items = await fetch_news_db(self.pool, sym, since=one_week_ago, limit=news_count)
            except Exception:
                items = []

            allowed = ALLOWED_STRATEGIES.get("forex_pair", set())
            # Auto-pick metals template for XAU/XAG when no override provided
            prefer_metals = base in {"XAU", "XAG"}
            if strategy_override and strategy_override in allowed:
                strategy_name = strategy_override
            elif prefer_metals and "metal_pair_compact_10q_position.json" in allowed:
                strategy_name = "metal_pair_compact_10q_position.json"
            else:
                strategy_name = DEFAULT_STRATEGIES["forex_pair"]
            if strategy_override and strategy_override not in allowed:
                logger.warning("[health] unsupported forex strategy override %s, using default", strategy_override)
            strat = _load_strategy_json(strategy_name)
            if not strat:
                logger.warning("[health] failed to load strategy %s, falling back to default", strategy_name)
                strategy_name = DEFAULT_STRATEGIES["forex_pair"]
                strat = _load_strategy_json(strategy_name)
            # Detect per-question position schema (BUY/SELL with SL/TP)
            question_schema = strat.get("question_response_schema") if isinstance(strat, dict) else None
            answer_type = _strategy_answer_type(strat)
            if answer_type not in {"bool", "choice"}:
                answer_type = "bool"
            choice_template = strat.get("answer_options") if answer_type == "choice" else []
            logger.info("[health] strategy=%s kind=forex_pair symbol=%s news=%d", strategy_name, sym, news_count)

            questions = [q for q in (strat.get("questions") or []) if isinstance(q, dict)]

            # Upsert the used news into DB under the pair symbol (so freshness can resolve exact article times)
            try:
                pair_symbol = f"{base}{quote}"
                combined_items = []
                seen_urls: set[str] = set()
                for it in items:
                    u = (it or {}).get("url")
                    if not u or u in seen_urls:
                        continue
                    seen_urls.add(u)
                    row = dict(it)
                    row["symbol"] = pair_symbol
                    combined_items.append(row)
                if combined_items:
                    await upsert_news_articles(self.pool, combined_items)
            except Exception:
                logger.debug("[health] upsert of used news failed", exc_info=True)

            def _call_one(qobj: dict) -> tuple[str, Any, str]:
                qid = str(qobj.get("id") or "")
                raw_text = str(qobj.get("text") or "")
                question_text = _substitute_currency_tokens(raw_text, base, quote)
                # Per-question position schema overrides the legacy choice/bool behavior
                if isinstance(question_schema, dict):
                    prompt = _build_pair_prompt_position_question(question_text, sym, items, timeframe)
                    out = AI_CLIENT.send_request_with_json_schema(
                        prompt,
                        question_schema,
                        system_content="You are a decisive FX analyst. Reply only with JSON that matches the schema.",
                        schema_name="fx_question_position",
                        model=model_override,
                        provider=provider_override,
                    )
                    return (qid, out, str((out or {}).get("explanation") or ""))
                if answer_type == "choice":
                    resolved_options = choice_template or [base, quote]
                    resolved_options = [
                        _substitute_currency_tokens(opt, base, quote).strip().upper()
                        for opt in resolved_options
                        if opt
                    ]
                    if not resolved_options:
                        resolved_options = [base.upper(), quote.upper()]
                    prompt = _build_pair_prompt_choice_combined(question_text, sym, items, timeframe, resolved_options)
                    out = AI_CLIENT.send_request_with_json_schema(
                        prompt,
                        _make_choice_schema(resolved_options),
                        system_content="You are a decisive analyst. Reply only with JSON that matches the schema.",
                        schema_name="fx_choice_answer",
                        model=model_override,
                        provider=provider_override,
                    )
                    ans_raw = str((out or {}).get("answer") or "").strip().upper()
                    if ans_raw not in resolved_options:
                        ans_raw = resolved_options[0]
                    expl = str((out or {}).get("explanation") or "").strip()
                    return (qid, ans_raw, expl)
                prompt = _build_pair_prompt_one_combined(question_text, sym, items, timeframe)
                out = AI_CLIENT.send_request_with_json_schema(
                    prompt,
                    HEALTH_BOOL_SCHEMA,
                    system_content="You are a precise analyst. Reply only with JSON that matches the schema.",
                    schema_name="fx_bool_answer",
                    model=model_override,
                    provider=provider_override,
                )
                ans_bool = bool((out or {}).get("answer") is True)
                expl = str((out or {}).get("explanation") or "").strip()
                return (qid, ans_bool, expl)

            from concurrent.futures import ThreadPoolExecutor as _TPE
            local_workers = min(8, max(1, len(questions)))
            answers: list[tuple[str, Any, str]] = []
            if questions:
                with _TPE(max_workers=local_workers) as ex:
                    futs = [loop.run_in_executor(ex, _call_one, q) for q in questions]
                    answers = await asyncio.gather(*futs, return_exceptions=False)

            a_map: dict[str, tuple[Any, str]] = {qid: (val, expl) for qid, val, expl in answers}
            ans_struct: list[dict[str, Any]] = []
            for q in questions:
                qid = q.get("id")
                if isinstance(question_schema, dict):
                    default_val = {"position": "BUY", "sl": 0, "tp": 0, "explanation": ""}
                elif answer_type == "choice":
                    default_val: Any = base.upper()
                else:
                    default_val = False
                val, expl = a_map.get(str(qid), (default_val, ""))
                if answer_type == "choice" and isinstance(val, str):
                    val = val.upper()
                ans_struct.append({
                    "id": qid,
                    "answer": val,
                    "explanation": str(expl),
                })

            if isinstance(question_schema, dict):
                buy_count = sum(1 for a in ans_struct if isinstance(a.get("answer"), dict) and str(a["answer"].get("position") or "").upper() == "BUY")
                sell_count = sum(1 for a in ans_struct if isinstance(a.get("answer"), dict) and str(a["answer"].get("position") or "").upper() == "SELL")
                score_value = buy_count - sell_count
                scores_payload = {"BUY": buy_count, "SELL": sell_count, "NET": score_value}
            elif answer_type == "choice":
                base_upper = base.upper()
                quote_upper = quote.upper()
                base_count = sum(1 for a in ans_struct if isinstance(a["answer"], str) and a["answer"].upper() == base_upper)
                quote_count = sum(1 for a in ans_struct if isinstance(a["answer"], str) and a["answer"].upper() == quote_upper)
                score_value = base_count - quote_count
                scores_payload = {"BASE": base_count, "QUOTE": quote_count, "NET": score_value}
            else:
                score_value = sum(1 for a in ans_struct if bool(a["answer"]))
                scores_payload = None

            signal = "NEUTRAL"
            thresholds = strat.get("scoring", {}).get("thresholds", [])
            for th in thresholds:
                try:
                    if int(th.get("min")) <= score_value <= int(th.get("max")):
                        signal = str(th.get("signal") or signal)
                        break
                except Exception:
                    continue

            news_ids = [it.get("url") for it in items if it.get("url")]

            # Compute the newest used news timestamp for metadata (helps freshness without DB lookups)
            def _extract_pub(it):
                v = (it or {}).get("published_at") or (it or {}).get("published") or (it or {}).get("publishedAt")
                return str(v) if v else None
            used_ts_values = [t for t in map(_extract_pub, items) if t]
            latest_used_iso = None
            base_min = base_max = quote_min = quote_max = None
            if used_ts_values:
                try:
                    from datetime import datetime as _dt
                    import re as _re
                    def _parse(v: str):
                        vv = (v or '').strip()
                        if not vv:
                            raise ValueError('empty ts')
                        m = _re.match(r"^(\d{8})T(\d{6})Z$", vv)
                        if m:
                            d,t = m.groups()
                            vv = f"{d[0:4]}-{d[4:6]}-{d[6:8]}T{t[0:2]}:{t[2:4]}:{t[4:6]}+00:00"
                        else:
                            if vv.endswith('Z'):
                                vv = vv[:-1] + '+00:00'
                            if ' ' in vv and 'T' not in vv:
                                vv = vv.replace(' ', 'T')
                        return _dt.fromisoformat(vv)
                    latest_used_iso = max((_parse(x) for x in used_ts_values)).isoformat()
                    # only combined trace here (base/quote splits not used)
                except Exception:
                    latest_used_iso = None
                    base_min = base_max = quote_min = quote_max = None
            # Trace what we used for baseline on this run
            try:
                logger.info(
                    "[health.run.basic] %s items=%d meta.last_used=%s",
                    sym,
                    len(items),
                    latest_used_iso,
                )
            except Exception:
                logger.debug("[health.run.basic] trace logging failed", exc_info=True)

            # Optional final position (BUY/SELL with SL/TP) when strategy defines a position_response_schema
            position_obj = None
            try:
                pos_schema = (strat or {}).get("position_response_schema")
                if isinstance(pos_schema, dict):
                    pos_prompt = _build_pair_position_prompt(sym, items, timeframe)
                    position_obj = AI_CLIENT.send_request_with_json_schema(
                        pos_prompt,
                        pos_schema,
                        system_content="You are a decisive FX analyst. Reply only with JSON that matches the schema.",
                        schema_name="fx_position",
                        model=model_override,
                        provider=provider_override,
                    )
            except Exception:
                position_obj = None

            answers_json = {
                "questions": ans_struct,
                "score": score_value,
                "signal": signal,
                "strategy": strategy_name,
                "group": "basic",
                "scores": scores_payload,
                "meta": {"timeframe": timeframe, "base": base, "quote": quote, "news_count": news_count, "last_used_news_ts": latest_used_iso},
            }
            if position_obj:
                answers_json["position"] = position_obj

            ins = await insert_health_run(
                self.pool,
                kind="forex_pair",
                symbol=sym,
                base_ccy=base,
                quote_ccy=quote,
                news_count=news_count,
                news_ids=news_ids,
                answers_json=answers_json,
            )

            self.set_header("Content-Type", "application/json")
            self.set_header("Cache-Control", "no-store")
            self.finish(
                json.dumps(
                    {
                        "ok": True,
                        "kind": "forex_pair",
                        "symbol": sym,
                        "base": base,
                        "quote": quote,
                        "used_news": items,
                        "answers": ans_struct,
                        "score": score_value,
                        "scores": scores_payload,
                        "signal": signal,
                        "strategy": strategy_name,
                        "position": position_obj,
                        "run_id": ins.get("id"),
                        "created_at": ins.get("created_at").isoformat() if ins.get("created_at") else None,
                    }
                )
            )
            return

        # stock
        symbol = str(payload.get("symbol") or payload.get("ticker") or default_symbol()).upper()
        items = await loop.run_in_executor(EXECUTOR, lambda: fetch_news_for_symbol(symbol, limit=news_count))
        items = items[:news_count]
        # Upsert the used news under the stock symbol
        try:
            combined_items = []
            seen_urls: set[str] = set()
            for it in items:
                u = (it or {}).get("url")
                if not u or u in seen_urls:
                    continue
                seen_urls.add(u)
                row = dict(it)
                row["symbol"] = symbol
                combined_items.append(row)
            if combined_items:
                await upsert_news_articles(self.pool, combined_items)
        except Exception:
            logger.debug("[health] upsert of used stock news failed", exc_info=True)
        allowed_stock = ALLOWED_STRATEGIES.get("stock", set())
        strategy_name = strategy_override if strategy_override and strategy_override in allowed_stock else DEFAULT_STRATEGIES["stock"]
        if strategy_override and strategy_override not in allowed_stock:
            logger.warning("[health] unsupported stock strategy override %s, using default", strategy_override)
        strat = _load_strategy_json(strategy_name)
        if not strat:
            logger.warning("[health] failed to load stock strategy %s, using default", strategy_name)
            strategy_name = DEFAULT_STRATEGIES["stock"]
            strat = _load_strategy_json(strategy_name)
        logger.info("[health] strategy=%s kind=stock symbol=%s news=%d", strategy_name, symbol, news_count)
        questions = [q for q in (strat.get("questions") or []) if isinstance(q, dict)]

        question_schema_stock = strat.get("question_response_schema") if isinstance(strat, dict) else None
        answer_type = _strategy_answer_type(strat)
        use_choice = (answer_type == "choice")
        choice_options = [str(o).strip().upper() for o in (strat.get("answer_options") or ["BULLISH","BEARISH"]) if o]

        def _call_one_stock_bool(qobj: dict) -> tuple[str, bool, str]:
            qid = str(qobj.get("id") or "")
            qtext = str(qobj.get("text") or "")
            prompt = _build_stock_prompt_one(qtext, symbol, items, timeframe)
            out = AI_CLIENT.send_request_with_json_schema(
                prompt,
                HEALTH_BOOL_SCHEMA,
                system_content="You are a precise analyst. Reply only with JSON that matches the schema.",
                schema_name="bool_answer",
                model=model_override,
                provider=provider_override,
            )
            ans = bool((out or {}).get("answer") is True)
            expl = str((out or {}).get("explanation") or "").strip()
            return (qid, ans, expl)

        def _call_one_stock_choice(qobj: dict) -> tuple[str, str, str]:
            qid = str(qobj.get("id") or "")
            qtext = str(qobj.get("text") or "")
            prompt = _build_stock_prompt_choice(qtext, symbol, items, timeframe, choice_options)
            out = AI_CLIENT.send_request_with_json_schema(
                prompt,
                _make_choice_schema(choice_options),
                system_content="You are a decisive analyst. Reply only with JSON that matches the schema.",
                schema_name="stock_choice_answer",
                model=model_override,
                provider=provider_override,
            )
            ans_raw = str((out or {}).get("answer") or "").strip().upper()
            if ans_raw not in choice_options:
                ans_raw = choice_options[0]
            expl = str((out or {}).get("explanation") or "").strip()
            return (qid, ans_raw, expl)

        def _call_one_stock_position(qobj: dict) -> tuple[str, dict, str]:
            qid = str(qobj.get("id") or "")
            qtext = str(qobj.get("text") or "")
            prompt = _build_stock_prompt_position_question(qtext, symbol, items, timeframe)
            out = AI_CLIENT.send_request_with_json_schema(
                prompt,
                question_schema_stock,
                system_content="You are a precise equity analyst. Reply only with JSON that matches the schema.",
                schema_name="stock_question_position",
                model=model_override,
                provider=provider_override,
            )
            return (qid, out, str((out or {}).get("explanation") or ""))

        from concurrent.futures import ThreadPoolExecutor as _TPE
        local_workers = min(8, max(1, len(questions)))
        if questions:
            with _TPE(max_workers=local_workers) as ex:
                if isinstance(question_schema_stock, dict):
                    futs = [loop.run_in_executor(ex, _call_one_stock_position, q) for q in questions]
                elif use_choice:
                    futs = [loop.run_in_executor(ex, _call_one_stock_choice, q) for q in questions]
                else:
                    futs = [loop.run_in_executor(ex, _call_one_stock_bool, q) for q in questions]
                answers = await asyncio.gather(*futs, return_exceptions=False)
        else:
            answers = []

        ans_struct: list[dict[str, Any]] = []
        scores_payload = None
        score_value = 0
        if isinstance(question_schema_stock, dict):
            a_map: dict[str, tuple[dict, str]] = {qid: (val, expl) for qid, val, expl in answers}  # type: ignore
            buy = 0
            sell = 0
            for q in questions:
                qid = str(q.get("id"))
                val, expl = a_map.get(qid, ({"position": "BUY", "sl": 0, "tp": 0, "explanation": ""}, ""))
                pos = str((val or {}).get("position") or "").upper()
                if pos == "BUY":
                    buy += 1
                elif pos == "SELL":
                    sell += 1
                ans_struct.append({"id": qid, "answer": val, "explanation": str(expl)})
            score_value = buy - sell
            scores_payload = {"BUY": buy, "SELL": sell, "NET": score_value}
        elif use_choice:
            a_map: dict[str, tuple[str, str]] = {qid: (val, expl) for qid, val, expl in answers}  # type: ignore
            bullish = 0
            bearish = 0
            for q in questions:
                qid = str(q.get("id"))
                val, expl = a_map.get(qid, (choice_options[0], ""))
                up = str(val).upper()
                if up == "BULLISH":
                    bullish += 1
                elif up == "BEARISH":
                    bearish += 1
                ans_struct.append({"id": qid, "answer": up, "explanation": str(expl)})
            score_value = bullish - bearish
            scores_payload = {"BULLISH": bullish, "BEARISH": bearish, "NET": score_value}
        else:
            a_map_bool: dict[str, tuple[bool, str]] = {qid: (val, expl) for qid, val, expl in answers}  # type: ignore
            for q in questions:
                qid = str(q.get("id"))
                val, expl = a_map_bool.get(qid, (False, ""))
                ans_struct.append({"id": qid, "answer": bool(val), "explanation": str(expl)})
            score_value = sum(1 for a in ans_struct if a.get("answer") is True)

        signal = "NEUTRAL"
        thresholds = strat.get("scoring", {}).get("thresholds", [])
        for th in thresholds:
            try:
                if int(th.get("min")) <= score_value <= int(th.get("max")):
                    signal = str(th.get("signal") or signal)
                    break
            except Exception:
                continue
        news_ids = [it.get("url") for it in items if it.get("url")]
        # Compute newest used news timestamp
        def _extract_pub_stock(it):
            v = (it or {}).get("published_at") or (it or {}).get("published") or (it or {}).get("publishedAt")
            return str(v) if v else None
        used_ts_values_stock = [t for t in map(_extract_pub_stock, items) if t]
        latest_used_iso_stock = None
        if used_ts_values_stock:
            try:
                from datetime import datetime as _dt
                import re as _re
                def _parse2(v: str):
                    vv = (v or '').strip()
                    if not vv:
                        raise ValueError('empty ts')
                    m = _re.match(r"^(\d{8})T(\d{6})Z$", vv)
                    if m:
                        d,t = m.groups()
                        vv = f"{d[0:4]}-{d[4:6]}-{d[6:8]}T{t[0:2]}:{t[2:4]}:{t[4:6]}+00:00"
                    else:
                        if vv.endswith('Z'):
                            vv = vv[:-1] + '+00:00'
                        if ' ' in vv and 'T' not in vv:
                            vv = vv.replace(' ', 'T')
                    return _dt.fromisoformat(vv)
                latest_used_iso_stock = max((_parse2(x) for x in used_ts_values_stock)).isoformat()
            except Exception:
                latest_used_iso_stock = None
        # Trace stock baseline as well
        try:
            logger.info(
                "[health.run.basic.stock] %s items=%d meta.last_used=%s",
                symbol,
                len(items),
                latest_used_iso_stock,
            )
        except Exception:
            logger.debug("[health.run.basic.stock] trace logging failed", exc_info=True)

        # Optional final position (BUY/SELL with SL/TP) when strategy defines a position_response_schema
        position_obj = None
        try:
            pos_schema = (strat or {}).get("position_response_schema")
            if isinstance(pos_schema, dict):
                pos_prompt = _build_stock_position_prompt(symbol, items, timeframe)
                position_obj = AI_CLIENT.send_request_with_json_schema(
                    pos_prompt,
                    pos_schema,
                    system_content="You are a precise equity analyst. Reply only with JSON that matches the schema.",
                    schema_name="stock_position",
                    model=model_override,
                    provider=provider_override,
                )
        except Exception:
            position_obj = None

        answers_json = {
            "questions": ans_struct,
            "score": score_value,
            "signal": signal,
            "strategy": strategy_name,
            "group": "basic",
            "scores": scores_payload,
            "meta": {"timeframe": timeframe, "symbol": symbol, "news_count": news_count, "last_used_news_ts": latest_used_iso_stock},
        }
        if position_obj:
            answers_json["position"] = position_obj
        ins = await insert_health_run(
            self.pool,
            kind="stock",
            symbol=symbol,
            base_ccy=None,
            quote_ccy=None,
            news_count=news_count,
            news_ids=news_ids,
            answers_json=answers_json,
        )

        self.set_header("Content-Type", "application/json")
        self.set_header("Cache-Control", "no-store")
        self.finish(
            json.dumps(
                {
                    "ok": True,
                    "kind": "stock",
                    "symbol": symbol,
                    "used_news": items,
                    "answers": ans_struct,
                    "score": score_value,
                    "scores": scores_payload,
                    "signal": signal,
                    "strategy": strategy_name,
                    "position": position_obj,
                    "run_id": ins.get("id"),
                    "created_at": ins.get("created_at").isoformat() if ins.get("created_at") else None,
                }
            )
        )


class TradePlanHandler(tornado.web.RequestHandler):
    def initialize(self, pool):
        self.pool = pool

    def _load_trade_prompts(self) -> dict[str, str]:
        root = Path(__file__).resolve().parents[1]
        path = root / "strategies" / "llm" / "ai_trade_plan_prompts.json"
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    async def post(self):
        global AI_CLIENT
        if AI_CLIENT is None:
            self.set_status(503)
            self.set_header("Content-Type", "application/json")
            self.finish(json.dumps({"ok": False, "error": "LLM unavailable"}))
            return
        try:
            payload = json.loads(self.request.body or "{}")
        except Exception:
            payload = {}
        symbol = str(payload.get("symbol") or payload.get("ticker") or default_symbol()).upper()
        timeframe = str(payload.get("timeframe") or payload.get("tf") or "H1").upper()
        action = str(payload.get("action") or payload.get("side") or "").upper()
        leverage = float(payload.get("leverage") or 10)
        snapshot_text = str(payload.get("tech_snapshot") or "").strip()
        if action not in {"BUY", "SELL"}:
            self.set_status(400)
            self.finish(json.dumps({"ok": False, "error": "action must be BUY or SELL"}))
            return
        if not snapshot_text:
            self.set_status(400)
            self.finish(json.dumps({"ok": False, "error": "tech_snapshot required"}))
            return

        # Compose Basic and Tech+AI blocks from latest runs
        kind = "forex_pair" if _is_fx_symbol(symbol) else "stock"
        base = quote = None
        if kind == "forex_pair":
            s = symbol
            if len(s) >= 6:
                base, quote = s[:3], s[3:6]
        # Determine default strategy for basic
        if kind == "forex_pair":
            # metals vs non-metals
            if base in {"XAU", "XAG"}:
                basic_strategy = "metal_pair_compact_10q.json"
            else:
                basic_strategy = "forex_pair_compact_10q.json"
        else:
            basic_strategy = "stocks_compact_10q.json"

        async def _latest_run(strategy: str) -> dict | None:
            if kind == "forex_pair":
                runs = await list_health_runs(self.pool, kind="forex_pair", base_ccy=base, quote_ccy=quote, limit=1, offset=0, strategy=strategy)
            else:
                runs = await list_health_runs(self.pool, kind="stock", symbol=symbol, limit=1, offset=0, strategy=strategy)
            return runs[0] if runs else None

        basic_run = await _latest_run(basic_strategy)
        tech_run = await _latest_run("tech_snapshot_10q.json")

        # Ensure prerequisite reports exist: if missing, trigger them via the same API
        # so they are persisted to history just like a frontend click.
        if basic_run is None or tech_run is None:
            try:
                client = AsyncHTTPClient()
                base_url = f"{self.request.protocol}://{self.request.host}"
                url = base_url + "/api/health/run"
                # Run Basic health if absent
                if basic_run is None:
                    basic_payload: dict[str, Any] = {
                        "kind": kind,
                        "symbol": symbol,
                        "strategy": basic_strategy,
                        # keep defaults for news_count/timeframe; server will pick sensible values
                    }
                    req = HTTPRequest(url, method="POST", headers={"Content-Type": "application/json"}, body=json.dumps(basic_payload))
                    await client.fetch(req, raise_error=False)
                # Run Tech+AI snapshot (requires snapshot text) if absent
                if tech_run is None and snapshot_text:
                    tech_payload: dict[str, Any] = {
                        "kind": kind,
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "strategy": "tech_snapshot_10q.json",
                        "tech_snapshot": snapshot_text,
                    }
                    req2 = HTTPRequest(url, method="POST", headers={"Content-Type": "application/json"}, body=json.dumps(tech_payload))
                    await client.fetch(req2, raise_error=False)
            except Exception:
                logger.debug("failed to auto-run basic/tech reports before trade plan", exc_info=True)
            # Requery after attempted creation
            basic_run = await _latest_run(basic_strategy)
            tech_run = await _latest_run("tech_snapshot_10q.json")

        def _format_run_block(run: dict | None) -> str:
            if not run:
                return "(no recent run)"
            ans = run.get("answers_json") or {}
            score = ans.get("score")
            signal = ans.get("signal")
            strategy = ans.get("strategy") or ""
            scores = ans.get("scores") or {}
            parts = []
            parts.append(f"Score: {score}")
            if signal:
                parts.append(str(signal))
            if strategy:
                parts.append(f"Strategy: {strategy}")
            # counts line
            counts = []
            if "BASE" in scores and "QUOTE" in scores and base and quote:
                counts.append(f"{base}={scores['BASE']}")
                counts.append(f"{quote}={scores['QUOTE']}")
            if "BULLISH" in scores or "BEARISH" in scores:
                if "BULLISH" in scores:
                    counts.append(f"BULLISH={scores['BULLISH']}")
                if "BEARISH" in scores:
                    counts.append(f"BEARISH={scores['BEARISH']}")
            if "NET" in scores:
                counts.append(f"NET={scores['NET']}")
            if counts:
                parts.append(" ".join(["•".join(counts)]) if False else " ".join([" • ".join(counts)]))
            # enumerate answers
            qlist = ans.get("questions") or []
            lines = []
            for i, q in enumerate(qlist, 1):
                aval = q.get("answer")
                expl = q.get("explanation") or ""
                lines.append(f"{i}.\n{str(aval).upper()}\n{expl}")
            return "\n".join(parts + lines)

        basic_block = _format_run_block(basic_run)
        tech_block = _format_run_block(tech_run)

        # Build final prompt
        prompts = self._load_trade_prompts()
        template_key = "buy_prompt" if action == "BUY" else "sell_prompt"
        template = prompts.get(template_key) or ""
        if not template:
            self.set_status(500)
            self.finish(json.dumps({"ok": False, "error": "trade prompt template missing"}))
            return
        prompt = (
            template
            .replace("{{SYMBOL}}", symbol)
            .replace("{{TF}}", timeframe)
            .replace("{{BASIC_HEALTH_BLOCK}}", basic_block)
            .replace("{{TECH_AI_BLOCK}}", tech_block)
            .replace("{{TECH_SNAPSHOT_BLOCK}}", snapshot_text)
        )

        # Call AI
        # Optional model/provider override (only for trade plans)
        model = None
        provider = None
        try:
            req = json.loads(self.request.body or b"{}")
            model = str((req or {}).get("model") or "").strip() or None
            provider = str((req or {}).get("provider") or "").strip().lower() or None
        except Exception:
            model = None
            provider = None
        # Infer provider from model when not explicitly provided
        if not provider and model:
            low = model.lower()
            if low.startswith("deepseek"):
                provider = "deepseek"
            else:
                provider = "openai"
        try:
            out = await tornado.ioloop.IOLoop.current().run_in_executor(
                EXECUTOR,
                lambda: AI_CLIENT.send_request_with_json_schema(
                    prompt,
                    TRADE_PLAN_SCHEMA,
                    system_content="You are a disciplined trading assistant. Reply only with JSON matching the schema.",
                    schema_name="trade_plan",
                    model=model,
                    provider=provider,
                ),
            )
        except Exception as exc:
            self.set_status(502)
            self.finish(json.dumps({"ok": False, "error": str(exc)}))
            return

        # Normalize and enforce loss cap
        plan = out or {}
        position = str(plan.get("position") or action).upper()
        sl = float(plan.get("stop_loss") or 0)
        tp = float(plan.get("take_profit") or 0)
        explanation = str(plan.get("explanation") or "")

        # Reference price = latest close
        rows = await fetch_ohlc_bars(self.pool, symbol, timeframe, 1)
        ref_price = float(rows[-1]["close"]) if rows else 0.0
        max_loss_pct = 0.20 / max(1.0, float(leverage or 10.0))
        enforced = False
        if ref_price > 0 and sl > 0 and max_loss_pct > 0:
            if position == "BUY":
                min_sl = ref_price * (1.0 - max_loss_pct)
                if sl < min_sl:
                    sl = min_sl
                    enforced = True
            elif position == "SELL":
                max_sl = ref_price * (1.0 + max_loss_pct)
                if sl > max_sl:
                    sl = max_sl
                    enforced = True

        # Persist plan as a health_run record (strategy-tagged)
        try:
            kind = "forex_pair" if _is_fx_symbol(symbol) else "stock"
            base_ccy = symbol[:3] if kind == "forex_pair" else None
            quote_ccy = symbol[3:6] if kind == "forex_pair" else None
            answers_json = {
                "strategy": "ai_trade_plan",
                "group": "plan",
                "plan": {
                    "position": position,
                    "stop_loss": sl,
                    "take_profit": tp,
                    "explanation": explanation,
                },
                "meta": {
                    "timeframe": timeframe,
                    "symbol": symbol,
                    "action": action,
                    "leverage": leverage,
                    "ref_price": ref_price,
                    "max_loss_pct": max_loss_pct,
                    "enforced": enforced,
                },
            }
            ins = await insert_health_run(
                self.pool,
                kind=kind,
                symbol=(symbol if kind == "stock" else f"{base_ccy}{quote_ccy}"),
                base_ccy=base_ccy,
                quote_ccy=quote_ccy,
                news_count=0,
                news_ids=[],
                answers_json=answers_json,
            )
            run_id = ins.get("id")
            created_at = ins.get("created_at").isoformat() if ins.get("created_at") else None
        except Exception:
            run_id = None
            created_at = None

        self.set_header("Content-Type", "application/json")
        self.set_header("Cache-Control", "no-store")
        self.finish(json.dumps({
            "ok": True,
            "symbol": symbol,
            "timeframe": timeframe,
            "action": action,
            "leverage": leverage,
            "ref_price": ref_price,
            "max_loss_pct": max_loss_pct,
            "enforced": enforced,
            "plan": {
                "position": position,
                "stop_loss": sl,
                "take_profit": tp,
                "explanation": explanation,
            },
            "run_id": run_id,
            "created_at": created_at,
        }))
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

    # Account balance polling (default every 60 min)
    try:
        balance_min = int(os.getenv("BALANCE_POLL_MIN", "60"))
    except Exception:
        balance_min = 60
    def _schedule_balance_poll():
        tornado.ioloop.IOLoop.current().add_callback(poll_and_store_account_balance)
    global BALANCE_CB
    if BALANCE_CB is None:
        BALANCE_CB = tornado.ioloop.PeriodicCallback(_schedule_balance_poll, max(5, balance_min) * 60 * 1000)
        BALANCE_CB.start()

    # Closed orders update signal (default every 30 min)
    try:
        closed_min = int(os.getenv("CLOSED_ORDERS_POLL_MIN", "30"))
    except Exception:
        closed_min = 30
    def _schedule_closed_emit():
        tornado.ioloop.IOLoop.current().add_callback(emit_closed_deals_event)
    global CLOSED_ORDERS_CB
    if CLOSED_ORDERS_CB is None:
        CLOSED_ORDERS_CB = tornado.ioloop.PeriodicCallback(_schedule_closed_emit, max(1, closed_min) * 60 * 1000)
        CLOSED_ORDERS_CB.start()

    # Auto news backfill (default on)
    try:
        news_auto_env = os.getenv("AUTO_NEWS_BACKFILL", "1").lower() not in ("0", "false", "no", "off")
        interval_min = int(os.getenv("NEWS_BACKFILL_MIN", "30"))
    except Exception:
        news_auto_env = True
        interval_min = 30
    def _schedule_news_backfill():
        tornado.ioloop.IOLoop.current().add_callback(run_news_backfill)
    global NEWS_BACKFILL_CB
    if news_auto_env:
        # Align to real time (:00 and :30 when interval=30)
        schedule_news_backfill_aligned(max(1, interval_min))

    # Start IOLoop (blocking)
    loop.start()


if __name__ == "__main__":
    main()
