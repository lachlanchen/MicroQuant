import os
import json
import logging
import asyncio
from functools import partial
from datetime import datetime, timezone, timedelta
from concurrent.futures import ThreadPoolExecutor

import tornado.ioloop
import tornado.web
from tornado.websocket import WebSocketHandler
from dotenv import load_dotenv

from app.db import create_pool, init_schema, upsert_ohlc_bars, fetch_ohlc_bars, set_pref, get_pref, latest_bar_ts, set_prefs, get_prefs
from app.mt5_client import client as mt5_client
from app.strategy import crossover_strategy
from app.news_fetcher import fetch_news_for_symbol


EXECUTOR = ThreadPoolExecutor(max_workers=2)
logger = logging.getLogger("mt5app")

WS_CLIENTS: set = set()


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


ALL_TIMEFRAMES = ["M1", "M5", "M15", "M30", "H1", "H4", "D1"]
PREF_KEYS = ["last_symbol", "last_tf", "last_count", "chart_type", "last_volume", "last_sl", "last_tp", "last_fast", "last_slow"]

def _default_backfill_days(tf: str) -> int:
    tf = (tf or "").upper()
    if tf.startswith("D"):
        return 2000
    if tf.startswith("H"):
        return 365
    return 30


def schedule_symbol_backfill(pool, symbol: str, *, timeframes: list[str] | None = None):
    """Kick off a lightweight background job to enrich history for a symbol across timeframes."""
    tfs = timeframes or ALL_TIMEFRAMES
    loop = tornado.ioloop.IOLoop.current()
    logger.info("[backfill] scheduling %s across %d timeframes", symbol, len(tfs))

    async def _runner():
        now = datetime.now(timezone.utc)
        for tf in tfs:
            try:
                days = _default_backfill_days(tf)
                since = now - timedelta(days=days)
                fetch_fn = partial(mt5_client.fetch_bars_since, symbol, tf, since)
                bars = await loop.run_in_executor(EXECUTOR, fetch_fn)
                if bars:
                    inserted = await upsert_ohlc_bars(pool, bars)
                    logger.info("[backfill] %s %s +%d bars (inserted=%d)", symbol, tf, len(bars), inserted)
                    await emit_fetch_event(
                        symbol=symbol,
                        timeframe=tf,
                        mode="backfill",
                        fetch_mode="since",
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
                        fetch_mode="since",
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
                    fetch_mode="since",
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
        if mode == "inc":
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
        or "XAUUSD, XAGUSD, EURUSD, GBPUSD, USDJPY, USDCHF, USDCAD, AUDUSD, NZDUSD, MSFT, NVDA, TSLA, AAPL, AMZN, GOOGL"
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
                extras = await get_prefs(pool, ["last_count", "chart_type", "last_volume", "last_sl", "last_tp", "last_fast", "last_slow"])
            except Exception:
                extras = {}
                logger.debug("no prefs yet for last_symbol/last_tf")

        sym = (last_sym or default_symbol()).upper()
        if sym not in SUPPORTED_SYMBOLS:
            sym = default_symbol()
        tf = (last_tf or "H1").upper()
        if tf not in ("M1","M5","M15","M30","H1","H4","D1"):
            tf = "H1"
        extras = extras or {}
        count_pref = extras.get("last_count") or "500"
        chart_pref = (extras.get("chart_type") or "candlestick").lower()
        volume_pref = extras.get("last_volume") or "0.10"
        sl_pref = extras.get("last_sl") or ""
        tp_pref = extras.get("last_tp") or ""
        fast_pref = extras.get("last_fast") or "20"
        slow_pref = extras.get("last_slow") or "50"

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
            (r"/api/news", NewsHandler),
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
            items = await loop.run_in_executor(EXECUTOR, lambda: fetch_news_for_symbol(symbol, limit=25))
            self.set_header("Content-Type", "application/json")
            self.set_header("Cache-Control", "no-store")
            self.finish(json.dumps({"ok": True, "symbol": symbol, "items": items}))
        except Exception as e:
            self.set_status(500)
            self.set_header("Content-Type", "application/json")
            self.set_header("Cache-Control", "no-store")
            self.finish(json.dumps({"ok": False, "error": str(e), "items": []}))


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








