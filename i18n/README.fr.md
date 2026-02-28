[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# MetaTrader QT - Kit de démarrage au trading quantitatif (Philosophie Micro Quant)

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Backend](https://img.shields.io/badge/Backend-Tornado-2d7cbf)
![Database](https://img.shields.io/badge/Database-PostgreSQL-336791?logo=postgresql&logoColor=white)
![Broker](https://img.shields.io/badge/Broker%20Bridge-MetaTrader5-1f6feb)
![UI](https://img.shields.io/badge/UI-Lightweight%20Charts%20%2B%20Chart.js-0ea5e9)
![Status](https://img.shields.io/badge/README-Expanded-success)
![GitHub%20Stars](https://img.shields.io/github/stars/lachlanchen/MicroQuant?style=for-the-badge&logo=github&logoColor=white&labelColor=0f172a&color=0ea5e9)
![GitHub%20Issues](https://img.shields.io/github/issues/lachlanchen/MicroQuant?style=for-the-badge&logo=github&logoColor=white&labelColor=0f172a&color=ef4444)

## 🎯 Vue d’ensemble du projet

| Focus | Stack |
|---|---|
| Runtime | Tornado + asyncpg + WebSocket |
| Trading | MetaTrader5 + signaux IA/tech/news en couches |
| Stockage | PostgreSQL avec pipeline déterministe d’upsert |
| Déploiement | Actifs PWA + UI desktop/mobile en priorité navigateur |

## Table des matières
- [📸 Capture d’écran](#-capture-décran)
- [🧭 Aperçu](#-aperçu)
- [🧠 Philosophie centrale](#-philosophie-centrale)
- [✨ Fonctionnalités](#-fonctionnalités)
- [🗂️ Structure du projet](#️-structure-du-projet)
- [✅ Prérequis](#-prérequis)
- [🛠️ Installation](#-installation)
- [⚙️ Configuration](#️-configuration)
- [🚀 Utilisation](#-utilisation)
- [🔌 Endpoints d’API (Pratique)](#-endpoints-dapi-pratique)
- [🧪 Exemples](#-exemples)
- [🗄️ Base de données et schéma](#-base-de-données--schéma)
- [🛡️ Contrôles de trading et sécurité](#️-contrôles-de-trading-et-sécurité)
- [📈 Basculer le recalcul automatique STL](#-basculer-le-recalcul-automatique-stl)
- [🧷 Mémoriser la dernière sélection](#️-mémoriser-la-dernière-sélection)
- [🤖 Contexte du plan de trading IA](#️-contexte-du-plan-de-trading-ia)
- [🧰 Notes de développement](#-notes-de-développement)
- [🧯 Dépannage](#-dépannage)
- [🛣️ Feuille de route](#-feuille-de-route)
- [🤝 Contribuer](#-contribuer)
- [📚 Références](#-références)
- [❤️ Support](#️-support)
- [📄 Licence](#-licence)

## 📸 Capture d’écran
![Micro Quant UI](figures/demos/micro-quant-ui.png)

[![DATA Source](https://img.shields.io/badge/Data_Source-RoboForex-0060ff?style=for-the-badge&labelColor=0a4eb3)](https://my.roboforex.com/en/?a=efx)

## 🧭 Aperçu
Micro Quant n’est pas un projet de tableaux de bord brillants, mais une chaîne logique de trading reproductible : il extrait les données OHLC depuis MetaTrader 5, les persiste dans PostgreSQL, puis évalue des décisions systématiques via des signaux IA multicouches (nouvelles de base, instantanés techniques, plans de trading et overlays STL). L’UI reflète cette approche avec des bascules d’alignement, des fermetures argumentées, des préférences persistantes et un panneau d’exécution riche en données, pour que le serveur puisse exécuter des flux périodiques ou manuels tout en affichant des logs exploitables.

La page d’atterrissage statique (Quant by Lazying.art) se trouve dans `docs/` et est publiée via GitHub Pages (`trade.lazying.art` via `docs/CNAME`). Le dépôt contient aussi des références pour les prompts de plan de trading IA, les notes d’intégration et la documentation opérationnelle.

### En bref
| Domaine | Rôle |
|---|---|
| Données | Extrait les OHLC de MT5 et fait l’upsert dans PostgreSQL |
| Analytique | Exécute les workflows health/news/tech et STL |
| Décision | Construit des plans de trading IA à partir d’un contexte en couches |
| Exécution | Exécute/contrôle les flux de trading avec des garde-fous |
| Interface | Vues desktop/mobile avec workflows de graphiques synchronisés |

## 🧠 Philosophie centrale
- **Chaîne de vérité** : les vérifications de base des nouvelles (texte + scores) et les instantanés techniques (contexte technique riche + STL) alimentent un plan de trading unique par paire/timeframe. Les exécutions périodiques automatiques et celles déclenchées via modal partagent le même pipeline et les mêmes logs de raisonnement.
- **Exécution orientée alignement** : les commutateurs Accept-Tech/Hold-Neutral, le mode ignore-basics et les enveloppes de clôture partielle garantissent que la logique technique est suivie volontairement, que les positions opposées sont fermées avant toute nouvelle entrée si nécessaire, et que les sorties superflues sont réduites.
- **Données immuables** : chaque ingestion écrit dans Postgres avec une politique `ON CONFLICT`, tandis que `/api/data` lit des séries assainies pour l’UI. Les préférences (`auto` settings, `close_fraction`, bascules hide-tech, recalcul auto STL) sont persistées via `/api/preferences`.
- **Trading orienté sécurité** : `TRADING_ENABLED` et `safe_max` gèrent les autorisations en mode manuel et automatique. `/api/close` et les runners périodiques journalisent les raisons de clôture (neutre technique, désalignement, etc.) pour la traçabilité.

## ✨ Fonctionnalités
- Ingestion OHLC MT5 vers Postgres (`/api/fetch`, `/api/fetch_bulk`).
- UI chart sur `/` (desktop) et `/app` (mobile), avec Chart.js + Lightweight Charts dans les templates.
- Workflows de décomposition STL (`/api/stl`, `/api/stl/compute`, endpoints prune/delete).
- Ingestion et analyse des news (`/api/news`, `/api/news/backfill_forex`, `/api/news/analyze`).
- Orchestration du flux IA (`/api/health/run`, `/api/health/runs`, `/api/ai/trade_plan`).
- Exécution manuelle de trades (`/api/trade`, `/api/trade/execute_plan`) protégée par `TRADING_ENABLED`.
- Opérations de gestion du risque des positions (`/api/positions*`, `/api/close`, `/api/close_tickets`) avec des fermetures autorisées par comportement de sécurité explicite.
- Flux de mises à jour WebSocket sur `/ws/updates` pour signaux et rafraîchissements en temps réel.
- Actifs PWA/statics pour un dashboard installable.

## 🗂️ Structure du projet
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

## ✅ Prérequis
- Ubuntu/Linux ou Windows avec accès terminal.
- MetaTrader 5 installé (`terminal64.exe`) et connecté lorsque nécessaire.
- Python 3.10+ (Python 3.11 recommandé pour une compatibilité plus large avec les wheels MetaTrader5).
- Instance PostgreSQL accessible depuis le serveur d’app.
- Clés API optionnelles pour les fournisseurs de news :
  - FMP
  - Alpha Vantage

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

# Alternative: local 3.11 venv (if global Python is newer)
# Requires python3.11 on your system
# sudo apt install python3.11 python3.11-venv
bash scripts/bootstrap_venv311.sh
source .venv311/bin/activate

# DB (use your own user/password as needed)
# createdb -h localhost -p 5432 -U lachlan metatrader_db

# Configure env
cp .env.example .env
# edit .env with your MT5 path and credentials
test -f .env && set -a; source .env; set +a

# Run app
python -m app.server
# Open http://localhost:8888
```

## ⚙️ Configuration
Copiez `.env.example` en `.env` et ajustez les valeurs.

### Variables principales
| Variable | Objectif |
|---|---|
| `DATABASE_URL` | DSN PostgreSQL préféré |
| `DATABASE_MT_URL` | DSN de secours si `DATABASE_URL` n’est pas renseigné |
| `DATABASE_QT_URL` | DSN secondaire de secours |
| `MT5_PATH` | Chemin vers `terminal64.exe` (Wine ou natif) |
| `MT5_LOGIN` / `MT5_PASSWORD` / `MT5_SERVER` | Optionnels si la session MT5 est déjà connectée |
| `PORT` | Port du serveur (par défaut `8888`) |

### Variables optionnelles
- `FMP_API_KEY`, `ALPHAVANTAGE_API_KEY` pour l’enrichissement des news.
- `TRADING_ENABLED` (`0` par défaut, passer à `1` pour autoriser les endpoints de passage d’ordres).
- `TRADING_VOLUME` (volume manuel par défaut).
- `AUTO_FETCH`, `AUTO_FETCH_SYMBOL`, `AUTO_FETCH_TF`, `AUTO_FETCH_COUNT`, `AUTO_FETCH_SEC`.
- `PIN_DEFAULTS_TO_XAU_H1=1` pour forcer les valeurs par défaut de symbole/timeframe au démarrage de l’UI.
- `LOG_LEVEL`, `LOG_BACKFILL`, ainsi que les préférences de compte/poll via `/api/preferences` et l’environnement.

Notes:
- `MT5_PATH` doit pointer vers votre `terminal64.exe` dans le préfixe Wine utilisé par votre installation MT5.
- Vous pouvez omettre les identifiants MT5 quand la session terminal est déjà active; l’application tentera de réutiliser cette session.

## 🚀 Utilisation

### Démarrer le serveur
```bash
python -m app.server
```

### Ouvrir l’UI
- UI desktop : `http://localhost:8888/`
- UI mobile : `http://localhost:8888/app`

### URLs clés
| Surface | URL | Objectif |
|---|---|---|
| Desktop | `http://localhost:8888/` | Graphique chandeliers et contrôles desktop |
| Mobile | `http://localhost:8888/app` | Interface tactile avec commandes compactes |
| Santé API | `http://localhost:8888/api/health/freshness` | Vérification rapide des données + état du service |

### Flux courant
1. Récupérer des barres depuis MT5 puis les persister dans Postgres.
2. Lire les barres depuis la base pour le charting.
3. Lancer les analyses health/tech/news.
4. Générer un plan de trading IA.
5. Exécuter ou fermer des positions via les garde-fous de sécurité.

## 🔌 Endpoints d’API (Pratique)
- `GET /api/fetch?symbol=XAUUSD&tf=H1&count=500[&mode=inc|full][&persist=1]`
  - Récupère depuis MT5 et fait un upsert dans la DB.
  - Si `persist=1`, le serveur enregistre `last_symbol/last_tf/last_count`; les fetchs bulk/background doivent l’omettre pour éviter d’écraser les choix de l’UI.
- `GET /api/fetch_bulk` — ingestion en lot/schedulée.
- `GET /api/data?symbol=XAUUSD&tf=H1&limit=500` — lit les données de chart depuis la DB.
- `GET /api/strategy/run?symbol=XAUUSD&tf=H1&fast=20&slow=50`
  - Exécute le croisement SMA(20/50) et renvoie la charge utile du signal.
  - Note importante : le passage d’ordres piloté par la stratégie depuis cet endpoint est actuellement désactivé côté serveur; l’exécution se fait via les endpoints de trading.
- `POST /api/trade` — Buy/Sell manuel depuis l’UI, protégé par `TRADING_ENABLED`.
- `POST /api/trade/execute_plan` — exécute un plan généré, incluant pré-clôture et vérifications de distance de stop.
- `POST /api/close` — aplatit les positions (autorisé même quand `TRADING_ENABLED=0` pour la sécurité) :
  - Symbole courant: corps de requête `symbol=...`; `side=long|short|both` optionnel.
  - Tous les symboles: `?scope=all` et `&side=...` optionnel.
  - La réponse inclut `closed_count` et les résultats par ticket.
- `POST /api/close_tickets` — ferme un sous-ensemble demandé par ticket.
- `GET /api/positions`, `GET /api/positions/all`.
- `GET /api/stl`, `POST /api/stl/compute`, `POST /api/stl/prune`, `POST /api/stl/prune_all`, `DELETE /api/stl/run/{id}`.
- `GET /api/news`, `POST /api/news/backfill_forex`, `POST /api/news/analyze`.
- `GET /api/health/freshness`, `GET /api/tech/freshness`, `GET|POST /api/health/run`, `GET /api/health/runs`.
- `POST /api/preferences` et récupération associée des préférences.
- `GET /api/ai/trade_plan`.
- `GET /api/accounts`, `GET /api/account/current`, `POST /api/account/login`.
- `GET /ws/updates`.

## 🧪 Exemples
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

## 🗄️ Base de données et schéma
Voir `sql/schema.sql`.

Points clés :
- La PK composite `(symbol, timeframe, ts)` dans `ohlc_bars` empêche les barres dupliquées.
- L’ingestion utilise `ON CONFLICT ... DO UPDATE`.
- Des tables supplémentaires soutiennent les exécutions STL/composants, les préférences, les articles de news, les health runs, séries de compte, deals fermés et le lien signal/order-plan.

## 🛡️ Contrôles de trading et sécurité
- Garde-fou d’environnement : `TRADING_ENABLED=0` désactive par défaut le placement d’ordres depuis les endpoints de trade manuel/plan.
- Le comportement `Auto` de l’entête UI planifie des vérifications de stratégie ; il ne contourne pas les garde-fous de trading.
- Les opérations de clôture sont volontairement autorisées même si le trading est désactivé.
- `safe_max` et la pondération par symbole/type sont utilisés dans les flux d’exécution pour limiter l’exposition.

## 📈 Basculer le recalcul automatique STL
- Le recalcul automatique STL est contrôlé par symbole x timeframe via l’interrupteur `Auto STL` du panneau STL.
- La valeur par défaut est OFF pour réduire le lag UI sur les contextes volumineux/lents.
- Quand ON, les STL manquantes/obsolètes peuvent se recalculer automatiquement; sinon utilisez les contrôles de recalcul manuel.
- L’état persiste via `/api/preferences` avec des clés `stl_auto_compute:SYMBOL:TF` et aussi via localStorage pour un démarrage plus rapide.

## 🧷 Mémoriser la dernière sélection
- Le serveur persiste `last_symbol`, `last_tf`, `last_count` et injecte les valeurs par défaut dans les templates.
- L’UI stocke également `last_symbol`/`last_tf` dans `localStorage`.
- `/?reset=1` ignore les préférences stockées pour ce chargement de page.
- `PIN_DEFAULTS_TO_XAU_H1=1` peut forcer les valeurs de démarrage.

## 🤖 Contexte du plan de trading IA
Lors d’une demande de plan de trading IA, le serveur vérifie qu’il existe des exécutions récentes de Basic Health et Tech Snapshot pour le symbole/timeframe courant (en les créant si nécessaire), puis construit le contexte du prompt avec :
- Bloc health de base,
- Bloc technique IA,
- Bloc instantané technique en direct.

## 🧰 Notes de développement
- Dépendances d’exécution principales : `tornado`, `asyncpg`, `MetaTrader5`, `numpy`, `python-dotenv`, `requests`, `httpx`, `statsmodels`, `openai`.
- Aucune suite de tests automatisée formelle n’est actuellement configurée; les smoke tests et la validation manuelle UI restent le flux actif.
- Smoke tests recommandés :
  - `python scripts/test_mixed_ai.py`
  - `python scripts/test_fmp.py`
  - `python scripts/test_fmp_endpoints.py`
- Contrôles manuels avant release :
  - synchronisation pan/zoom,
  - comportement STL overlay/period-lines,
  - contrôles de trading (y compris comportement de sécurité de fermeture),
  - fallback du panneau news.

## 🧯 Dépannage
| Symptôme | Action |
|---|---|
| Échec d’initialisation MT5 | Configurer `MT5_PATH` vers le `terminal64.exe` exact, puis lancer manuellement le terminal au moins une fois |
| Échec de connexion MT5 | Vérifier que `MT5_SERVER` correspond exactement à la chaîne serveur du terminal, ou omettre les credentials et réutiliser une session active |
| Aucune donnée pour le symbole | Vérifier le naming du symbole broker et la visibilité Market Watch (`XAUUSD`, `XAUUSD.a`, `GOLD`, etc.) |
| Problème de connexion PostgreSQL | Vérifier `DATABASE_URL`, puis exécuter `psql "$DATABASE_URL" -c 'select 1;'` |
| Analyse UI lente ou périmée | Désactiver auto STL sur les paires/TF lourds et recalculer manuellement |

## 🛣️ Feuille de route
- Étendre les ressources runtime de `i18n/` au-delà des docs multilingues basées sur le README.
- Ajouter des tests automatisés formels (API + intégration + automatisation smoke UI).
- Améliorer le packaging de déploiement et les profils d’environnement reproductibles.
- Poursuivre le raffinement de la validation des plans IA et des garde-fous d’exécution.

## 🤝 Contribuer
- Gardez les modifications petites et ciblées.
- Utilisez des préfixes de commit explicites quand pertinent (par exemple : `UI: ...`, `Server: ...`, `References: ...`).
- Évitez les changements de format sans rapport avec la logique.
- Incluez captures d’écran/GIFs pour les changements d’UI quand pertinent.
- Exécutez smoke tests et vérifications navigateur locales avant les PR.

## 📚 Références
- `references/ai-trader-overview.md`
- `references/database_setup_postgres.md`
- `references/mt5_python_setup_ubuntu.md`
- `references/mt4_vs_mt5.md`
- `references/llm_trading_system.md`
- `references/release_deploy.md`
- `references/pnl_debugging.md`

## 📄 Licence
Aucun fichier `LICENSE` n’est présent dans ce dépôt à la date du 2026-02-28.

Hypothèse : les conditions de licence sont actuellement non précisées dans le dépôt; conservez cette note tant que les mainteneurs n’ajoutent pas un fichier de licence explicite.


## ❤️ Support

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://camo.githubusercontent.com/24a4914f0b42c6f435f9e101621f1e52535b02c225764b2f6cc99416926004b7/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f446f6e6174652d4c617a79696e674172742d3045413545393f7374796c653d666f722d7468652d6261646765266c6f676f3d6b6f2d6669266c6f676f436f6c6f723d7768697465)](https://chat.lazying.art/donate) | [![PayPal](https://camo.githubusercontent.com/d0f57e8b016517a4b06961b24d0ca87d62fdba16e18bbdb6aba28e978dc0ea21/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f50617950616c2d526f6e677a686f754368656e2d3030343537433f7374796c653d666f722d7468652d6261646765266c6f676f3d70617970616c266c6f676f436f6c6f723d7768697465)](https://paypal.me/RongzhouChen) | [![Stripe](https://camo.githubusercontent.com/1152dfe04b6943afe3a8d2953676749603fb9f95e24088c92c97a01a897b4942/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f5374726970652d446f6e6174652d3633354246463f7374796c653d666f722d7468652d6261646765266c6f676f3d737472697065266c6f676f436f6c6f723d7768697465)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |
