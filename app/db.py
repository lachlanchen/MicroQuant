import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Iterable, Mapping
import asyncpg


def get_db_url() -> str:
    # Prefer a generic DATABASE_URL if set, else fall back to DATABASE_MT_URL
    return (
        os.getenv("DATABASE_URL")
        or os.getenv("DATABASE_MT_URL")
        or os.getenv("DATABASE_QT_URL")
        or ""
    )


async def create_pool() -> asyncpg.pool.Pool:
    db_url = get_db_url()
    if not db_url:
        raise RuntimeError(
            "DATABASE_URL or DATABASE_MT_URL not set. Export one before starting the app."
        )
    return await asyncpg.create_pool(dsn=db_url, min_size=1, max_size=5)


async def init_schema(pool: asyncpg.pool.Pool) -> None:
    root = Path(__file__).resolve().parents[1]
    schema_path = root / "sql" / "schema.sql"
    sql = schema_path.read_text(encoding="utf-8")
    async with pool.acquire() as conn:
        await conn.execute(sql)


async def upsert_ohlc_bars(pool: asyncpg.pool.Pool, rows: list[dict]) -> int:
    if not rows:
        return 0
    # rows: [{symbol, timeframe, ts, open, high, low, close, tick_volume, spread, real_volume}]
    q = (
        """
        INSERT INTO ohlc_bars
            (symbol, timeframe, ts, open, high, low, close, tick_volume, spread, real_volume)
        VALUES
            ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        ON CONFLICT (symbol, timeframe, ts) DO UPDATE SET
            open = EXCLUDED.open,
            high = EXCLUDED.high,
            low = EXCLUDED.low,
            close = EXCLUDED.close,
            tick_volume = EXCLUDED.tick_volume,
            spread = EXCLUDED.spread,
            real_volume = EXCLUDED.real_volume
        """
    )
    args = [
        (
            r["symbol"],
            r["timeframe"],
            r["ts"],
            r["open"],
            r["high"],
            r["low"],
            r["close"],
            r.get("tick_volume"),
            r.get("spread"),
            r.get("real_volume"),
        )
        for r in rows
    ]
    async with pool.acquire() as conn:
        await conn.executemany(q, args)
    return len(rows)


async def fetch_ohlc_bars(
    pool: asyncpg.pool.Pool, symbol: str, timeframe: str, limit: int = 500
) -> list[dict]:
    q = (
        """
        SELECT symbol, timeframe, ts, open, high, low, close, tick_volume, spread, real_volume
        FROM ohlc_bars
        WHERE symbol = $1 AND timeframe = $2
        ORDER BY ts DESC
        LIMIT $3
        """
    )
    async with pool.acquire() as conn:
        rows = await conn.fetch(q, symbol, timeframe, limit)
    # Return in ascending time for plotting
    result = [dict(r) for r in reversed(rows)]
    # Convert Decimal to float for JSON friendliness
    for r in result:
        for k in ("open", "high", "low", "close"):
            v = r[k]
            if v is not None:
                r[k] = float(v)
        r["ts"] = r["ts"].isoformat()
    return result


async def latest_bar_ts(pool: asyncpg.pool.Pool, symbol: str, timeframe: str):
    """Return the most recent timestamp we have for a symbol/timeframe, or None."""
    q = "SELECT ts FROM ohlc_bars WHERE symbol=$1 AND timeframe=$2 ORDER BY ts DESC LIMIT 1"
    async with pool.acquire() as conn:
        val = await conn.fetchval(q, symbol, timeframe)
    return val

async def set_pref(pool: asyncpg.pool.Pool, key: str, value: str) -> None:
    q = (
        """
        INSERT INTO app_prefs(key, value)
        VALUES($1, $2)
        ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
        """
    )
    async with pool.acquire() as conn:
        await conn.execute(q, key, value)


async def get_pref(pool: asyncpg.pool.Pool, key: str) -> str | None:
    q = "SELECT value FROM app_prefs WHERE key=$1"
    async with pool.acquire() as conn:
        val = await conn.fetchval(q, key)
    return val

async def get_prefs(pool: asyncpg.pool.Pool, keys: Iterable[str]) -> dict[str, str]:
    key_list = [k for k in keys if k]
    if not key_list:
        return {}
    q = "SELECT key, value FROM app_prefs WHERE key = ANY($1::text[])"
    async with pool.acquire() as conn:
        rows = await conn.fetch(q, key_list)
    return {row["key"]: row["value"] for row in rows}


