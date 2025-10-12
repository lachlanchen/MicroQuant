# MT5 + Python on Ubuntu (Wine)

This note shows how to connect Python to a running MT5 terminal installed via `mt5linux.sh`.

## 1) Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install MetaTrader5 pandas numpy
```

## 2) Find your MT5 terminal path

The MetaQuotes script installs MT5 under a Wine prefix. Common locations to try (paths vary by script/version):

- `~/.mt5/drive_c/Program Files/MetaTrader 5/terminal64.exe`
- `~/.wine/drive_c/Program Files/MetaTrader 5/terminal64.exe`
- `~/.local/share/wineprefixes/mt5/drive_c/Program Files/MetaTrader 5/terminal64.exe`

If unsure, search:

```bash
find ~ -type f -iname "terminal64.exe" 2>/dev/null | head -n 5
```

Ensure the terminal is running and logged into a trading account.

## 3) Connect from Python

```python
import MetaTrader5 as mt5

PATH = "/home/USER/.mt5/drive_c/Program Files/MetaTrader 5/terminal64.exe"  # <- update

# Initialize; omit path if MT5 is in default search locations
if not mt5.initialize(path=PATH):
    raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")

# Basic sanity checks
info = mt5.terminal_info()
account_info = mt5.account_info()
symbols = mt5.symbols_get(limit=5)
print(info)
print(account_info)
print([s.name for s in symbols])

mt5.shutdown()
```

Notes:

- On Linux/Wine, passing `path=` often avoids initialization issues.
- Terminal must be running and logged in (real or demo). If you have multiple installations, match the path to the running one.

## 4) Common gotchas

- Initialization error 1: Ensure `terminal64.exe` exists and is executable by Wine; run the terminal once manually.
- No data returned: Symbol not visible/active in Market Watch; enable it in the terminal.
- Order send fails: Check trade permissions and account type (netting vs hedging), and ensure the symbol is tradeable.

## 5) Strategy tester (optional)

For reproducible backtests, prefer MT5’s built‑in tester. On Linux/Wine it works well; use genetic/forward optimization for robust parameter search. You can also run local agents; the MQL5 Cloud Network requires an active terminal/agents.

