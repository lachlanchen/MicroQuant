[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


<p align="center">
  <img src="https://raw.githubusercontent.com/lachlanchen/lachlanchen/main/logos/banner.png" alt="LazyingArt banner" />
</p>

# MetaTrader QT - Quantitativer Trading-Starter (Micro-Quant-Philosophie)

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

## 🧭 Überblick
Bei Micro Quant geht es weniger um glänzende Dashboards als um einen wiederholbaren Trading-Logik-Stack: OHLC-Daten werden aus MetaTrader 5 gezogen, in Postgres persistiert und systematische Entscheidungen über geschichtete, KI-gestützte Signale bewertet (Basic News, Tech Snapshot, Trade-Pläne und STL-Overlays). Die UI spiegelt diese Philosophie durch Alignment-Toggles, begründete Schließungen, persistierte Präferenzen und ein datenreiches Ausführungs-Panel wider, sodass der Server periodische oder modale Trading-Flows sicher ausführen kann, während du Logs und Evidenz prüfst.

Die statische Landingpage (Quant by Lazying.art) liegt unter `docs/` und wird über GitHub Pages veröffentlicht (`trade.lazying.art` via `docs/CNAME`). Das Repository enthält außerdem Referenzen für AI-Trade-Plan-Prompts, Integrationshinweise und operative Dokumentation.

### Auf einen Blick
| Bereich | Funktion |
|---|---|
| Daten | Zieht MT5-OHLC und schreibt per Upsert nach PostgreSQL |
| Analytik | Führt Health/News/Tech- und STL-Workflows aus |
| Entscheidungslogik | Erstellt KI-Trade-Pläne aus geschichtetem Kontext |
| Ausführung | Führt Trading-Flows hinter Sicherheitsleitplanken aus bzw. steuert sie |
| UI | Desktop-/Mobile-Ansichten mit synchronisierten Chart-Workflows |

## 🧠 Kernphilosophie
- **Wahrheitskette**: Basic-News-Checks (Text + Scores) und Tech-Snapshots (schwerer technischer Kontext + STL) speisen einen einzelnen KI-Trade-Plan pro Symbol/Timeframe. Periodische Auto-Läufe und manuelle modale Läufe teilen sich dieselbe Pipeline und dieselben Begründungs-Logs.
- **Alignment-first-Ausführung**: Accept-Tech/Hold-Neutral-Toggles, Ignore-Basics-Switch und Partial-Close-Wrapper sorgen dafür, dass Tech bewusst befolgt wird, Gegenpositionen bei Bedarf vor neuen Einstiegen geschlossen werden und unnötige Exits minimiert sind.
- **Unveränderliche Daten**: Jeder Fetch schreibt mit `ON CONFLICT`-Hygiene nach Postgres, während `/api/data` bereinigte Reihen für die UI liest. Präferenzen (Auto-Volumes, `close_fraction`, Hide-Tech-Toggles, STL-Auto-Compute) werden über `/api/preferences` persistiert.
- **Safety-first-Trading**: `TRADING_ENABLED` und `safe_max` erzwingen Berechtigungen für manuelle/automatische Abläufe. `/api/close` und periodische Runner können Schließungsgründe (Tech neutral, Fehlanpassung usw.) zur Nachvollziehbarkeit protokollieren.

## ✨ Features
- MT5-OHLC-Ingestion nach Postgres (`/api/fetch`, `/api/fetch_bulk`).
- Chart-UI unter `/` (Desktop) plus `/app` (Mobile), mit Chart.js + Lightweight Charts in Templates.
- STL-Decomposition-Workflows (`/api/stl`, `/api/stl/compute`, prune/delete-Endpunkte).
- News-Ingestion und Analyse (`/api/news`, `/api/news/backfill_forex`, `/api/news/analyze`).
- KI-Workflow-Orchestrierung (`/api/health/run`, `/api/health/runs`, `/api/ai/trade_plan`).
- Manuelle Trade-Ausführung (`/api/trade`, `/api/trade/execute_plan`) abgesichert durch `TRADING_ENABLED`.
- Positions-/Risiko-Operationen (`/api/positions*`, `/api/close`, `/api/close_tickets`) mit erlaubten Close-Operationen aus Sicherheitsgründen.
- WebSocket-Update-Stream unter `/ws/updates`.

## 🗂️ Projektstruktur
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

## ✅ Voraussetzungen
- Ubuntu/Linux oder Windows.
- MT5 installiert und erreichbar (`terminal64.exe`), wobei das Terminal läuft/eingeloggt ist.
- Python 3.10+ (3.11 empfohlen für MetaTrader5-Kompatibilität).
- PostgreSQL-Instanz.

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

Hilfsskripte:
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

## ⚙️ Konfiguration
Kopiere `.env.example` nach `.env` und passe die Werte an.

### Kernvariablen
| Variable | Zweck |
|---|---|
| `DATABASE_URL` | Bevorzugter PostgreSQL-DSN |
| `DATABASE_MT_URL` | Fallback-DSN, wenn `DATABASE_URL` nicht gesetzt ist |
| `DATABASE_QT_URL` | Sekundärer Fallback-DSN |
| `MT5_PATH` | Pfad zu `terminal64.exe` (Wine oder nativ) |
| `MT5_LOGIN` / `MT5_PASSWORD` / `MT5_SERVER` | Optional, wenn die MT5-Terminal-Session bereits eingeloggt ist |
| `PORT` | Server-Port (Standard `8888`) |

### Optionale Variablen
- `FMP_API_KEY`, `ALPHAVANTAGE_API_KEY` für News-Anreicherung.
- `TRADING_ENABLED` (`0` Standard, auf `1` setzen, um Order-Platzierungsendpunkte zu erlauben).
- `TRADING_VOLUME` (Standardvolumen für manuelles Trading).
- `AUTO_FETCH`, `AUTO_FETCH_SYMBOL`, `AUTO_FETCH_TF`, `AUTO_FETCH_COUNT`, `AUTO_FETCH_SEC`.
- `PIN_DEFAULTS_TO_XAU_H1=1`, um UI-Startstandard für Symbol/Timeframe zu erzwingen.
- `LOG_LEVEL`, `LOG_BACKFILL`, plus account-/poll-bezogene Präferenzen über `/api/preferences` und Umgebung.

Hinweise:
- `MT5_PATH` sollte auf deine `terminal64.exe` unter dem Wine-Präfix deiner MT5-Installation zeigen.
- Du kannst MT5-Credentials weglassen, wenn die Terminal-Session bereits eingeloggt ist; die App versucht, diese Session wiederzuverwenden.

## 🚀 Verwendung

### Server starten
```bash
python -m app.server
```

### UI öffnen
- Desktop-UI: `http://localhost:8888/`
- Mobile-UI: `http://localhost:8888/app`

### Häufiger Workflow
1. Bars von MT5 abrufen und in Postgres persistieren.
2. Bars aus der DB fürs Charting lesen.
3. Health-/Tech-/News-Analysen ausführen.
4. KI-Trade-Plan generieren.
5. Positionen unter Sicherheitsleitplanken ausführen oder schließen.

## 🔌 API-Endpunkte (praktisch)
- `GET /api/fetch?symbol=XAUUSD&tf=H1&count=500[&mode=inc|full][&persist=1]`
  - Von MT5 abrufen und per Upsert in die DB schreiben.
  - Bei `persist=1` speichert der Server `last_symbol/last_tf/last_count` als Defaults; Bulk-/Hintergrund-Fetches sollten dies auslassen, um UI-Auswahlen nicht zu überschreiben.
- `GET /api/fetch_bulk` — Bulk-/geplante Ingestion.
- `GET /api/data?symbol=XAUUSD&tf=H1&limit=500` — Chartdaten aus der DB lesen.
- `GET /api/strategy/run?symbol=XAUUSD&tf=H1&fast=20&slow=50`
  - Führt SMA(20/50)-Crossover aus und liefert Signal-Payload zurück.
  - Wichtiger Implementierungshinweis: strategy-getriebene Order-Platzierung über diesen Endpunkt ist im Servercode derzeit deaktiviert; Order-Ausführung erfolgt über Trade-Endpunkte.
- `POST /api/trade` — manuelles Buy/Sell aus der UI, gesteuert durch `TRADING_ENABLED`.
- `POST /api/trade/execute_plan` — führt einen generierten Plan aus, inklusive Pre-Close- und Stop-Distance-Checks.
- `POST /api/close` — Positionen glattstellen (aus Sicherheitsgründen auch bei `TRADING_ENABLED=0` erlaubt):
  - Aktuelles Symbol: Form-Body `symbol=...`; optional `side=long|short|both`.
  - Alle Symbole: `?scope=all` und optional `&side=...`.
  - Antwort enthält `closed_count` und Ergebnisse pro Ticket.
- `POST /api/close_tickets` — gewünschte Teilmenge nach Ticket schließen.
- `GET /api/positions`, `GET /api/positions/all`.
- `GET /api/stl`, `POST /api/stl/compute`, `POST /api/stl/prune`, `POST /api/stl/prune_all`, `DELETE /api/stl/run/{id}`.
- `GET /api/news`, `POST /api/news/backfill_forex`, `POST /api/news/analyze`.
- `GET /api/health/freshness`, `GET /api/tech/freshness`, `GET|POST /api/health/run`, `GET /api/health/runs`.
- `POST /api/preferences` und zugehörige Präferenzabfragen.
- `GET /api/ai/trade_plan`.
- `GET /api/accounts`, `GET /api/account/current`, `POST /api/account/login`.
- `GET /ws/updates`.

## 🧪 Beispiele
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

## 🗄️ Datenbank & Schema
Siehe `sql/schema.sql`.

Highlights:
- Zusammengesetzter PK `(symbol, timeframe, ts)` in `ohlc_bars` verhindert doppelte Bars.
- Ingestion nutzt `ON CONFLICT ... DO UPDATE`.
- Zusätzliche Tabellen unterstützen STL-Läufe/-Komponenten, Präferenzen, News-Artikel, Health-Runs, Account-Serien, geschlossene Deals und Signal-/Order-Plan-Verknüpfung.

## 🛡️ Trading-Steuerung & Sicherheit
- Umgebungsleitplanke: `TRADING_ENABLED=0` deaktiviert standardmäßig Order-Platzierung aus manuellen/Plan-Ausführungs-Endpunkten.
- Header-`Auto`-Verhalten in der UI plant Strategieprüfungen; es umgeht keine Trading-Sicherheits-Gates.
- Close-Operationen sind bewusst auch dann erlaubt, wenn Trading deaktiviert ist.
- Safe-max sowie Symbol-/Kind-Gewichtung werden in Ausführungsflüssen genutzt, um Exposure zu begrenzen.

## 📈 STL-Auto-Compute-Toggle
- STL-Auto-Compute wird pro Symbol x Timeframe über den Schalter `Auto STL` im STL-Panel gesteuert.
- Standard ist AUS, um UI-Lag in großen/langsamen Kontexten zu reduzieren.
- Wenn EIN, kann fehlendes/veraltetes STL automatisch berechnet werden; andernfalls manuelle Recalc-Steuerung nutzen.
- Zustand wird über `/api/preferences`-Schlüssel wie `stl_auto_compute:SYMBOL:TF` persistiert und zusätzlich im Local Storage für schnelleren Start.

## 🧷 Letzte Auswahl merken
- Server persistiert `last_symbol`, `last_tf`, `last_count` und injiziert Defaults in Templates.
- UI speichert zusätzlich `last_symbol`/`last_tf` in `localStorage`.
- `/?reset=1` ignoriert gespeicherte Präferenzen für diesen Seitenaufruf.
- `PIN_DEFAULTS_TO_XAU_H1=1` kann Start-Defaults erzwingen.

## 🤖 Kontext für AI-Trade-Plan-Prompt
Beim Anfordern eines KI-Trade-Plans stellt der Server sicher, dass frische Basic-Health- und Tech-Snapshot-Läufe für das aktuelle Symbol/Timeframe vorhanden sind (und erstellt sie bei Bedarf), und baut dann den Prompt-Kontext aus:
- Basic-Health-Block,
- Tech-AI-Block,
- Live-Technical-Snapshot-Block.

## 🧰 Entwicklungshinweise
- Primäre Runtime-Abhängigkeiten: `tornado`, `asyncpg`, `MetaTrader5`, `numpy`, `python-dotenv`, `requests`, `httpx`, `statsmodels`, `openai`.
- Aktuell ist keine formale automatisierte Test-Suite konfiguriert; Smoke-Tests und manuelle UI-Validierung sind der aktive Workflow.
- Empfohlene Smoke-Tests:
  - `python scripts/test_mixed_ai.py`
  - `python scripts/test_fmp.py`
  - `python scripts/test_fmp_endpoints.py`
- Manuelle Checks vor dem Push:
  - Pan/Zoom-Sync,
  - STL-Overlay-/Period-Line-Verhalten,
  - Trading-Steuerung (inklusive Close-Sicherheitsverhalten),
  - Fallback-Verhalten des News-Panels.

## 🧯 Fehlerbehebung
| Symptom | Aktion |
|---|---|
| MT5 initialize failed | `MT5_PATH` auf exakte `terminal64.exe` setzen und Terminal mindestens einmal manuell starten |
| MT5 login failed | Sicherstellen, dass `MT5_SERVER` exakt der Server-Zeichenkette im Terminal entspricht, oder Credentials weglassen und aktive Session wiederverwenden |
| No data for symbol | Broker-Symbolnamen und Sichtbarkeit in Market Watch prüfen (`XAUUSD`, `XAUUSD.a`, `GOLD` usw.) |
| Postgres connection issues | `DATABASE_URL` prüfen und dann `psql "$DATABASE_URL" -c 'select 1;'` ausführen |
| Slow or stale UI analytics | Auto-STL bei schweren Pairs/TFs deaktivieren und manuell neu berechnen |

## 🛣️ Roadmap
- `i18n/`-Runtime-Assets über README-basierte mehrsprachige Doku hinaus erweitern.
- Formale automatisierte Tests ergänzen (API + Integration + UI-Smoke-Automation).
- Deployment-Packaging und reproduzierbare Umgebungsprofile verbessern.
- KI-Plan-Validierung und Ausführungsschutz weiter verfeinern.

## 🤝 Mitwirken
- Patches klein und fokussiert halten.
- Klare Commit-Präfixe verwenden, wo sinnvoll (zum Beispiel: `UI: ...`, `Server: ...`, `References: ...`).
- Unzusammenhängendes Formatierungsrauschen vermeiden.
- Bei UI-Änderungen, wenn relevant, Screenshots/GIFs beilegen.
- Vor PRs Smoke-Tests und lokale Browser-Checks ausführen.

## ❤️ Support / Sponsoring
Sponsor- und Support-Links sind in `.github/FUNDING.yml` konfiguriert:
- GitHub Sponsors: https://github.com/sponsors/lachlanchen
- Lazying.art: https://lazying.art
- Chat: https://chat.lazying.art
- OnlyIdeas: https://onlyideas.art

## 📚 Referenzen
- `references/ai-trader-overview.md`
- `references/database_setup_postgres.md`
- `references/mt5_python_setup_ubuntu.md`
- `references/mt4_vs_mt5.md`
- `references/llm_trading_system.md`
- `references/release_deploy.md`
- `references/pnl_debugging.md`

## 📄 Lizenz
In diesem Repository ist mit Stand 2026-02-28 keine `LICENSE`-Datei vorhanden.

Annahme: Die Lizenzbedingungen sind derzeit im Repository nicht explizit festgelegt; diese Notiz beibehalten, bis die Maintainer eine ausdrückliche Lizenzdatei hinzufügen.
