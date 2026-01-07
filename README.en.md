# MicroQuant by Lazying.art — Overview

MicroQuant by Lazying.art is a Micro Quant philosophy wrapped around a Tornado + Postgres prototype. It fetches market data (XAUUSD, etc.) from MetaTrader 5, persists it into PostgreSQL, and exposes a Chart.js-powered UI so the AI trade plan stack can breathe through a data-rich signal console.

The `docs/` directory holds the MicroQuant landing page (`quant.lazying.art`), while `references/` stores supporting notes about trading prompts, DB setup, and MT5+Python integration.

Use `python -m app.server` after configuring the `.env` variables and Postgres schema to explore the Quant UI locally.
