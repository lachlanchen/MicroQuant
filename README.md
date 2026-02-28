[English](README.md) · [العربية](i18n/README.ar.md) · [Español](i18n/README.es.md) · [Français](i18n/README.fr.md) · [日本語](i18n/README.ja.md) · [한국어](i18n/README.ko.md) · [Tiếng Việt](i18n/README.vi.md) · [中文 (简体)](i18n/README.zh-Hans.md) · [中文（繁體）](i18n/README.zh-Hant.md) · [Deutsch](i18n/README.de.md) · [Русский](i18n/README.ru.md)

<p align="center">
  <img src="https://raw.githubusercontent.com/lachlanchen/lachlanchen/main/logos/banner.png" alt="LazyingArt banner" />
</p>


# MetaTrader QT - Quantitative Trading Starter (Micro Quant Philosophy)

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Backend](https://img.shields.io/badge/Backend-Tornado-2d7cbf)
![Database](https://img.shields.io/badge/Database-PostgreSQL-336791?logo=postgresql&logoColor=white)
![Broker](https://img.shields.io/badge/Broker%20Bridge-MetaTrader5-1f6feb)
![UI](https://img.shields.io/badge/UI-Lightweight%20Charts%20%2B%20Chart.js-0ea5e9)
![Status](https://img.shields.io/badge/README-Expanded-success)

## 📸 Screenshot
![Micro Quant UI](figures/demos/micro-quant-ui.png)

<p align="center">
  <a href="https://my.roboforex.com/en/?a=efx" target="_blank" rel="noopener noreferrer">
    <button style="padding: 0.65rem 1.25rem; font-weight: 600; border-radius: 999px; border: none; color: white; background: #0060ff; cursor: pointer;">
      DATA Source
    </button>
  </a>
</p>

## 🧭 Overview
Micro Quant is less about shiny dashboards and more about a repeatable trading logic stack: it pulls OHLC data from MetaTrader 5, persists it into Postgres, and evaluates systematic decisions through layered AI-guided signals (Basic news, Tech snapshot, trade plans, and STL overlays). The UI reflects that philosophy with alignment toggles, reasoned closes, persisted preferences, and a data-rich execution pane so the server can safely run periodic or modal trade flows while you inspect logs and evidence.

The static landing page (Quant by Lazying.art) lives under `docs/` and is published through GitHub Pages (`trade.lazying.art` via `docs/CNAME`). The repository also includes references for AI Trade Plan prompts, integration notes, and operational documentation.

### At a glance
| Area | What it does |
|---|---|
| Data | Pulls MT5 OHLC and upserts to PostgreSQL |
| Analytics | Runs health/news/tech and STL workflows |
| Decisioning | Builds AI trade plans from layered context |
| Execution | Executes/controls trade flows behind safety guards |
| UI | Desktop/mobile views with synchronized chart workflows |

## 🧠 Core Philosophy
- **Chain of truth**: Basic news checks (text + scores) and Tech snapshots (heavy technical context + STL) feed a single AI trade plan per symbol/timeframe. Periodic auto-runs and manual modal runs share the same pipeline and reasoning logs.
- **Alignment-first execution**: Accept-Tech/Hold-Neutral toggles, ignore-basics switch, and partial-close wrappers ensure Tech is followed intentionally, opposite positions are closed before new entries when needed, and unnecessary exits are minimized.
- **Immutable data**: Every fetch writes to Postgres with `ON CONFLICT` hygiene, while `/api/data` reads sanitized series for the UI. Preferences (auto volumes, `close_fraction`, hide-tech toggles, STL auto-compute) persist through `/api/preferences`.
- **Safety-first trading**: `TRADING_ENABLED` and `safe_max` enforce manual/auto permissioning. `/api/close` and periodic runners can log closure reasons (tech neutral, misalignment, etc.) for traceability.

## ✨ Features
- MT5 OHLC ingestion into Postgres (`/api/fetch`, `/api/fetch_bulk`).
- Chart UI at `/` (desktop) plus `/app` (mobile), with Chart.js + Lightweight Charts usage in templates.
- STL decomposition workflows (`/api/stl`, `/api/stl/compute`, prune/delete endpoints).
- News ingestion and analysis (`/api/news`, `/api/news/backfill_forex`, `/api/news/analyze`).
- AI workflow orchestration (`/api/health/run`, `/api/health/runs`, `/api/ai/trade_plan`).
- Manual trade execution (`/api/trade`, `/api/trade/execute_plan`) guarded by `TRADING_ENABLED`.
- Position risk operations (`/api/positions*`, `/api/close`, `/api/close_tickets`) with close operations allowed for safety.
- WebSocket update stream at `/ws/updates`.

## 🗂️ Project Structure
```text
metatrader_qt/
├── app/
│   ├── server.py                # Tornado app, routes, orchestration
│   ├── db.py                    # asyncpg access layer + schema init
│   ├── mt5_client.py            # MetaTrader5 bridge + order/data operations
│   ├── news_fetcher.py          # FMP/AlphaVantage aggregation/filtering
│   └── strategy.py              # SMA crossover helper
├── templates/
│   ├── index.html               # Main desktop UI
│   └── mobile.html              # Mobile-oriented UI
├── static/                      # PWA assets (icons/manifest/service worker)
├── sql/
│   └── schema.sql               # Core DB schema
├── scripts/
│   ├── test_mixed_ai.py         # Mixed AI smoke test
│   ├── test_fmp.py              # FMP smoke test
│   ├── test_fmp_endpoints.py    # FMP endpoint probe script
│   ├── setup_windows.ps1        # Windows env bootstrap
│   ├── run_windows.ps1          # Windows run helper
│   └── bootstrap_venv311.sh     # Linux/mac Python 3.11 helper
├── docs/                        # GitHub Pages landing site
├── references/                  # Operational/setup notes
├── strategies/llm/              # Prompt/config JSON files
├── llm_model/echomind/          # LLM provider wrappers
├── i18n/                        # Present (currently empty)
├── .github/FUNDING.yml          # Sponsor/support metadata
└── README.md + README.*.md      # Canonical + multilingual docs
```

## ✅ Prerequisites
- Ubuntu/Linux or Windows.
- MT5 installed and accessible (`terminal64.exe`), with terminal running/logged in.
- Python 3.10+ (3.11 recommended for MetaTrader5 compatibility).
- PostgreSQL instance.

## 🛠️ Installation

### Windows (PowerShell)
```powershell
# 1) Create venv with Python 3.11 (MetaTrader5 has no wheels for 3.13 yet)
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt

# 2) Configure env
Copy-Item .env.example .env
# Edit .env and set DATABASE_URL, MT5_PATH (e.g. C:\Program Files\MetaTrader 5\terminal64.exe), and your MT5 demo creds
# Load env for this session
Get-Content .env | Where-Object { $_ -and $_ -notmatch '^#' } | ForEach-Object { $n,$v = $_ -split '=',2; [Environment]::SetEnvironmentVariable($n, $v, 'Process') }

# 3) Run app
python -m app.server
# Open http://localhost:8888
```

Helper scripts:
```powershell
scripts\setup_windows.ps1
scripts\run_windows.ps1
```

### Linux/macOS (bash)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Alternative: local 3.11 venv (if your global/Conda Python is 3.13)
# Requires python3.11 on your system
# sudo apt install python3.11 python3.11-venv
bash scripts/bootstrap_venv311.sh
source .venv311/bin/activate

# DB (use your own user/password as needed)
# createdb -h localhost -p 5432 -U lachlan metatrader_db

# Configure env
cp .env.example .env
# edit .env with your MT5 path and credentials
set -a; source .env; set +a

# Run app
python -m app.server
# Open http://localhost:8888
```

## ⚙️ Configuration
Copy `.env.example` to `.env` and adjust values.

### Core variables
| Variable | Purpose |
|---|---|
| `DATABASE_URL` | Preferred PostgreSQL DSN |
| `DATABASE_MT_URL` | Fallback DSN if `DATABASE_URL` unset |
| `DATABASE_QT_URL` | Secondary fallback DSN |
| `MT5_PATH` | Path to `terminal64.exe` (Wine or native) |
| `MT5_LOGIN` / `MT5_PASSWORD` / `MT5_SERVER` | Optional if MT5 terminal session is already logged in |
| `PORT` | Server port (default `8888`) |

### Optional variables
- `FMP_API_KEY`, `ALPHAVANTAGE_API_KEY` for news enrichment.
- `TRADING_ENABLED` (`0` default, set `1` to allow order placement endpoints).
- `TRADING_VOLUME` (default manual volume).
- `AUTO_FETCH`, `AUTO_FETCH_SYMBOL`, `AUTO_FETCH_TF`, `AUTO_FETCH_COUNT`, `AUTO_FETCH_SEC`.
- `PIN_DEFAULTS_TO_XAU_H1=1` to force UI startup default symbol/timeframe.
- `LOG_LEVEL`, `LOG_BACKFILL`, plus account/poll related prefs through `/api/preferences` and environment.

Notes:
- `MT5_PATH` should point to your `terminal64.exe` under the Wine prefix used by your MT5 install script.
- You can omit MT5 credentials when terminal session is already logged in; the app will attempt to reuse that session.

## 🚀 Usage

### Start server
```bash
python -m app.server
```

### Open UI
- Desktop UI: `http://localhost:8888/`
- Mobile UI: `http://localhost:8888/app`

### Common workflow
1. Fetch bars from MT5 and persist into Postgres.
2. Read bars from DB for charting.
3. Run health/tech/news analyses.
4. Generate AI trade plan.
5. Execute or close positions under safety guards.

## 🔌 API Endpoints (Practical)
- `GET /api/fetch?symbol=XAUUSD&tf=H1&count=500[&mode=inc|full][&persist=1]`
  - Fetch from MT5 and upsert to DB.
  - If `persist=1`, server saves `last_symbol/last_tf/last_count` defaults; bulk/background fetches should omit this to avoid overriding UI choices.
- `GET /api/fetch_bulk` — bulk/scheduled ingestion.
- `GET /api/data?symbol=XAUUSD&tf=H1&limit=500` — read chart data from DB.
- `GET /api/strategy/run?symbol=XAUUSD&tf=H1&fast=20&slow=50`
  - Runs SMA(20/50) crossover and returns signal payload.
  - Important implementation note: strategy-driven order placement from this endpoint is currently disabled in server code; order execution is handled through trade endpoints.
- `POST /api/trade` — manual Buy/Sell from UI, gated by `TRADING_ENABLED`.
- `POST /api/trade/execute_plan` — executes a generated plan, includes pre-close and stop-distance checks.
- `POST /api/close` — flatten positions (allowed even when `TRADING_ENABLED=0` for safety):
  - Current symbol: form body `symbol=...`; optional `side=long|short|both`.
  - All symbols: `?scope=all` and optional `&side=...`.
  - Response includes `closed_count` and per-ticket results.
- `POST /api/close_tickets` — close a requested subset by ticket.
- `GET /api/positions`, `GET /api/positions/all`.
- `GET /api/stl`, `POST /api/stl/compute`, `POST /api/stl/prune`, `POST /api/stl/prune_all`, `DELETE /api/stl/run/{id}`.
- `GET /api/news`, `POST /api/news/backfill_forex`, `POST /api/news/analyze`.
- `GET /api/health/freshness`, `GET /api/tech/freshness`, `GET|POST /api/health/run`, `GET /api/health/runs`.
- `POST /api/preferences` and related preference retrieval.
- `GET /api/ai/trade_plan`.
- `GET /api/accounts`, `GET /api/account/current`, `POST /api/account/login`.
- `GET /ws/updates`.

## 🧪 Examples
```bash
# Fetch 500 H1 bars for XAUUSD
curl "http://localhost:8888/api/fetch?symbol=XAUUSD&tf=H1&count=500"

# Read 200 bars from DB
curl "http://localhost:8888/api/data?symbol=XAUUSD&tf=H1&limit=200"

# Run SMA signal calculation
curl "http://localhost:8888/api/strategy/run?symbol=XAUUSD&tf=H1&fast=20&slow=50"

# Close current symbol long positions
curl -X POST "http://localhost:8888/api/close" -d "symbol=XAUUSD&side=long"

# Close all short positions across symbols
curl -X POST "http://localhost:8888/api/close?scope=all&side=short"
```

## 🗄️ Database & Schema
See `sql/schema.sql`.

Highlights:
- Composite PK `(symbol, timeframe, ts)` in `ohlc_bars` prevents duplicate bars.
- Ingestion uses `ON CONFLICT ... DO UPDATE`.
- Additional tables support STL runs/components, preferences, news articles, health runs, account series, closed deals, and signal/order-plan linking.

## 🛡️ Trading Controls & Safety
- Environment guard: `TRADING_ENABLED=0` by default disables order placement from manual/plan execution endpoints.
- Header `Auto` behavior in UI schedules strategy checks; it does not bypass trading safety gates.
- Close operations are intentionally allowed even when trading is disabled.
- Safe-max and symbol/kind weighting are used in execution flows to limit exposure.

## 📈 STL Auto-Compute Toggle
- STL auto-compute is controlled per symbol x timeframe via the `Auto STL` switch in the STL panel.
- Default is OFF to reduce UI lag on large/slow contexts.
- When ON, missing/stale STL can auto-compute; otherwise use manual recalc controls.
- State persists via `/api/preferences` keys like `stl_auto_compute:SYMBOL:TF` and also local storage for faster startup.

## 🧷 Remembering Last Selection
- Server persists `last_symbol`, `last_tf`, `last_count` and injects defaults into templates.
- UI also stores `last_symbol`/`last_tf` in `localStorage`.
- `/?reset=1` ignores stored preferences for that page load.
- `PIN_DEFAULTS_TO_XAU_H1=1` can force startup defaults.

## 🤖 AI Trade Plan Prompt Context
When requesting an AI trade plan, the server ensures fresh Basic Health and Tech Snapshot runs exist for the current symbol/timeframe (creating them if missing), then builds prompt context from:
- Basic health block,
- Tech AI block,
- Live technical snapshot block.

## 🧰 Development Notes
- Primary runtime dependencies: `tornado`, `asyncpg`, `MetaTrader5`, `numpy`, `python-dotenv`, `requests`, `httpx`, `statsmodels`, `openai`.
- No formal automated test suite is currently configured; smoke tests and manual UI validation are the active workflow.
- Recommended smoke tests:
  - `python scripts/test_mixed_ai.py`
  - `python scripts/test_fmp.py`
  - `python scripts/test_fmp_endpoints.py`
- Manual checks to run before pushing:
  - pan/zoom sync,
  - STL overlay/period line behavior,
  - trading controls (including close safety behavior),
  - news panel fallback behavior.

## 🧯 Troubleshooting
| Symptom | Action |
|---|---|
| MT5 initialize failed | Set `MT5_PATH` to exact `terminal64.exe`, then run terminal manually at least once |
| MT5 login failed | Ensure `MT5_SERVER` exactly matches terminal server string, or omit credentials and reuse an active session |
| No data for symbol | Verify broker symbol naming and Market Watch visibility (`XAUUSD`, `XAUUSD.a`, `GOLD`, etc.) |
| Postgres connection issues | Verify `DATABASE_URL`, then run `psql "$DATABASE_URL" -c 'select 1;'` |
| Slow or stale UI analytics | Disable auto STL on heavy pairs/TFs and recalc manually |

## 🛣️ Roadmap
- Expand `i18n/` runtime assets beyond README-based multilingual docs.
- Add formal automated tests (API + integration + UI smoke automation).
- Improve deployment packaging and reproducible environment profiles.
- Continue refining AI plan validation and execution safeguards.

## 🤝 Contributing
- Keep patches small and scoped.
- Use clear commit prefixes where applicable (for example: `UI: ...`, `Server: ...`, `References: ...`).
- Avoid unrelated formatting churn.
- Include screenshots/GIFs for UI changes when relevant.
- Run smoke tests and local browser checks before PRs.

## ❤️ Support / Sponsor
Sponsor and support links are configured in `.github/FUNDING.yml`:
- GitHub Sponsors: https://github.com/sponsors/lachlanchen
- Lazying.art: https://lazying.art
- Chat: https://chat.lazying.art
- OnlyIdeas: https://onlyideas.art

## 📚 References
- `references/ai-trader-overview.md`
- `references/database_setup_postgres.md`
- `references/mt5_python_setup_ubuntu.md`
- `references/mt4_vs_mt5.md`
- `references/llm_trading_system.md`
- `references/release_deploy.md`
- `references/pnl_debugging.md`

## 📄 License
No `LICENSE` file is present in this repository as of 2026-02-28.

Assumption: licensing terms are currently unspecified in-repo; preserve this note until maintainers add an explicit license file.