async def set_prefs(pool: asyncpg.pool.Pool, mapping: Mapping[str, str]) -> None:
    if not mapping:
        return
    q = (
        """
        INSERT INTO app_prefs(key, value)
        VALUES($1, $2)
        ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
        """
    )
    async with pool.acquire() as conn:
        async with conn.transaction():
            for key, value in mapping.items():
                await conn.execute(q, key, value)


async def ohlc_range(pool: asyncpg.pool.Pool, symbol: str, timeframe: str) -> dict | None:
    """Return earliest, latest, and count for stored OHLC data."""
    q = """
        SELECT MIN(ts) AS start_ts, MAX(ts) AS end_ts, COUNT(*)::BIGINT AS rows_count
        FROM ohlc_bars
        WHERE symbol=$1 AND timeframe=$2
    """
    async with pool.acquire() as conn:
        row = await conn.fetchrow(q, symbol, timeframe)
    if not row or row["rows_count"] == 0:
        return None
    start_ts = row["start_ts"]
    end_ts = row["end_ts"]
    if start_ts and start_ts.tzinfo is None:
        start_ts = start_ts.replace(tzinfo=timezone.utc)
    if end_ts and end_ts.tzinfo is None:
        end_ts = end_ts.replace(tzinfo=timezone.utc)
    return {
        "start_ts": start_ts,
        "end_ts": end_ts,
        "rows_count": int(row["rows_count"]),
    }


async def fetch_ohlc_bars_range(
    pool: asyncpg.pool.Pool,
    symbol: str,
    timeframe: str,
    *,
    start_ts: datetime | None = None,
    end_ts: datetime | None = None,
) -> list[dict]:
    """Fetch bars within an optional timestamp range (ascending)."""
    q = (
        """
        SELECT symbol, timeframe, ts, open, high, low, close, tick_volume, spread, real_volume
        FROM ohlc_bars
        WHERE symbol = $1
          AND timeframe = $2
          AND ($3::timestamptz IS NULL OR ts >= $3)
          AND ($4::timestamptz IS NULL OR ts <= $4)
        ORDER BY ts ASC
        """
    )
    async with pool.acquire() as conn:
        rows = await conn.fetch(q, symbol, timeframe, start_ts, end_ts)
    result = []
    for rec in rows:
        row = dict(rec)
        row["ts"] = (rec["ts"].isoformat() if isinstance(rec["ts"], datetime) else str(rec["ts"]))
        for key in ("open", "high", "low", "close"):
            val = row[key]
            if val is not None:
                row[key] = float(val)
        result.append(row)
    return result


async def create_stl_run(
    pool: asyncpg.pool.Pool,
    *,
    symbol: str,
    timeframe: str,
    period: int,
    start_ts: datetime,
    end_ts: datetime,
    rows_count: int,
) -> dict:
    q = """
        INSERT INTO stl_runs (symbol, timeframe, period, start_ts, end_ts, rows_count)
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING id, created_at
    """
    async with pool.acquire() as conn:
        row = await conn.fetchrow(q, symbol, timeframe, period, start_ts, end_ts, rows_count)
    created_at = row["created_at"]
    if created_at and created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    return {"id": row["id"], "created_at": created_at}


async def insert_stl_components(
    pool: asyncpg.pool.Pool,
    run_id: int,
    rows: list[dict],
) -> int:
    if not rows:
        return 0
    q = (
        """
        INSERT INTO stl_run_components (run_id, ts, close, trend, seasonal, resid)
        VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (run_id, ts) DO UPDATE SET
            close = EXCLUDED.close,
            trend = EXCLUDED.trend,
            seasonal = EXCLUDED.seasonal,
            resid = EXCLUDED.resid
        """
    )
    args = []
    for rec in rows:
        ts = rec["ts"]
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts)
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        args.append(
            (
                run_id,
                ts,
                rec.get("close"),
                rec.get("trend"),
                rec.get("seasonal"),
                rec.get("resid"),
            )
        )
    async with pool.acquire() as conn:
        await conn.executemany(q, args)
    return len(rows)


