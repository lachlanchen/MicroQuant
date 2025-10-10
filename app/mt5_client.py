import os
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

    def initialize(self) -> None:
        if mt5 is None:
            raise RuntimeError(
                f"MetaTrader5 package not available: {_mt5_import_error}"
            )

        path = os.getenv("MT5_PATH") or None
        if not mt5.initialize(path=path):
            code, msg = mt5.last_error()
            raise RuntimeError(f"mt5.initialize failed: {code} {msg}")

        login = os.getenv("MT5_LOGIN")
        password = os.getenv("MT5_PASSWORD")
        server = os.getenv("MT5_SERVER")
        # If login details provided, attempt login; otherwise rely on running terminal session
        if login and password:
            if not mt5.login(int(login), password=password, server=server):
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
        mt5.symbol_select(symbol, True)

        rates = mt5.copy_rates_from_pos(symbol, tf, 0, int(count))
        if rates is None:
            code, msg = mt5.last_error()
            raise RuntimeError(f"copy_rates_from_pos failed: {code} {msg}")

        out = []
        for r in rates:
            ts = datetime.fromtimestamp(int(r["time"]), tz=timezone.utc)
            out.append(
                {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "ts": ts,
                    "open": float(r["open"]),
                    "high": float(r["high"]),
                    "low": float(r["low"]),
                    "close": float(r["close"]),
                    "tick_volume": int(r.get("tick_volume", 0)),
                    "spread": int(r.get("spread", 0)),
                    "real_volume": int(r.get("real_volume", 0)),
                }
            )
        return out


client = MT5Client()

