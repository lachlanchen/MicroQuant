# MT5 Tornado Starter (Gold Data)

A minimal Tornado + Postgres app that fetches OHLC bars from MetaTrader 5 (via the official Python package) and serves a simple chart UI. Default symbol is `XAUUSD` (gold vs USD).

## Features
- Fetch bars from MT5: `/api/fetch?symbol=XAUUSD&tf=H1&count=500`
- Persist OHLC into Postgres (`ohlc_bars` table)
- Serve chart UI at `/` using Chart.js (close price line)

## Prereqs
- Ubuntu with MT5 installed via Wine (e.g., `mt5linux.sh`). Ensure the terminal is running and logged in to your demo or real account.
- Python 3.10+
- PostgreSQL running locally; create `metatrader_db` and user `lachlan` (or adjust).

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Alternative: local 3.11 venv (if your Conda env is 3.13)
# Requires python3.11 on your system
# sudo apt install python3.11 python3.11-venv
bash scripts/bootstrap_venv311.sh
source .venv311/bin/activate

# DB (use your own user/password as needed)
# createdb -h localhost -p 5432 -U lachlan metatrader_db

# Configure env (copy and edit)
cp .env.example .env
# then edit .env with your MT5 PATH and credentials
# export env vars into your shell
set -a; source .env; set +a

# Run app
python -m app.server
# Open http://localhost:8888
```

Notes:
- `MT5_PATH` should point to your `terminal64.exe` under the Wine prefix used by the install script.
- You can omit `MT5_LOGIN/MT5_PASSWORD/MT5_SERVER` if your terminal is already running and logged in. If provided, the app will attempt `mt5.login()`.
- Default DB env var is `DATABASE_URL`. If not set, the app tries `DATABASE_MT_URL` then `DATABASE_QT_URL`.

## Endpoints
- `GET /api/fetch?symbol=XAUUSD&tf=H1&count=500` — fetch from MT5 and upsert to DB
- `GET /api/data?symbol=XAUUSD&tf=H1&limit=500` — read from DB for charting
- `GET /` — simple UI with a line chart of closes

## Schema
See `sql/schema.sql`. Primary key on `(symbol, timeframe, ts)` prevents duplicate bars; inserts use `ON CONFLICT ... DO UPDATE`.

## Troubleshooting
- MT5 initialize failed: set `MT5_PATH` to the exact `terminal64.exe` and ensure the terminal is running once manually.
- Login failed: specify `MT5_SERVER` exactly as shown in the MT5 terminal or omit and rely on the existing session.
- No data for symbol: make sure the symbol exists with your broker and is visible in Market Watch; you can adjust the symbol (e.g., `XAUUSD`, `XAUUSD.a`, `GOLD` depending on broker).
- Postgres connection: ensure `DATABASE_URL` is correct; test with `psql "$DATABASE_URL" -c 'select 1;'`.

## Dev tips
- For candlestick charts, you can later add the `chartjs-chart-financial` plugin. The starter uses a line chart for simplicity.
- For scheduled fetching, add a periodic callback in Tornado that calls `/api/fetch` logic.
