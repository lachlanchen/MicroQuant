# Deploying a Stable “Release” Instance (same machine)

This guide shows how to run a stable copy of the app alongside your dev instance on the same Windows PC, using a cloned code folder and a duplicated PostgreSQL database with the `_release` suffix.

## Overview

- Release code folder: `C:\Users\<you>\Projects\QuantTrading\microquant`
- Dev code folder (current): `C:\Users\<you>\Projects\QuantTrading\MetaTrader`
- Dev database: `metatrader_db`
- Release database: `metatrader_db_release`
- Release port: `8889` (configurable via `.env`)

The two instances are fully isolated: separate working folders, separate DBs, different ports.

## Prerequisites

- Windows PostgreSQL (v18 in examples) is installed and running.
- psql is available (e.g., `C:\Program Files\PostgreSQL\18\bin\psql.exe`).
- Python 3.10+ and pip available on Windows.
- Optional: WSL access (if you prefer running psql from WSL). Not required for production use.

## 1) Clone the “release” code folder

From PowerShell:

```
cd C:\Users\<you>\Projects\QuantTrading
git clone git@github.com:lachlanchen/MetaTrader.git microquant
```

Copy `.env` from your dev folder and adjust for release:

```
copy .\MetaTrader\.env .\microquant\.env
```

Edit `microquant\.env`:

- Set a different port (to avoid clashing with dev):
  - `PORT=8889`
- Point to the release DB (see step 3):
  - `DATABASE_URL=postgresql://postgres:<password>@localhost:5432/metatrader_db_release`
  - `DATABASE_MT_URL=postgresql://postgres:<password>@localhost:5432/metatrader_db_release`

Keep the rest of your secrets (LLM, news, MT5) as needed. Do not commit secrets.

## 2) (Optional) Allow WSL to access Windows Postgres

If you need to run DB commands from WSL, enable access:

- Edit `postgresql.conf` (e.g., `C:\Program Files\PostgreSQL\18\data\postgresql.conf`):
  - `listen_addresses = '*'`
- Edit `pg_hba.conf` (same data directory) and add your WSL vSwitch subnet (replace `/20` with your mask):
  - `host all all 172.26.176.0/20 md5`
- Firewall (PowerShell, Admin):
  - `netsh advfirewall firewall add rule name="PostgreSQL 5432" dir=in action=allow protocol=TCP localport=5432`
- Restart PostgreSQL service:
  - `net stop postgresql-x64-18 && net start postgresql-x64-18`

WSL test (no password prompt):

```
PGPASSWORD='<password>' psql -h 172.26.176.1 -p 5432 -U postgres -d metatrader_db -c "SELECT current_database(), current_user, inet_server_addr();"
``;

## 3) Duplicate the database for release

Fast path (same server, minimal downtime):

```
"C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -d postgres -c "CREATE DATABASE metatrader_db_release TEMPLATE metatrader_db;"
```

If TEMPLATE is blocked, use dump/restore:

```
"C:\Program Files\PostgreSQL\18\bin\pg_dump.exe" -U postgres -h localhost -p 5432 -d metatrader_db -Fc -f C:\Temp\metatrader.release.dump
"C:\Program Files\PostgreSQL\18\bin\createdb.exe" -U postgres -h localhost -p 5432 metatrader_db_release
"C:\Program Files\PostgreSQL\18\bin\pg_restore.exe" -U postgres -h localhost -p 5432 -d metatrader_db_release C:\Temp\metatrader.release.dump
```

Verification (Windows or WSL):

```
psql -U postgres -h localhost -d metatrader_db -c "SELECT COUNT(*) FROM ohlc_bars;"
psql -U postgres -h localhost -d metatrader_db_release -c "SELECT COUNT(*) FROM ohlc_bars;"
```

Counts for key tables (`ohlc_bars`, `news_articles`, `health_runs`, `stl_runs`, `stl_run_components`, `app_prefs`, `account_balances`, `closed_deals`, `signal_trades`) should match after a fresh clone.

## 4) Run the release instance

```
cd C:\Users\<you>\Projects\QuantTrading\microquant
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
killport 8889; python -m app.server
```

The server listens on `http://localhost:8889` and uses the `_release` database.

## 5) Re‑sync release DB later (optional)

If you want to refresh the release DB with a fresh copy of dev:

```
psql -U postgres -h localhost -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname IN ('metatrader_db','metatrader_db_release') AND pid <> pg_backend_pid();"
psql -U postgres -h localhost -d postgres -c "DROP DATABASE IF EXISTS metatrader_db_release;"
psql -U postgres -h localhost -d postgres -c "CREATE DATABASE metatrader_db_release TEMPLATE metatrader_db;"
```

## 6) Troubleshooting

- `FATAL: database does not exist`: confirm the DB name in `.env` and in psql commands.
- Timeouts from WSL: open firewall for 5432 and ensure `listen_addresses='*'`.
- `pg_dump version mismatch`: use the Windows `pg_dump.exe` when the server is on Windows, or use the TEMPLATE method.
- Permission errors on TEMPLATE: ensure no sessions are connected; terminate them before drop/create.

## 7) Notes on secrets and ports

- Keep `.env` out of version control; do not commit API keys.
- Use different ports for dev and release (`8888` vs `8889`) to avoid collisions.
- MT5 credentials are shared across instances unless you override them in `microquant\.env`.

