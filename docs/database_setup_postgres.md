# PostgreSQL Setup (Ubuntu) — metatrader_db

Use these commands to create the `metatrader_db` database and (optionally) the `lachlan` role. Prefer not committing real passwords; use placeholders or a local `.env` not tracked by git.

## Prerequisites
- PostgreSQL installed and running (`sudo systemctl status postgresql`)
- Admin access to the `postgres` role (default superuser)

## Create role (if missing)
```bash
# Create role only if it does not exist
sudo -u postgres psql -v ON_ERROR_STOP=1 -c "DO $$ BEGIN IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'lachlan') THEN CREATE ROLE lachlan WITH LOGIN PASSWORD '<YOUR_PASSWORD>'; END IF; END $$;"
```

## Create database and set owner
```bash
# Create the database owned by 'lachlan'
sudo -u postgres psql -v ON_ERROR_STOP=1 -c "CREATE DATABASE metatrader_db OWNER lachlan ENCODING 'UTF8' TEMPLATE template0;"
```

## Optional: create qtrader_db as well
```bash
sudo -u postgres psql -v ON_ERROR_STOP=1 -c "CREATE DATABASE qtrader_db OWNER lachlan ENCODING 'UTF8' TEMPLATE template0;"
```

## Verify databases
```bash
# List databases
sudo -u postgres psql -tAc "SELECT datname FROM pg_database ORDER BY 1;"
```

## Test connection
```bash
# Using a full URL (replace placeholders)
psql "postgresql://lachlan:<YOUR_PASSWORD>@localhost:5432/metatrader_db" -c "SELECT current_database(), current_user;"
```

## Environment variables (example)
If you want to use env vars in your apps, set them locally (don’t commit secrets):
```bash
export DATABASE_MT_URL='postgresql://lachlan:<YOUR_PASSWORD>@localhost:5432/metatrader_db'
export DATABASE_QT_URL='postgresql://lachlan:<YOUR_PASSWORD>@localhost:5432/qtrader_db'
```

Notes:
- If you already have role `lachlan`, you can skip the role creation step.
- If you prefer `createdb`/`createuser` CLI:
  - `sudo -u postgres createuser --login --pwprompt lachlan`
  - `sudo -u postgres createdb --owner=lachlan metatrader_db`
- On fresh installs, `psql` may use peer auth for `postgres`; `sudo -u postgres ...` handles this.
