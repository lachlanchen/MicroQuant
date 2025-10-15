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
        self.current_login: Optional[int] = None
        self.last_login_error: Optional[tuple[int, str]] = None

    # Backoff between failed initialize attempts to avoid log spam
    _last_init_attempt: float = 0.0
    _init_cooldown_sec: float = 5.0

    def initialize(self) -> None:
        if mt5 is None:
            raise RuntimeError(
                f"MetaTrader5 package not available: {_mt5_import_error}"
            )

        path = os.getenv("MT5_PATH") or None
        import time as _t
        now = _t.time()
        if self._last_init_attempt and (now - self._last_init_attempt) < self._init_cooldown_sec:
            raise RuntimeError("mt5 not ready (cooldown)")
        self._last_init_attempt = now
        self.logger.info("mt5.initialize path=%r", path)
        if not mt5.initialize(path=path):
            code, msg = mt5.last_error()
            # Fallback: attempt attach without explicit path (may connect to running terminal)
            self.logger.warning("mt5.initialize failed: %s %s; trying default attach", code, msg)
            if not mt5.initialize():
                # Leave initialized False; caller can trigger login() path
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
                self.current_login = None
                self.last_login_error = (code, msg)
                self.logger.warning("mt5.login failed during init account=%s code=%s msg=%s", login, code, msg)
            else:
                self.current_login = int(login)
                self.last_login_error = None

        self.initialized = True
        info = mt5.account_info()
        if info:
            try:
                self.current_login = int(getattr(info, "login", 0) or 0)
            except (TypeError, ValueError):
                self.current_login = None

    def login(self, account: int, password: str, server: Optional[str] = None) -> bool:
        """Ensure MT5 session is authenticated for the requested account.

        Returns True when the session is already on that login or after a successful login,
        False when MetaTrader refuses the credentials.
        """
        try:
            account_id = int(account)
        except (TypeError, ValueError):
            self.logger.warning("mt5.login invalid account=%r", account)
            return False

        need_retry = False
        try:
            self._ensure_initialized()
        except RuntimeError as exc:
            self.logger.warning("mt5.initialize failed (%s); retry with credentials", exc)
            need_retry = True

        if need_retry:
            path = os.getenv("MT5_PATH") or None
            try:
                mt5.shutdown()
            except Exception:
                pass
            self.logger.info("mt5.initialize retry with credentials account=%s server=%r", account_id, server)
            if server:
                ok = mt5.initialize(path=path, login=account_id, password=password, server=server)
            else:
                ok = mt5.initialize(path=path, login=account_id, password=password)
            if not ok:
                code, msg = mt5.last_error()
                self.logger.error("mt5.initialize retry failed account=%s code=%s msg=%s", account_id, code, msg)
                self.current_login = None
                self.last_login_error = (code, msg)
                self.initialized = False
                return False
            self.initialized = True
            self.current_login = account_id
            self.last_login_error = None
            return True

        info = mt5.account_info()
        if info and int(getattr(info, "login", 0) or 0) == account_id:
            self.current_login = account_id
            self.last_login_error = None
            return True

        self.logger.info("mt5.login account=%s server=%r", account_id, server)
        if server:
            ok = mt5.login(account_id, password=password, server=server)
        else:
            ok = mt5.login(account_id, password=password)

        if ok:
            self.current_login = account_id
            self.last_login_error = None
            return True

        code, msg = mt5.last_error()
        self.logger.warning("mt5.login failed account=%s code=%s msg=%s", account_id, code, msg)
        self.last_login_error = (code, msg)
        return False

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

    def fetch_bars_range(self, symbol: str, timeframe: str, start_dt, end_dt) -> list[dict]:
        """Fetch bars in [start_dt, end_dt] using copy_rates_range.
        Datetimes should be timezone-aware UTC (or naive UTC). A small future buffer is applied to end_dt
        using MT5_HISTORY_FUTURE_HOURS env (default 12) to avoid boundary misses.
        """
        if not self.initialized:
            self.initialize()

        if timeframe not in TF_MAP:
            raise ValueError(f"Unsupported timeframe: {timeframe}")
        tf = TF_MAP[timeframe]

        if start_dt is None or end_dt is None:
            return []
        if getattr(start_dt, 'tzinfo', None) is None:
            start_dt = start_dt.replace(tzinfo=timezone.utc)
        if getattr(end_dt, 'tzinfo', None) is None:
            end_dt = end_dt.replace(tzinfo=timezone.utc)

        try:
            fwd_hours = int(os.getenv("MT5_HISTORY_FUTURE_HOURS", "12"))
        except Exception:
            fwd_hours = 12
        from datetime import timedelta
        eff_end = end_dt + timedelta(hours=max(0, fwd_hours))

        self.logger.info("copy_rates_range symbol=%s tf=%s from=%s to=%s", symbol, timeframe, start_dt, eff_end)
        mt5.symbol_select(symbol, True)
        rates = mt5.copy_rates_range(symbol, tf, start_dt, eff_end)
        if rates is None:
            code, msg = mt5.last_error()
            self.logger.warning("copy_rates_range returned None for %s %s (%s→%s): %s %s", symbol, timeframe, start_dt, eff_end, code, msg)
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
                    "symbol": symbol,
                    "ticket": int(getattr(p, "ticket", 0)),
                    "type": int(getattr(p, "type", 0)),
                    "volume": float(getattr(p, "volume", 0.0)),
                    "price_open": float(getattr(p, "price_open", 0.0)),
                    "sl": float(getattr(p, "sl", 0.0)),
                    "tp": float(getattr(p, "tp", 0.0)),
                    "comment": str(getattr(p, "comment", "")) if hasattr(p, "comment") else "",
                    "profit": float(getattr(p, "profit", 0.0)),
                    "time": int(getattr(p, "time", 0)),
                })
            except Exception:
                # Be defensive; skip malformed entries
                continue
        return out

    def modify_position_sltp(self, symbol: str, ticket: int, sl: float | None, tp: float | None) -> dict:
        """Modify SL/TP for a single open position by ticket.

        Always sends both SL and TP values (falling back to existing values should be handled by caller).
        """
        self._ensure_initialized()
        info = self.symbol_info(symbol)
        if not info:
            raise RuntimeError("Symbol not found")
        # Ensure symbol is selected in terminal
        mt5.symbol_select(symbol, True)
        try:
            req = {
                "action": getattr(mt5, "TRADE_ACTION_SLTP", 3),
                "symbol": symbol,
                "position": int(ticket),
            }
            if sl is not None:
                req["sl"] = float(sl)
            if tp is not None:
                req["tp"] = float(tp)
            result = mt5.order_send(req)
            if result is None:
                code, msg = mt5.last_error()
                return {"ok": False, "retcode": code, "error": f"order_send failed: {code} {msg}"}
            return {
                "ok": int(getattr(result, "retcode", 0)) == getattr(mt5, "TRADE_RETCODE_DONE", 10009),
                "retcode": int(getattr(result, "retcode", 0)),
                "order": int(getattr(result, "order", 0)) if hasattr(result, "order") else None,
                "deal": int(getattr(result, "deal", 0)) if hasattr(result, "deal") else None,
                "comment": getattr(result, "comment", ""),
            }
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def list_positions_all(self) -> list[dict]:
        """Return simplified open positions across all symbols."""
        self._ensure_initialized()
        try:
            all_pos = mt5.positions_get() or []
        except Exception:
            all_pos = []
        out: list[dict] = []
        for p in all_pos:
            try:
                out.append({
                    "symbol": str(getattr(p, "symbol", "")),
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

    def close_position(self, position, deviation: int = 20) -> dict:
        """Attempt to close a single position by ticket (hedging-safe)."""
        self._ensure_initialized()
        try:
            ticket = int(getattr(position, "ticket", 0))
            symbol = str(getattr(position, "symbol", ""))
            ptype = int(getattr(position, "type", 0))
            volume = float(getattr(position, "volume", 0.0))
        except Exception:
            return {"ok": False, "error": "invalid_position"}
        if not ticket or not symbol or volume <= 0:
            return {"ok": False, "error": "invalid_position_fields"}
        opp = "sell" if ptype == getattr(mt5, "POSITION_TYPE_BUY", 0) else "buy"
        price = self._current_price(symbol, opp)
        info = self.symbol_info(symbol)
        req = {
            "action": getattr(mt5, "TRADE_ACTION_DEAL", 1),
            "symbol": symbol,
            "position": ticket,
            "volume": float(volume),
            "type": getattr(mt5, "ORDER_TYPE_SELL", 1) if opp == "sell" else getattr(mt5, "ORDER_TYPE_BUY", 0),
            "price": price,
            "deviation": int(deviation),
            "magic": 734001,
            "comment": "auto-quant-close",
            "type_time": getattr(mt5, "ORDER_TIME_GTC", 0),
            "type_filling": self._pick_filling(info),
        }
        result = mt5.order_send(req)
        if result is None:
            code, msg = mt5.last_error()
            return {"ok": False, "retcode": code, "error": f"order_send failed: {code} {msg}"}
        if result.retcode != getattr(mt5, "TRADE_RETCODE_DONE", 10009):
            # Try IOC if needed
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
                "ok": False,
                "retcode": int(getattr(result, "retcode", 0)),
                "order": int(getattr(result, "order", 0)),
                "deal": int(getattr(result, "deal", 0)),
                "comment": getattr(result, "comment", ""),
            }
        return {
            "ok": True,
            "retcode": int(result.retcode),
            "order": int(getattr(result, "order", 0)),
            "deal": int(getattr(result, "deal", 0)),
        }

    def close_all_for(self, symbol: str, deviation: int = 20, side: str | None = None) -> list[dict]:
        # In netting accounts, sending the opposite market order with same volume reduces/closes
        pos = self.positions_for(symbol)
        self.logger.info("close_all_for symbol=%s positions=%d side=%s", symbol, len(pos), side)
        out = []
        for p in pos:
            ptype = int(getattr(p, "type", 0))
            # Filter by requested side: 'long' closes only buys; 'short' closes only sells
            if side == "long" and ptype != getattr(mt5, "POSITION_TYPE_BUY", 0):
                continue
            if side == "short" and ptype != getattr(mt5, "POSITION_TYPE_SELL", 1):
                continue
            out.append(self.close_position(p, deviation))
        return out

    def close_all(self, deviation: int = 20, side: str | None = None) -> list[dict]:
        """Close all open positions across all symbols.
        Note: Uses netting behavior by sending opposite market orders for each position.
        """
        self._ensure_initialized()
        all_pos = mt5.positions_get() or []
        self.logger.info("close_all across symbols positions=%d side=%s", len(all_pos), side)
        out: list[dict] = []
        for p in all_pos:
            try:
                sym = str(getattr(p, "symbol", ""))
                if not sym:
                    continue
                ptype = int(getattr(p, "type", 0))
                if side == "long" and ptype != getattr(mt5, "POSITION_TYPE_BUY", 0):
                    continue
                if side == "short" and ptype != getattr(mt5, "POSITION_TYPE_SELL", 1):
                    continue
                out.append(self.close_position(p, deviation))
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
        # Enrich with symbol metadata when available so the UI can format prices precisely
        info = None
        try:
            info = mt5.symbol_info(symbol)
        except Exception:
            info = None
        digits = int(getattr(info, "digits", 0) or 0) if info is not None else None
        point = float(getattr(info, "point", 0.0) or 0.0) if info is not None else None
        contract_size = float(getattr(info, "trade_contract_size", 0.0) or 0.0) if info is not None else None
        min_vol = float(getattr(info, "volume_min", 0.0) or 0.0) if info is not None else None
        vol_step = float(getattr(info, "volume_step", 0.0) or 0.0) if info is not None else None
        return {
            "bid": float(getattr(t, "bid", 0.0)),
            "ask": float(getattr(t, "ask", 0.0)),
            "last": float(getattr(t, "last", 0.0)) if hasattr(t, "last") else None,
            "time": int(getattr(t, "time", 0)),
            # optional meta
            "digits": digits,
            "point": point,
            "contract_size": contract_size,
            "min_volume": min_vol,
            "volume_step": vol_step,
        }

    def closed_deals(self, from_dt=None, to_dt=None) -> list[dict]:
        """Return simplified closed deals within a time range.
        Each item: {ts, symbol, profit, commission, swap, order, deal, volume, entry}

        Notes:
        - Extends the query window by +/- MT5_HISTORY_FUTURE_HOURS (default 12) to avoid
          timezone boundary truncation (MT5 expects local-naive datetimes).
        """
        self._ensure_initialized()
        # Default to last 180 days if not provided
        import datetime as _dt
        from datetime import timezone as _tz
        if to_dt is None:
            to_dt = _dt.datetime.now(_tz.utc)
        if from_dt is None:
            from_dt = to_dt - _dt.timedelta(days=180)
        # Apply a future/past buffer to reduce risk of missing near-boundary items
        try:
            _fwd_hours = int(os.getenv("MT5_HISTORY_FUTURE_HOURS", "12"))
        except Exception:
            _fwd_hours = 12
        try:
            _back_hours = int(os.getenv("MT5_HISTORY_BACK_HOURS", str(_fwd_hours)))
        except Exception:
            _back_hours = _fwd_hours
        from_dt_buf = from_dt - _dt.timedelta(hours=max(0, _back_hours))
        to_dt_buf = to_dt + _dt.timedelta(hours=max(0, _fwd_hours))
        # MetaTrader expects naive datetimes expressed in the terminal's local timezone.
        # Convert any timezone-aware inputs to local time, then drop tzinfo so we pass naive datetimes.
        _local_tz = _dt.datetime.now().astimezone().tzinfo
        def _to_local_naive(d: _dt.datetime) -> _dt.datetime:
            if getattr(d, "tzinfo", None) is None:
                return d
            return d.astimezone(_local_tz).replace(tzinfo=None)

        from_sel = _to_local_naive(from_dt_buf)
        to_sel = _to_local_naive(to_dt_buf)
        # Ensure history window is selected for reliability across terminals
        try:
            self.logger.debug("history_select local %s -> %s (buffered)", from_sel, to_sel)
            mt5.history_select(from_sel, to_sel)
        except Exception:
            pass
        deals = mt5.history_deals_get(from_sel, to_sel) or []
        try:
            if deals is None or len(deals) == 0:
                code, msg = mt5.last_error()
                self.logger.info("history_deals_get returned empty; last_error=%s %s", code, msg)
            else:
                # Log a concise summary: total count and entry distribution
                entry_counts: dict[str, int] = {}
                for d in deals:
                    e = getattr(d, "entry", None)
                    key = str(int(e)) if e is not None else "None"
                    entry_counts[key] = entry_counts.get(key, 0) + 1
                self.logger.info(
                    "history_deals_get count=%d entries=%s", len(deals), entry_counts
                )
        except Exception:
            pass
        out: list[dict] = []
        for d in deals:
            try:
                ts = getattr(d, "time", 0)
                # MetaTrader5 returns epoch seconds in some builds; also has time_msc. Use time if available.
                if hasattr(d, "time_msc") and int(getattr(d, "time_msc", 0)):
                    ts_ms = int(getattr(d, "time_msc", 0))
                    ts_iso = _dt.datetime.fromtimestamp(ts_ms / 1000, _tz.utc).isoformat()
                else:
                    ts_iso = _dt.datetime.fromtimestamp(int(ts), _tz.utc).isoformat()
                # Prefer 'ticket' as the unique deal id; some builds expose it as 'ticket' rather than 'deal'
                deal_id = None
                try:
                    deal_id = int(getattr(d, "deal", 0))
                except Exception:
                    deal_id = None
                if not deal_id:
                    try:
                        deal_id = int(getattr(d, "ticket", 0))
                    except Exception:
                        deal_id = 0
                out.append({
                    "ts": ts_iso,
                    "symbol": str(getattr(d, "symbol", "")),
                    "profit": float(getattr(d, "profit", 0.0)),
                    "commission": float(getattr(d, "commission", 0.0)) if hasattr(d, "commission") else 0.0,
                    "swap": float(getattr(d, "swap", 0.0)) if hasattr(d, "swap") else 0.0,
                    "order": int(getattr(d, "order", 0)) if hasattr(d, "order") else None,
                    "deal": deal_id,
                    "volume": float(getattr(d, "volume", 0.0)) if hasattr(d, "volume") else None,
                    "entry": int(getattr(d, "entry", 0)) if hasattr(d, "entry") else None,
                    "comment": str(getattr(d, "comment", "")) if hasattr(d, "comment") else None,
                })
            except Exception:
                continue
        # Keep all deals; some brokers/netting modes may not mark OUT consistently.
        # Frontend can choose which to visualize; we store everything for completeness.
        # Sort ascending by ts
        out.sort(key=lambda r: r.get("ts") or "")
        return out

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