async def list_stl_runs(pool: asyncpg.pool.Pool, symbol: str, timeframe: str) -> list[dict]:
    q = """
        SELECT id, symbol, timeframe, period, start_ts, end_ts, rows_count, created_at
        FROM stl_runs
        WHERE symbol=$1 AND timeframe=$2
        ORDER BY created_at DESC
    """
    async with pool.acquire() as conn:
        rows = await conn.fetch(q, symbol, timeframe)
    result = []
    for rec in rows:
        start_ts = rec["start_ts"]
        end_ts = rec["end_ts"]
        created_at = rec["created_at"]
        if start_ts and start_ts.tzinfo is None:
            start_ts = start_ts.replace(tzinfo=timezone.utc)
        if end_ts and end_ts.tzinfo is None:
            end_ts = end_ts.replace(tzinfo=timezone.utc)
        if created_at and created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        result.append(
            {
                "id": rec["id"],
                "symbol": rec["symbol"],
                "timeframe": rec["timeframe"],
                "period": rec["period"],
                "start_ts": start_ts,
                "end_ts": end_ts,
                "rows_count": rec["rows_count"],
                "created_at": created_at,
            }
        )
    return result


async def get_stl_run(pool: asyncpg.pool.Pool, run_id: int) -> dict | None:
    q = """
        SELECT id, symbol, timeframe, period, start_ts, end_ts, rows_count, created_at
        FROM stl_runs
        WHERE id=$1
    """
    async with pool.acquire() as conn:
        rec = await conn.fetchrow(q, run_id)
    if not rec:
        return None
    start_ts = rec["start_ts"]
    end_ts = rec["end_ts"]
    created_at = rec["created_at"]
    if start_ts and start_ts.tzinfo is None:
        start_ts = start_ts.replace(tzinfo=timezone.utc)
    if end_ts and end_ts.tzinfo is None:
        end_ts = end_ts.replace(tzinfo=timezone.utc)
    if created_at and created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    return {
        "id": rec["id"],
        "symbol": rec["symbol"],
        "timeframe": rec["timeframe"],
        "period": rec["period"],
        "start_ts": start_ts,
        "end_ts": end_ts,
        "rows_count": rec["rows_count"],
        "created_at": created_at,
    }


async def delete_stl_run(pool: asyncpg.pool.Pool, run_id: int) -> int:
    q = "DELETE FROM stl_runs WHERE id=$1"
    async with pool.acquire() as conn:
        result = await conn.execute(q, run_id)
    # result like 'DELETE 0/1'
    return int(result.split()[-1])


async def fetch_stl_run_data(pool: asyncpg.pool.Pool, run_id: int) -> dict | None:
    run = await get_stl_run(pool, run_id)
    if not run:
        return None
    q = """
        SELECT ts, close, trend, seasonal, resid
        FROM stl_run_components
        WHERE run_id=$1
        ORDER BY ts ASC
    """
    async with pool.acquire() as conn:
        rows = await conn.fetch(q, run_id)
    data = []
    for rec in rows:
        ts = rec["ts"]
        if isinstance(ts, datetime):
            ts = ts.isoformat()
        row = {
            "ts": ts,
            "close": float(rec["close"]) if rec["close"] is not None else None,
            "trend": float(rec["trend"]) if rec["trend"] is not None else None,
            "seasonal": float(rec["seasonal"]) if rec["seasonal"] is not None else None,
            "resid": float(rec["resid"]) if rec["resid"] is not None else None,
        }
        data.append(row)
    return {"run": run, "rows": data}



async def upsert_news_articles(pool: asyncpg.pool.Pool, rows: list[dict]) -> int:
    if not rows:
        return 0
    q = (
        """
        INSERT INTO news_articles (symbol, url, title, source, site, image, published_at, summary, body)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        ON CONFLICT (symbol, url) DO UPDATE SET
            title = EXCLUDED.title,
            source = EXCLUDED.source,
            site = EXCLUDED.site,
            image = EXCLUDED.image,
            published_at = COALESCE(EXCLUDED.published_at, news_articles.published_at),
            summary = EXCLUDED.summary,
            body = EXCLUDED.body
        """
    )
    args = []
    for r in rows:
        pub = r.get("published_at") or r.get("published") or r.get("publishedAt")
        if isinstance(pub, str):
            try:
                pub_dt = datetime.fromisoformat(pub)
            except Exception:
                pub_dt = None
        else:
            pub_dt = pub
        if pub_dt is not None and pub_dt.tzinfo is None:
            pub_dt = pub_dt.replace(tzinfo=timezone.utc)
        args.append(
            (
                r.get("symbol"),
                r.get("url"),
                r.get("title"),
                r.get("source") or r.get("publisher"),
                r.get("site"),
                r.get("image"),
                pub_dt,
                r.get("summary"),
                r.get("body") or r.get("text") or "",
            )
        )
    async with pool.acquire() as conn:
        await conn.executemany(q, args)
    return len(rows)


