import os
import logging
from datetime import datetime, timezone
from typing import Optional

try:
    import MetaTrader5 as mt5
except Exception as e:  # pragma: no cover
    mt5 = None
    _mt5_import_error = e
else:
    _mt5_import_error = None


TF_MAP = {
    "M1": getattr(mt5, "TIMEFRAME_M1", 1) if mt5 else 1,
    "M5": getattr(mt5, "TIMEFRAME_M5", 5) if mt5 else 5,
    "M15": getattr(mt5, "TIMEFRAME_M15", 15) if mt5 else 15,
    "M30": getattr(mt5, "TIMEFRAME_M30", 30) if mt5 else 30,
    "H1": getattr(mt5, "TIMEFRAME_H1", 60) if mt5 else 60,
    "H4": getattr(mt5, "TIMEFRAME_H4", 240) if mt5 else 240,
    "D1": getattr(mt5, "TIMEFRAME_D1", 1440) if mt5 else 1440,
    "W1": getattr(mt5, "TIMEFRAME_W1", 10080) if mt5 else 10080,
    "MN1": getattr(mt5, "TIMEFRAME_MN1", 43200) if mt5 else 43200,
}


class MT5Client:
    def __init__(self) -> None:
        self.initialized = False
        self.logger = logging.getLogger("mt5app.mt5")

    def initialize(self) -> None:
        if mt5 is None:
            raise RuntimeError(
                f"MetaTrader5 package not available: {_mt5_import_error}"
            )

        path = os.getenv("MT5_PATH") or None
        self.logger.info("mt5.initialize path=%r", path)
        if not mt5.initialize(path=path):
            code, msg = mt5.last_error()
            raise RuntimeError(
                f"mt5.initialize failed: {code} {msg} (MT5_PATH={path!r})"
            )

        login = os.getenv("MT5_LOGIN")
        password = os.getenv("MT5_PASSWORD")
        server = os.getenv("MT5_SERVER")
        # If login details provided, attempt login; otherwise rely on running terminal session
        if login and password:
            self.logger.info("mt5.login account=%s server=%r", login, server)
            # Call without server when it's not provided; some builds treat None as invalid
            if server:
                ok = mt5.login(int(login), password=password, server=server)
            else:
                ok = mt5.login(int(login), password=password)
            if not ok:
                code, msg = mt5.last_error()
                raise RuntimeError(f"mt5.login failed: {code} {msg}")

        self.initialized = True

    def fetch_bars(self, symbol: str, timeframe: str, count: int = 500) -> list[dict]:
        if not self.initialized:
            self.initialize()

        if timeframe not in TF_MAP:
            raise ValueError(f"Unsupported timeframe: {timeframe}")
        tf = TF_MAP[timeframe]

        # Ensure symbol is available
        self.logger.debug("symbol_select %s", symbol)
        mt5.symbol_select(symbol, True)

        self.logger.info("copy_rates_from_pos symbol=%s tf=%s count=%s", symbol, timeframe, count)
        rates = mt5.copy_rates_from_pos(symbol, tf, 0, int(count))
        if rates is None:
            code, msg = mt5.last_error()
            raise RuntimeError(f"copy_rates_from_pos failed: {code} {msg}")

        # rates is a numpy structured array; fields are accessible via indexing, not .get
        names = set(getattr(rates, "dtype", None).names or [])
        out = []
        for r in rates:
            ts = datetime.fromtimestamp(int(r["time"]), tz=timezone.utc)
            tick_volume = int(r["tick_volume"]) if "tick_volume" in names else 0
            spread = int(r["spread"]) if "spread" in names else 0
            real_volume = int(r["real_volume"]) if "real_volume" in names else 0
            out.append(
                {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "ts": ts,
                    "open": float(r["open"]),
                    "high": float(r["high"]),
                    "low": float(r["low"]),
                    "close": float(r["close"]),
                    "tick_volume": tick_volume,
                    "spread": spread,
                    "real_volume": real_volume,
                }
            )
        return out

    def fetch_bars_since(self, symbol: str, timeframe: str, since_dt) -> list[dict]:
        """Fetch bars from (since_dt, now] using copy_rates_range to support incremental updates.
        since_dt should be a timezone-aware datetime in UTC (or naive UTC).
        """
        if not self.initialized:
            self.initialize()

        if timeframe not in TF_MAP:
            raise ValueError(f"Unsupported timeframe: {timeframe}")
        tf = TF_MAP[timeframe]

        # Normalize timestamp to UTC
        if since_dt is None:
            return []
        if getattr(since_dt, 'tzinfo', None) is None:
            since_dt = since_dt.replace(tzinfo=timezone.utc)

        end_dt = datetime.now(timezone.utc)
        self.logger.info("copy_rates_range symbol=%s tf=%s from=%s to=%s", symbol, timeframe, since_dt, end_dt)
        mt5.symbol_select(symbol, True)
        rates = mt5.copy_rates_range(symbol, tf, since_dt, end_dt)
        if rates is None:
            code, msg = mt5.last_error()
            self.logger.warning("copy_rates_range returned None for %s %s (since %s): %s %s", symbol, timeframe, since_dt, code, msg)
            return []

        names = set(getattr(rates, "dtype", None).names or [])
        out = []
        for r in rates:
            ts = datetime.fromtimestamp(int(r["time"]), tz=timezone.utc)
            tick_volume = int(r["tick_volume"]) if "tick_volume" in names else 0
            spread = int(r["spread"]) if "spread" in names else 0
            real_volume = int(r["real_volume"]) if "real_volume" in names else 0
            out.append(
                {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "ts": ts,
                    "open": float(r["open"]),
                    "high": float(r["high"]),
                    "low": float(r["low"]),
                    "close": float(r["close"]),
                    "tick_volume": tick_volume,
                    "spread": spread,
                    "real_volume": real_volume,
                }
            )
        return out

    # --- Trading helpers (demo-first; use at your own risk) ---
    def _ensure_initialized(self):
        if not self.initialized:
            self.initialize()

    def symbol_info(self, symbol: str):
        self._ensure_initialized()
        return mt5.symbol_info(symbol)

    def _current_price(self, symbol: str, side: str) -> float:
        tick = mt5.symbol_info_tick(symbol)
        if not tick:
            raise RuntimeError("No tick for symbol")
        return float(tick.ask if side == "buy" else tick.bid)

    def _pick_filling(self, info) -> int:
        # Best effort: try to honor broker's filling mode
        # 0=FOK, 1=IOC, 2=RETURN; fall back to FOK
        mode = getattr(info, "filling_mode", 0)
        if mode == 1 and hasattr(mt5, "ORDER_FILLING_IOC"):
            return mt5.ORDER_FILLING_IOC
        if mode == 2 and hasattr(mt5, "ORDER_FILLING_RETURN"):
            return mt5.ORDER_FILLING_RETURN
        return getattr(mt5, "ORDER_FILLING_FOK", 0)

    def positions_for(self, symbol: str):
        self._ensure_initialized()
        return mt5.positions_get(symbol=symbol) or []

    def list_positions(self, symbol: str) -> list[dict]:
        """Return simplified open positions for a symbol."""
        pos = self.positions_for(symbol)
        out: list[dict] = []
        for p in pos:
            try:
                out.append({
                    "ticket": int(getattr(p, "ticket", 0)),
                    "type": int(getattr(p, "type", 0)),
                    "volume": float(getattr(p, "volume", 0.0)),
                    "price_open": float(getattr(p, "price_open", 0.0)),
                    "sl": float(getattr(p, "sl", 0.0)),
                    "tp": float(getattr(p, "tp", 0.0)),
                    "profit": float(getattr(p, "profit", 0.0)),
                    "time": int(getattr(p, "time", 0)),
                })
            except Exception:
                # Be defensive; skip malformed entries
                continue
        return out

    def place_market(self, symbol: str, side: str, volume: float, deviation: int = 20, comment: str = "auto-quant", sl: float | None = None, tp: float | None = None) -> dict:
        self._ensure_initialized()
        info = self.symbol_info(symbol)
        if not info:
            raise RuntimeError("Symbol not found")
        mt5.symbol_select(symbol, True)

        price = self._current_price(symbol, side)
        req = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": float(volume),
            "type": mt5.ORDER_TYPE_BUY if side == "buy" else mt5.ORDER_TYPE_SELL,
            "price": price,
            "deviation": int(deviation),
            "magic": 734001,  # arbitrary
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": self._pick_filling(info),
        }
        if sl is not None:
            req["sl"] = float(sl)
        if tp is not None:
            req["tp"] = float(tp)
        result = mt5.order_send(req)
        if result is None:
            code, msg = mt5.last_error()
            raise RuntimeError(f"order_send failed: {code} {msg}")
        # Some brokers require different filling; try IOC if FOK failed
        if result.retcode != getattr(mt5, "TRADE_RETCODE_DONE", 10009):
            if req["type_filling"] != getattr(mt5, "ORDER_FILLING_IOC", 1):
                req["type_filling"] = getattr(mt5, "ORDER_FILLING_IOC", 1)
                result2 = mt5.order_send(req)
                if result2 and result2.retcode == getattr(mt5, "TRADE_RETCODE_DONE", 10009):
                    return {
                        "ok": True,
                        "retcode": int(result2.retcode),
                        "order": int(getattr(result2, "order", 0)),
                        "deal": int(getattr(result2, "deal", 0)),
                    }
        return {
            "ok": result.retcode == getattr(mt5, "TRADE_RETCODE_DONE", 10009),
            "retcode": int(result.retcode),
            "order": int(getattr(result, "order", 0)),
            "deal": int(getattr(result, "deal", 0)),
            "comment": getattr(result, "comment", ""),
        }

    def close_all_for(self, symbol: str, deviation: int = 20) -> list[dict]:
        # In netting accounts, sending the opposite market order with same volume reduces/closes
        pos = self.positions_for(symbol)
        out = []
        for p in pos:
            side = "sell" if int(p.type) == getattr(mt5, "POSITION_TYPE_BUY", 0) else "buy"
            out.append(self.place_market(symbol, side, float(p.volume), deviation, comment="auto-quant-close"))
        return out

    def close_all(self, deviation: int = 20) -> list[dict]:
        """Close all open positions across all symbols.
        Note: Uses netting behavior by sending opposite market orders for each position.
        """
        self._ensure_initialized()
        all_pos = mt5.positions_get() or []
        out: list[dict] = []
        for p in all_pos:
            try:
                sym = str(getattr(p, "symbol", ""))
                if not sym:
                    continue
                side = "sell" if int(getattr(p, "type", 0)) == getattr(mt5, "POSITION_TYPE_BUY", 0) else "buy"
                vol = float(getattr(p, "volume", 0.0))
                if vol <= 0:
                    continue
                out.append(self.place_market(sym, side, vol, deviation, comment="auto-quant-close"))
            except Exception:
                continue
        return out

    def get_tick(self, symbol: str) -> dict:
        self._ensure_initialized()
        if not mt5.symbol_select(symbol, True):
            code, msg = mt5.last_error()
            raise RuntimeError(f"symbol_select failed: {code} {msg}")
        t = mt5.symbol_info_tick(symbol)
        if not t:
            code, msg = mt5.last_error()
            raise RuntimeError(f"symbol_info_tick failed: {code} {msg}")
        return {
            "bid": float(getattr(t, "bid", 0.0)),
            "ask": float(getattr(t, "ask", 0.0)),
            "last": float(getattr(t, "last", 0.0)) if hasattr(t, "last") else None,
            "time": int(getattr(t, "time", 0)),
        }

    def account_info(self) -> dict:
        self._ensure_initialized()
        info = mt5.account_info()
        if not info:
            code, msg = mt5.last_error()
            raise RuntimeError(f"account_info failed: {code} {msg}")
        # Convert to plain dict with fields we care about
        return {
            "login": int(getattr(info, "login", 0)),
            "balance": float(getattr(info, "balance", 0.0)),
            "equity": float(getattr(info, "equity", 0.0)),
            "margin": float(getattr(info, "margin", 0.0)),
            "margin_free": float(getattr(info, "margin_free", 0.0)),
            "currency": str(getattr(info, "currency", "")),
        }


client = MT5Client()
