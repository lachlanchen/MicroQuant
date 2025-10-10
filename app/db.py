import os
from pathlib import Path
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