async def fetch_news_db(
    pool: asyncpg.pool.Pool,
    symbol: str,
    *,
    since: datetime | None = None,
    limit: int = 25,
) -> list[dict]:
    q = (
        """
        SELECT symbol, url, title, source, site, image, published_at, summary, body
        FROM news_articles
        WHERE symbol = $1
          AND ($2::timestamptz IS NULL OR published_at >= $2)
        ORDER BY published_at DESC NULLS LAST, id DESC
        LIMIT $3
        """
    )
    async with pool.acquire() as conn:
        rows = await conn.fetch(q, symbol, since, limit)
    out: list[dict] = []
    for r in rows:
        item = dict(r)
        pub = item.get("published_at")
        if pub and hasattr(pub, "isoformat"):
            item["publishedAt"] = pub.isoformat()
        out.append(item)
    return out

async def insert_health_run(
    pool: asyncpg.pool.Pool,
    *,
    kind: str,
    symbol: str | None,
    base_ccy: str | None,
    quote_ccy: str | None,
    news_count: int,
    news_ids: list[str],
    answers_json: dict,
) -> dict:
    q = (
        """
        INSERT INTO health_runs (kind, symbol, base_ccy, quote_ccy, news_count, news_ids, answers_json)
        VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb)
        RETURNING id, created_at
        """
    )
    # Ensure JSONB receives a serialized string for compatibility
    import json as _json
    answers_str = _json.dumps(answers_json, ensure_ascii=False)
    async with pool.acquire() as conn:
        row = await conn.fetchrow(q, kind, symbol, base_ccy, quote_ccy, int(news_count), news_ids, answers_str)
    created_at = row["created_at"]
    if created_at and created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    return {"id": row["id"], "created_at": created_at}


async def list_health_runs(
    pool: asyncpg.pool.Pool,
    *,
    kind: str,
    symbol: str | None = None,
    base_ccy: str | None = None,
    quote_ccy: str | None = None,
    limit: int = 5,
    offset: int = 0,
) -> list[dict]:
    if limit <= 0:
        limit = 5
    if offset < 0:
        offset = 0
    if (kind or "").lower() == "stock":
        q = (
            """
            SELECT id, kind, symbol, base_ccy, quote_ccy, news_count, news_ids, answers_json, created_at
            FROM health_runs
            WHERE kind=$1 AND symbol=$2
            ORDER BY created_at DESC
            LIMIT $3 OFFSET $4
            """
        )
        args = (kind, symbol, limit, offset)
    else:
        q = (
            """
            SELECT id, kind, symbol, base_ccy, quote_ccy, news_count, news_ids, answers_json, created_at
            FROM health_runs
            WHERE kind=$1 AND base_ccy=$2 AND quote_ccy=$3
            ORDER BY created_at DESC
            LIMIT $4 OFFSET $5
            """
        )
        args = (kind, base_ccy, quote_ccy, limit, offset)
    async with pool.acquire() as conn:
        rows = await conn.fetch(q, *args)
    result: list[dict] = []
    for rec in rows:
        created_at = rec["created_at"]
        if created_at and created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        # Normalize JSON field to dict
        ans = rec["answers_json"]
        try:
            if isinstance(ans, str):
                import json as _json
                ans = _json.loads(ans)
        except Exception:
            pass
        result.append(
            {
                "id": rec["id"],
                "kind": rec["kind"],
                "symbol": rec["symbol"],
                "base_ccy": rec["base_ccy"],
                "quote_ccy": rec["quote_ccy"],
                "news_count": rec["news_count"],
                "news_ids": list(rec["news_ids"] or []),
                "answers_json": ans,
                "created_at": created_at,
            }
        )
    return result
