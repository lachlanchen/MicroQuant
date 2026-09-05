[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# MetaTrader QT - Quantitatives Trading-Startset (Micro Quant Philosophie)

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Backend](https://img.shields.io/badge/Backend-Tornado-2d7cbf)
![Database](https://img.shields.io/badge/Database-PostgreSQL-336791?logo=postgresql&logoColor=white)
![Broker](https://img.shields.io/badge/Broker%20Bridge-MetaTrader5-1f6feb)
![UI](https://img.shields.io/badge/UI-Lightweight%20Charts%20%2B%20Chart.js-0ea5e9)
![Status](https://img.shields.io/badge/README-Expanded-success)
![GitHub%20Stars](https://img.shields.io/github/stars/lachlanchen/MicroQuant?style=for-the-badge&logo=github&logoColor=white&labelColor=0f172a&color=0ea5e9)
![GitHub%20Issues](https://img.shields.io/github/issues/lachlanchen/MicroQuant?style=for-the-badge&logo=github&logoColor=white&labelColor=0f172a&color=ef4444)

## 🎯 Project Snapshot

| Fokus | Stack |
|---|---|
| Laufzeit | Tornado + asyncpg + WebSocket |
| Trading | MetaTrader5 + KI/Technik/News-Kontext in Schichten |
| Speicherung | PostgreSQL mit deterministischer Upsert-Pipeline |
| Deployment | PWA-Assets + browser-first Desktop-/Mobile-UI |

## Inhaltsverzeichnis
- [Screenshot](#-screenshot)
- [Überblick](#-überblick)
- [Kernphilosophie](#-kernphilosophie)
- [Funktionen](#-funktionen)
- [Projektstruktur](#-projektstruktur)
- [Voraussetzungen](#-voraussetzungen)
- [Installation](#-installation)
- [Konfiguration](#️-konfiguration)
- [Nutzung](#-nutzung)
- [API-Endpunkte (praktisch)](#-api-endpunkte-praktisch)
- [Beispiele](#-beispiele)
- [Datenbank & Schema](#-datenbank--schema)
- [Handelssteuerung & Sicherheit](#️-handelssteuerung--sicherheit)
- [STL-Auto-Compute-Toggle](#-stl-auto-compute-toggle)
- [Letzte Auswahl merken](#-letzte-auswahl-merken)
- [KI-Handelsplan-Kontext](#️-ki-handelsplan-kontext)
- [Entwicklungsnotizen](#-entwicklungsnotizen)
- [Fehlerbehebung](#-fehlerbehebung)
- [Roadmap](#-roadmap)
- [Mitwirken](#-mitwirken)
- [Referenzen](#-referenzen)
- [Support](#️-support)
- [Lizenz](#-lizenz)

## 📸 Screenshot
![Micro Quant UI](figures/demos/micro-quant-ui.png)

[![DATA Source](https://img.shields.io/badge/Data_Source-RoboForex-0060ff?style=for-the-badge&labelColor=0a4eb3)](https://my.roboforex.com/en/?a=efx)

Affiliate-Hinweis: Die RoboForex-Schaltfläche oben enthält meinen Partnercode (`efx`), daher kann ich eine Provision für die Handelsaktivität vermittelter Nutzer erhalten. Die Nutzung ist freiwillig und hat keinen Einfluss auf die Funktionsweise von MicroQuant. Der Handel mit Hebelwirkung birgt ein hohes Verlustrisiko; dieses Projekt ist experimentelle Software und weder Anlageberatung noch ein Renditeversprechen. Siehe das [aktuelle Partnerprogramm](https://roboforex.com/partner-program/) und die [Risikohinweise](https://roboforex.com/about/company/documents/).

## 🧭 Überblick
Micro Quant steht weniger für glänzende Dashboards, sondern für eine wiederholbare Handelslogik: Es bezieht OHLC-Daten aus MetaTrader 5, speichert sie in PostgreSQL und bewertet Entscheidungen systematisch über KI-gestützte, gestapelte Signale (Basic News, Tech Snapshot, Handelspläne und STL-Overlays). Die UI setzt diese Philosophie um mit Ausrichtungs-Switches, begründbaren Schließungen, gespeicherten Präferenzen und einem datenreichen Ausführungsbereich, sodass der Server sichere periodische oder modale Handelsabläufe steuern kann, während Sie Logs und Nachweise prüfen.

Die statische Landingpage (Quant by Lazying.art) liegt unter `docs/` und wird über GitHub Pages bereitgestellt (`quant.lazying.art` über `docs/CNAME`). Das Repository enthält zusätzlich Referenzen zu KI-Handelsplan-Prompts, Integrationshinweisen und Betriebsdokumentation.

### Kurzüberblick
| Bereich | Funktion |
|---|---|
| Daten | Lädt MT5-OHLC und schreibt per Upsert nach PostgreSQL |
| Analyse | Führt Health-/News-/Tech-Abläufe sowie STL-Workflows aus |
| Entscheidungslogik | Erstellt KI-Handelspläne aus mehrstufigem Kontext |
| Ausführung | Führt Handelsabläufe hinter Sicherheits-Gates aus |
| UI | Desktop-/Mobile-Ansichten mit synchronisierten Chart-Workflows |

## 🧠 Kernphilosophie
- **Truth-Chain-Ansatz**: Basic-News-Prüfungen (Text + Scores) und Tech-Snapshots (umfangreicher technischer Kontext + STL) liefern gemeinsam einen einzelnen KI-Handelsplan je Symbol/Zeitrahmen. Periodische Auto-Läufe und manuelle Modal-Läufe nutzen dieselbe Pipeline und dieselben Begründungs-Logs.
- **Ausrichtungsbasierte Ausführung**: Accept-Tech/Hold-Neutral-Schalter, Ignore-Basics-Umschaltung und Partial-Close-Wrapper stellen sicher, dass Tech-Regeln bewusst befolgt werden, Gegentransaktionen bei Bedarf vor neuen Entries geschlossen werden und unnötige Ausstiege reduziert werden.
- **Unveränderliche Datenbasis**: Jeder Abruf schreibt in Postgres mit `ON CONFLICT`-Logik, während `/api/data` bereinigte Reihen für die UI liest. Präferenzen (`auto`-Einstellungen, `close_fraction`, Hide-Tech-Umschalter, STL Auto-Compute) werden via `/api/preferences` persistiert.
- **Sicherheitsorientiertes Trading**: `TRADING_ENABLED` und `safe_max` steuern Berechtigungen für manuelle und automatische Abläufe. `/api/close` und periodische Runner protokollieren Schließgründe (Tech neutral, Fehlanpassung usw.) für vollständige Nachvollziehbarkeit.

## ✨ Funktionen
- MT5-OHLC-Ingestion nach Postgres (`/api/fetch`, `/api/fetch_bulk`).
- Chart-UI unter `/` (Desktop) plus `/app` (Mobile), mit Chart.js + Lightweight Charts in den Templates.
- STL-Dekompositionsabläufe (`/api/stl`, `/api/stl/compute`, Endpunkte zum Entfernen/Löschen).
- News-Ingestion und -Analyse (`/api/news`, `/api/news/backfill_forex`, `/api/news/analyze`).
- KI-Orchestrierung (`/api/health/run`, `/api/health/runs`, `/api/ai/trade_plan`).
- Manuelle Ausführung (`/api/trade`, `/api/trade/execute_plan`), abgesichert durch `TRADING_ENABLED`.
- Risiko-Operationen für Positionen (`/api/positions*`, `/api/close`, `/api/close_tickets`) mit expliziter Sicherheitslogik bei Schließvorgängen.
- WebSocket-Update-Stream unter `/ws/updates` für Echtzeit-Hinweise und Refresh-Signale.
- PWA-/statische Assets für ein installierbares Dashboard.

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
├── i18n/                        # Translated docs (currently language only)
├── .github/FUNDING.yml          # Sponsor/support metadata
└── README.md + README.*.md      # Canonical + multilingual docs
```

## ✅ Voraussetzungen
- Ubuntu/Linux oder Windows mit Terminalzugriff.
- MetaTrader 5 installiert (`terminal64.exe`) und bei Bedarf mit Login.
- Python 3.10+ (Python 3.11 empfohlen für breitere Kompatibilität mit MetaTrader5-Wheels).
- PostgreSQL-Instanz, die vom App-Server erreichbar ist.
- Optionale API-Schlüssel für News-Anbieter:
  - FMP
  - Alpha Vantage

## 🛠️ Installation

### Windows (PowerShell)
```powershell
# 1) Virtual Environment mit Python 3.11 erstellen (MetaTrader5 liefert noch keine Wheels für 3.13)
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt

# 2) Environment konfigurieren
Copy-Item .env.example .env
# .env bearbeiten und DATABASE_URL, MT5_PATH (z. B. C:\Program Files\MetaTrader 5\terminal64.exe) sowie MT5-Demo-Zugangsdaten setzen
# Umgebung für diese Sitzung laden
Get-Content .env | Where-Object { $_ -and $_ -notmatch '^#' } | ForEach-Object { $n,$v = $_ -split '=',2; [Environment]::SetEnvironmentVariable($n, $v, 'Process') }

# 3) App starten
python -m app.server
# Öffnen Sie http://localhost:8888
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

# Alternativ: Lokale Python-3.11-Umgebung (falls globale Version neuer ist)
# Erfordert python3.11 im System
# sudo apt install python3.11 python3.11-venv
bash scripts/bootstrap_venv311.sh
source .venv311/bin/activate

# DB (eigene User-/Passwortangaben je nach Bedarf)
# createdb -h localhost -p 5432 -U lachlan metatrader_db

# Env konfigurieren
cp .env.example .env
# .env mit MT5-Pfad und Zugriffsdaten bearbeiten
test -f .env && set -a; source .env; set +a

# App starten
python -m app.server
# Öffnen Sie http://localhost:8888
```

## ⚙️ Konfiguration
Kopieren Sie `.env.example` nach `.env` und passen Sie die Werte an.

### Kerndaten
| Variable | Zweck |
|---|---|
| `DATABASE_URL` | Bevorzugte PostgreSQL-DSN |
| `DATABASE_MT_URL` | Fallback-DSN falls `DATABASE_URL` nicht gesetzt ist |
| `DATABASE_QT_URL` | Zweiter Fallback-DSN |
| `MT5_PATH` | Pfad zu `terminal64.exe` (Wine oder native Ausführung) |
| `MT5_LOGIN` / `MT5_PASSWORD` / `MT5_SERVER` | Optional, wenn die MT5-Terminalsitzung bereits angemeldet ist |
| `PORT` | Server-Port (Standard `8888`) |

### Optionale Variablen
- `FMP_API_KEY`, `ALPHAVANTAGE_API_KEY` für News-Anreicherung.
- `TRADING_ENABLED` (`0` Standard, auf `1` setzen, um Endpunkte für Orderplatzierung zu aktivieren).
- `TRADING_VOLUME` (Standardvolumen für manuelle Aufträge).
- `AUTO_FETCH`, `AUTO_FETCH_SYMBOL`, `AUTO_FETCH_TF`, `AUTO_FETCH_COUNT`, `AUTO_FETCH_SEC`.
- `PIN_DEFAULTS_TO_XAU_H1=1`, um Standard-Symbol/Zeitrahmen beim UI-Start zu erzwingen.
- `LOG_LEVEL`, `LOG_BACKFILL` sowie account-/poll-bezogene Einstellungen über `/api/preferences` und Umgebungswerte.

Hinweise:
- `MT5_PATH` sollte auf das `terminal64.exe`-Binary im verwendeten Wine-Prefix zeigen.
- Sie können MT5-Anmeldedaten weglassen, wenn die Terminalsitzung bereits aktiv ist; die App versucht, diese Session wiederzuverwenden.

## 🚀 Nutzung

### Server starten
```bash
python -m app.server
```

### UI öffnen
- Desktop-UI: `http://localhost:8888/`
- Mobile UI: `http://localhost:8888/app`

### Schlüsselte URLs
| Oberfläche | URL | Zweck |
|---|---|---|
| Desktop | `http://localhost:8888/` | Candlestick-Chart und Desktop-Workflow-Steuerung |
| Mobile | `http://localhost:8888/app` | Touch-first-Layout mit kompakten Steuerelementen |
| API Health | `http://localhost:8888/api/health/freshness` | Schneller Smoke-Check für Daten + Betriebsbereitschaft |

### Typischer Ablauf
1. Kerzen von MT5 holen und in Postgres speichern.
2. Kerzen aus der DB für Charts lesen.
3. Health-/Tech-/News-Analysen ausführen.
4. KI-Handelsplan erzeugen.
5. Positionen unter Sicherheitsregeln ausführen oder schließen.

## 🔌 API-Endpunkte (praktisch)
- `GET /api/fetch?symbol=XAUUSD&tf=H1&count=500[&mode=inc|full][&persist=1]`
  - Lädt Daten aus MT5 und führt Upsert in die DB durch.
  - Bei `persist=1` speichert der Server `last_symbol/last_tf/last_count` als Standard; Bulk-/Hintergrundabrufe sollten das vermeiden, um UI-Auswahlen nicht zu überschreiben.
- `GET /api/fetch_bulk` — Massenerfassung / geplanter Import.
- `GET /api/data?symbol=XAUUSD&tf=H1&limit=500` — Chartdaten aus der DB lesen.
- `GET /api/strategy/run?symbol=XAUUSD&tf=H1&fast=20&slow=50`
  - Führt SMA(20/50)-Crossover aus und liefert das Signal-Payload.
  - Wichtig: Strategiegetriebene Orderausführung über diesen Endpoint ist derzeit im Servercode deaktiviert; Ausführungen laufen über Trade-Endpunkte.
- `POST /api/trade` — manueller Buy/Sell aus der UI, abgesichert durch `TRADING_ENABLED`.
- `POST /api/trade/execute_plan` — führt einen erzeugten Plan aus, inklusive Pre-Close- und Stop-Distanzprüfung.
- `POST /api/close` — Positionen schließen (auch bei `TRADING_ENABLED=0` aus Sicherheitsgründen erlaubt):
  - Aktuelles Symbol: Formularkörper `symbol=...`; optional `side=long|short|both`.
  - Alle Symbole: `?scope=all` und optional `&side=...`.
  - Antwort enthält `closed_count` sowie Ergebnisse je Ticket.
- `POST /api/close_tickets` — schließt eine angefragte Teilmenge anhand von Tickets.
- `GET /api/positions`, `GET /api/positions/all`.
- `GET /api/stl`, `POST /api/stl/compute`, `POST /api/stl/prune`, `POST /api/stl/prune_all`, `DELETE /api/stl/run/{id}`.
- `GET /api/news`, `POST /api/news/backfill_forex`, `POST /api/news/analyze`.
- `GET /api/health/freshness`, `GET /api/tech/freshness`, `GET|POST /api/health/run`, `GET /api/health/runs`.
- `POST /api/preferences` und zugehöriger Abruf.
- `GET /api/ai/trade_plan`.
- `GET /api/accounts`, `GET /api/account/current`, `POST /api/account/login`.
- `GET /ws/updates`.

## 🧪 Beispiele
```bash
# 500 H1-Kerzen für XAUUSD abrufen
curl "http://localhost:8888/api/fetch?symbol=XAUUSD&tf=H1&count=500"

# 200 Bars aus der DB lesen
curl "http://localhost:8888/api/data?symbol=XAUUSD&tf=H1&limit=200"

# SMA-Signalberechnung ausführen
curl "http://localhost:8888/api/strategy/run?symbol=XAUUSD&tf=H1&fast=20&slow=50"

# Long-Positionen des aktuellen Symbols schließen
curl -X POST "http://localhost:8888/api/close" -d "symbol=XAUUSD&side=long"

# Alle Short-Positionen über alle Symbole schließen
curl -X POST "http://localhost:8888/api/close?scope=all&side=short"
```

## 🗄️ Datenbank & Schema
Siehe `sql/schema.sql`.

Wichtige Punkte:
- Der zusammengesetzte Primärschlüssel `(symbol, timeframe, ts)` in `ohlc_bars` verhindert doppelte Kerzen.
- Die Ingestion verwendet `ON CONFLICT ... DO UPDATE`.
- Zusatz-Tabellen unterstützen STL-Läufe/-Komponenten, Präferenzen, News-Artikel, Health-Runs, Kontoreihen, geschlossene Deals sowie Signal-/Orderplan-Verknüpfungen.

## 🛡️ Handelssteuerung & Sicherheit
- Umgebungsschutz: `TRADING_ENABLED=0` deaktiviert standardmäßig die Orderplatzierung über manuelle und Plan-Ausführungs-Endpoints.
- Der Header `Auto` in der UI plant Strategieprüfungen; er umgeht nicht die Sicherheitsgates für Trades.
- Schließvorgänge sind absichtlich auch erlaubt, wenn Trading deaktiviert ist.
- Safe-max und Symbol-/Typ-Gewichtung werden in Ausführungsabläufen eingesetzt, um das Exposure zu begrenzen.

## 📈 STL Auto-Compute Toggle
- STL Auto-Compute wird pro Symbol und Zeitrahmen über den Schalter `Auto STL` im STL-Panel gesteuert.
- Standard ist AUS, um UI-Lags bei großen/langsamen Kontexten zu reduzieren.
- Bei aktivem Schalter können fehlende oder veraltete STL automatisch berechnet werden; andernfalls verwenden Sie manuelle Neuberechnung.
- Der Status wird über `/api/preferences`-Keys wie `stl_auto_compute:SYMBOL:TF` sowie `localStorage` für schnelleren Start gespeichert.

## 🧷 Letzte Auswahl merken
- Der Server speichert `last_symbol`, `last_tf`, `last_count` und setzt diese Defaults in Templates ein.
- Die UI speichert ebenfalls `last_symbol`/`last_tf` in `localStorage`.
- `/?reset=1` ignoriert gespeicherte Präferenzen für diesen Seitenaufruf.
- `PIN_DEFAULTS_TO_XAU_H1=1` kann Start-Defaults erzwingen.

## 🤖 KI-Handelsplan-Kontext
Beim Abruf eines KI-Handelsplans stellt der Server sicher, dass aktuelle Basic Health- und Tech Snapshot-Läufe für das aktuelle Symbol/Zeitrahmen vorhanden sind (bei Bedarf werden sie erstellt), bevor der Prompt-Kontext aus folgenden Blöcken aufgebaut wird:
- Basic-Health-Block,
- Tech-AI-Block,
- Live-Tech-Snapshot-Block.

## 🧰 Entwicklungsnotizen
- Zentrale Laufzeitabhängigkeiten: `tornado`, `asyncpg`, `MetaTrader5`, `numpy`, `python-dotenv`, `requests`, `httpx`, `statsmodels`, `openai`.
- Eine formale automatisierte Test-Suite ist aktuell nicht konfiguriert; Smoke-Tests und manuelle UI-Validierung sind der aktuelle Arbeitsablauf.
- Empfohlene Smoke-Tests:
  - `python scripts/test_mixed_ai.py`
  - `python scripts/test_fmp.py`
  - `python scripts/test_fmp_endpoints.py`
- Manuelle Checks vor einem Release:
  - Pan/Zoom-Sync,
  - STL Overlay/Periodenlinien-Verhalten,
  - Handelssteuerung (inkl. Close-Sicherheitsverhalten),
  - News-Panel-Fallback-Verhalten.

## 🧯 Fehlerbehebung
| Symptom | Maßnahme |
|---|---|
| MT5 initialize failed | `MT5_PATH` exakt auf `terminal64.exe` setzen, anschließend das Terminal mindestens einmal manuell starten |
| MT5 login failed | Sicherstellen, dass `MT5_SERVER` exakt dem Server-String im Terminal entspricht, oder auf Credentials verzichten und eine aktive Sitzung wiederverwenden |
| No data for symbol | Broker-Symbolnamen und Sichtbarkeit im Market Watch prüfen (`XAUUSD`, `XAUUSD.a`, `GOLD` usw.) |
| Postgres connection issues | `DATABASE_URL` prüfen, dann `psql "$DATABASE_URL" -c 'select 1;'` ausführen |
| Slow or stale UI analytics | Auto STL bei schweren Paaren/Zeitrahmen deaktivieren und manuell neu berechnen |

## 🛣️ Roadmap
- Ausbau von `i18n/`-Laufzeitressourcen über README-basierte mehrsprachige Dokumentation hinaus.
- Einführung formeller automatisierter Tests (API + Integration + UI-Smoke).
- Verbesserung von Deployment-Paketen und reproduzierbaren Umgebungsprofilen.
- Weiterentwicklung der KI-Planvalidierung und Ausführungssicherheit.

## 🤝 Mitwirken
- Halten Sie Patches klein und fokussiert.
- Verwenden Sie klare Commit-Prefixe, wo sinnvoll (z. B. `UI: ...`, `Server: ...`, `References: ...`).
- Vermeiden Sie nicht zusammenhängende Formatierungsänderungen.
- Fügen Sie Screenshots/GIFs für UI-Änderungen bei Bedarf hinzu.
- Führen Sie Smoke-Tests und lokale Browser-Checks vor PRs durch.

## 📚 Referenzen
- `references/ai-trader-overview.md`
- `references/database_setup_postgres.md`
- `references/mt5_python_setup_ubuntu.md`
- `references/mt4_vs_mt5.md`
- `references/llm_trading_system.md`
- `references/release_deploy.md`
- `references/pnl_debugging.md`

## 📄 Lizenz
Keine `LICENSE`-Datei ist in diesem Repository zum Stand von 2026-02-28 vorhanden.

Annahme: Die Lizenzbedingungen sind in diesem Repository derzeit nicht festgelegt; behalten Sie diesen Hinweis bis eine explizite Lizenzdatei ergänzt wird.


## ❤️ Support

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://camo.githubusercontent.com/24a4914f0b42c6f435f9e101621f1e52535b02c225764b2f6cc99416926004b7/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f446f6e6174652d4c617a79696e674172742d3045413545393f7374796c653d666f722d7468652d6261646765266c6f676f3d6b6f2d6669266c6f676f436f6c6f723d7768697465)](https://chat.lazying.art/donate) | [![PayPal](https://camo.githubusercontent.com/d0f57e8b016517a4b06961b24d0ca87d62fdba16e18bbdb6aba28e978dc0ea21/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f50617950616c2d526f6e677a686f754368656e2d3030343537433f7374796c653d666f722d7468652d6261646765266c6f676f3d70617970616c266c6f676f436f6c6f723d7768697465)](https://paypal.me/RongzhouChen) | [![Stripe](https://camo.githubusercontent.com/1152dfe04b6943afe3a8d2953676749603fb9f95e24088c92c97a01a897b4942/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f5374726970652d446f6e6174652d3633354246463f7374796c653d666f722d7468652d6261646765266c6f676f3d737472697065266c6f676f436f6c6f723d7768697465)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |
