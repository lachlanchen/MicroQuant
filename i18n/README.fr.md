[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


<p align="center">
  <img src="https://raw.githubusercontent.com/lachlanchen/lachlanchen/main/logos/banner.png" alt="LazyingArt banner" />
</p>

# MetaTrader QT - Démarrage du trading quantitatif (philosophie Micro Quant)

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Backend](https://img.shields.io/badge/Backend-Tornado-2d7cbf)
![Database](https://img.shields.io/badge/Database-PostgreSQL-336791?logo=postgresql&logoColor=white)
![Broker](https://img.shields.io/badge/Broker%20Bridge-MetaTrader5-1f6feb)
![UI](https://img.shields.io/badge/UI-Lightweight%20Charts%20%2B%20Chart.js-0ea5e9)
![Status](https://img.shields.io/badge/README-Expanded-success)

## 📸 Capture d’écran
![Micro Quant UI](figures/demos/micro-quant-ui.png)

<p align="center">
  <a href="https://my.roboforex.com/en/?a=efx" target="_blank" rel="noopener noreferrer">
    <button style="padding: 0.65rem 1.25rem; font-weight: 600; border-radius: 999px; border: none; color: white; background: #0060ff; cursor: pointer;">
      DATA Source
    </button>
  </a>
</p>

## 🧭 Vue d’ensemble
Micro Quant met moins l’accent sur les tableaux de bord « flashy » que sur une pile logique de trading reproductible : il récupère les données OHLC depuis MetaTrader 5, les persiste dans Postgres et évalue des décisions systématiques via des signaux guidés par l’IA en couches (Basic news, Tech snapshot, plans de trade et overlays STL). L’interface reflète cette philosophie avec des bascules d’alignement, des clôtures motivées, des préférences persistées et un panneau d’exécution riche en données afin que le serveur puisse exécuter en sécurité des flux de trading périodiques ou modaux pendant que vous inspectez les logs et les éléments de preuve.

La page statique d’accueil (Quant by Lazying.art) se trouve dans `docs/` et est publiée via GitHub Pages (`trade.lazying.art` via `docs/CNAME`). Le dépôt inclut aussi des références pour les prompts AI Trade Plan, des notes d’intégration et de la documentation opérationnelle.

### En un coup d’œil
| Zone | Rôle |
|---|---|
| Data | Récupère OHLC MT5 et upsert vers PostgreSQL |
| Analytics | Exécute les workflows health/news/tech et STL |
| Decisioning | Construit des plans de trade IA à partir d’un contexte en couches |
| Execution | Exécute/contrôle les flux de trading derrière des garde-fous de sécurité |
| UI | Vues desktop/mobile avec workflows de graphiques synchronisés |

## 🧠 Philosophie centrale
- **Chaîne de vérité** : les vérifications Basic news (texte + scores) et les Tech snapshots (contexte technique lourd + STL) alimentent un plan de trade IA unique par symbole/timeframe. Les auto-runs périodiques et les exécutions manuelles en modal partagent le même pipeline et les mêmes logs de raisonnement.
- **Exécution d’abord alignée** : les bascules Accept-Tech/Hold-Neutral, l’option ignore-basics et les wrappers de clôture partielle garantissent un suivi intentionnel du Tech, la fermeture des positions opposées avant de nouvelles entrées quand nécessaire, et la réduction des sorties inutiles.
- **Données immuables** : chaque récupération écrit dans Postgres avec une hygiène `ON CONFLICT`, tandis que `/api/data` lit des séries assainies pour l’UI. Les préférences (volumes auto, `close_fraction`, bascules hide-tech, STL auto-compute) persistent via `/api/preferences`.
- **Trading orienté sécurité** : `TRADING_ENABLED` et `safe_max` imposent les autorisations manuelles/auto. `/api/close` et les runners périodiques peuvent journaliser les raisons de clôture (tech neutral, désalignement, etc.) pour la traçabilité.

## ✨ Fonctionnalités
- Ingestion OHLC MT5 dans Postgres (`/api/fetch`, `/api/fetch_bulk`).
- UI graphique sur `/` (desktop) et `/app` (mobile), avec usage de Chart.js + Lightweight Charts dans les templates.
- Workflows de décomposition STL (`/api/stl`, `/api/stl/compute`, endpoints prune/delete).
- Ingestion et analyse des news (`/api/news`, `/api/news/backfill_forex`, `/api/news/analyze`).
- Orchestration du workflow IA (`/api/health/run`, `/api/health/runs`, `/api/ai/trade_plan`).
- Exécution manuelle des trades (`/api/trade`, `/api/trade/execute_plan`) protégée par `TRADING_ENABLED`.
- Opérations de risque sur positions (`/api/positions*`, `/api/close`, `/api/close_tickets`) avec clôtures autorisées pour la sécurité.
- Flux de mise à jour WebSocket sur `/ws/updates`.

## 🗂️ Structure du projet
```text
metatrader_qt/
├── app/
│   ├── server.py                # App Tornado, routes, orchestration
│   ├── db.py                    # Couche d’accès asyncpg + init du schéma
│   ├── mt5_client.py            # Bridge MetaTrader5 + opérations ordre/données
│   ├── news_fetcher.py          # Agrégation/filtrage FMP/AlphaVantage
│   └── strategy.py              # Helper crossover SMA
├── templates/
│   ├── index.html               # UI desktop principale
│   └── mobile.html              # UI orientée mobile
├── static/                      # Ressources PWA (icônes/manifest/service worker)
├── sql/
│   └── schema.sql               # Schéma DB principal
├── scripts/
│   ├── test_mixed_ai.py         # Smoke test Mixed AI
│   ├── test_fmp.py              # Smoke test FMP
│   ├── test_fmp_endpoints.py    # Script de sonde des endpoints FMP
│   ├── setup_windows.ps1        # Bootstrap d’environnement Windows
│   ├── run_windows.ps1          # Helper d’exécution Windows
│   └── bootstrap_venv311.sh     # Helper Python 3.11 Linux/mac
├── docs/                        # Site d’accueil GitHub Pages
├── references/                  # Notes opérationnelles/de setup
├── strategies/llm/              # Fichiers JSON prompt/config
├── llm_model/echomind/          # Wrappers de provider LLM
├── i18n/                        # Présent (actuellement vide)
├── .github/FUNDING.yml          # Métadonnées sponsor/support
└── README.md + README.*.md      # Doc canonique + multilingue
```

## ✅ Prérequis
- Ubuntu/Linux ou Windows.
- MT5 installé et accessible (`terminal64.exe`), terminal en cours d’exécution/connecté.
- Python 3.10+ (3.11 recommandé pour la compatibilité MetaTrader5).
- Instance PostgreSQL.

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

Scripts utilitaires :
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
Copiez `.env.example` vers `.env` puis ajustez les valeurs.

### Variables principales
| Variable | Utilité |
|---|---|
| `DATABASE_URL` | DSN PostgreSQL préféré |
| `DATABASE_MT_URL` | DSN de repli si `DATABASE_URL` non défini |
| `DATABASE_QT_URL` | DSN de repli secondaire |
| `MT5_PATH` | Chemin vers `terminal64.exe` (Wine ou natif) |
| `MT5_LOGIN` / `MT5_PASSWORD` / `MT5_SERVER` | Optionnel si la session terminal MT5 est déjà connectée |
| `PORT` | Port serveur (par défaut `8888`) |

### Variables optionnelles
- `FMP_API_KEY`, `ALPHAVANTAGE_API_KEY` pour enrichir les news.
- `TRADING_ENABLED` (`0` par défaut, mettez `1` pour autoriser les endpoints de passage d’ordres).
- `TRADING_VOLUME` (volume manuel par défaut).
- `AUTO_FETCH`, `AUTO_FETCH_SYMBOL`, `AUTO_FETCH_TF`, `AUTO_FETCH_COUNT`, `AUTO_FETCH_SEC`.
- `PIN_DEFAULTS_TO_XAU_H1=1` pour forcer le symbole/timeframe de démarrage de l’UI.
- `LOG_LEVEL`, `LOG_BACKFILL`, plus des préférences liées au compte/poll via `/api/preferences` et l’environnement.

Notes :
- `MT5_PATH` doit pointer vers votre `terminal64.exe` dans le préfixe Wine utilisé par votre script d’installation MT5.
- Vous pouvez omettre les identifiants MT5 si la session terminal est déjà connectée ; l’app essaiera de réutiliser cette session.

## 🚀 Utilisation

### Démarrer le serveur
```bash
python -m app.server
```

### Ouvrir l’UI
- UI desktop : `http://localhost:8888/`
- UI mobile : `http://localhost:8888/app`

### Workflow courant
1. Récupérer les barres depuis MT5 et persister dans Postgres.
2. Lire les barres depuis la DB pour l’affichage des graphiques.
3. Exécuter les analyses health/tech/news.
4. Générer un plan de trade IA.
5. Exécuter ou fermer des positions sous garde-fous de sécurité.

## 🔌 Endpoints API (pratiques)
- `GET /api/fetch?symbol=XAUUSD&tf=H1&count=500[&mode=inc|full][&persist=1]`
  - Récupère depuis MT5 et upsert en DB.
  - Si `persist=1`, le serveur enregistre les valeurs par défaut `last_symbol/last_tf/last_count` ; les récupérations bulk/en arrière-plan doivent l’omettre pour éviter d’écraser les choix UI.
- `GET /api/fetch_bulk` — ingestion bulk/planifiée.
- `GET /api/data?symbol=XAUUSD&tf=H1&limit=500` — lit les données de graphique depuis la DB.
- `GET /api/strategy/run?symbol=XAUUSD&tf=H1&fast=20&slow=50`
  - Exécute le crossover SMA(20/50) et renvoie la charge utile de signal.
  - Note d’implémentation importante : le passage d’ordres piloté par la stratégie depuis cet endpoint est actuellement désactivé dans le code serveur ; l’exécution des ordres est gérée via les endpoints de trade.
- `POST /api/trade` — Buy/Sell manuel depuis l’UI, protégé par `TRADING_ENABLED`.
- `POST /api/trade/execute_plan` — exécute un plan généré, inclut des vérifications pre-close et de distance de stop.
- `POST /api/close` — aplatit les positions (autorisé même quand `TRADING_ENABLED=0` pour la sécurité) :
  - Symbole courant : body form `symbol=...` ; `side=long|short|both` optionnel.
  - Tous les symboles : `?scope=all` et `&side=...` optionnel.
  - La réponse inclut `closed_count` et les résultats par ticket.
- `POST /api/close_tickets` — ferme un sous-ensemble demandé par ticket.
- `GET /api/positions`, `GET /api/positions/all`.
- `GET /api/stl`, `POST /api/stl/compute`, `POST /api/stl/prune`, `POST /api/stl/prune_all`, `DELETE /api/stl/run/{id}`.
- `GET /api/news`, `POST /api/news/backfill_forex`, `POST /api/news/analyze`.
- `GET /api/health/freshness`, `GET /api/tech/freshness`, `GET|POST /api/health/run`, `GET /api/health/runs`.
- `POST /api/preferences` et récupération de préférences associées.
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
- La PK composite `(symbol, timeframe, ts)` dans `ohlc_bars` évite les barres dupliquées.
- L’ingestion utilise `ON CONFLICT ... DO UPDATE`.
- Des tables additionnelles prennent en charge les runs/composants STL, les préférences, les articles de news, les health runs, les séries de compte, les deals clôturés et le lien signal/order-plan.

## 🛡️ Contrôles de trading et sécurité
- Garde environnemental : `TRADING_ENABLED=0` par défaut désactive le passage d’ordres depuis les endpoints d’exécution manuelle/de plan.
- Le comportement de l’en-tête `Auto` dans l’UI planifie des vérifications de stratégie ; il ne contourne pas les garde-fous de sécurité du trading.
- Les opérations de clôture sont volontairement autorisées même quand le trading est désactivé.
- Safe-max et la pondération symbole/type sont utilisés dans les flux d’exécution pour limiter l’exposition.

## 📈 Bascule STL Auto-Compute
- Le calcul automatique STL est contrôlé par symbole x timeframe via le switch `Auto STL` du panneau STL.
- La valeur par défaut est OFF pour réduire la latence UI dans les contextes lourds/lents.
- Quand ON, un STL manquant/périmé peut être calculé automatiquement ; sinon utilisez les contrôles de recalcul manuel.
- L’état persiste via des clés `/api/preferences` comme `stl_auto_compute:SYMBOL:TF` et aussi en stockage local pour un démarrage plus rapide.

## 🧷 Mémorisation de la dernière sélection
- Le serveur persiste `last_symbol`, `last_tf`, `last_count` et injecte les valeurs par défaut dans les templates.
- L’UI stocke aussi `last_symbol`/`last_tf` dans `localStorage`.
- `/?reset=1` ignore les préférences stockées pour ce chargement de page.
- `PIN_DEFAULTS_TO_XAU_H1=1` peut forcer les valeurs de démarrage.

## 🤖 Contexte de prompt AI Trade Plan
Lors d’une requête de plan de trade IA, le serveur vérifie que des runs Basic Health et Tech Snapshot récents existent pour le symbole/timeframe courant (en les créant si nécessaire), puis construit le contexte du prompt à partir de :
- Bloc Basic health,
- Bloc Tech AI,
- Bloc live technical snapshot.

## 🧰 Notes de développement
- Dépendances runtime principales : `tornado`, `asyncpg`, `MetaTrader5`, `numpy`, `python-dotenv`, `requests`, `httpx`, `statsmodels`, `openai`.
- Aucune suite de tests automatisés formelle n’est actuellement configurée ; les smoke tests et la validation manuelle de l’UI constituent le workflow actif.
- Smoke tests recommandés :
  - `python scripts/test_mixed_ai.py`
  - `python scripts/test_fmp.py`
  - `python scripts/test_fmp_endpoints.py`
- Vérifications manuelles à effectuer avant de push :
  - synchronisation pan/zoom,
  - comportement overlay STL/lignes de période,
  - contrôles de trading (y compris le comportement de sécurité des clôtures),
  - comportement de repli du panneau news.

## 🧯 Dépannage
| Symptôme | Action |
|---|---|
| MT5 initialize failed | Définissez `MT5_PATH` vers le `terminal64.exe` exact, puis lancez le terminal manuellement au moins une fois |
| MT5 login failed | Assurez-vous que `MT5_SERVER` correspond exactement à la chaîne serveur du terminal, ou omettez les identifiants et réutilisez une session active |
| No data for symbol | Vérifiez la nomenclature des symboles chez le broker et la visibilité dans Market Watch (`XAUUSD`, `XAUUSD.a`, `GOLD`, etc.) |
| Postgres connection issues | Vérifiez `DATABASE_URL`, puis exécutez `psql "$DATABASE_URL" -c 'select 1;'` |
| Slow or stale UI analytics | Désactivez Auto STL sur les paires/timeframes lourds puis recalculez manuellement |

## 🛣️ Feuille de route
- Étendre les assets runtime `i18n/` au-delà de la documentation README multilingue.
- Ajouter des tests automatisés formels (API + intégration + automatisation smoke UI).
- Améliorer le packaging de déploiement et les profils d’environnement reproductibles.
- Continuer à affiner la validation des plans IA et les garde-fous d’exécution.

## 🤝 Contribution
- Gardez les patchs petits et ciblés.
- Utilisez des préfixes de commit clairs lorsque pertinent (par exemple : `UI: ...`, `Server: ...`, `References: ...`).
- Évitez le churn de formatage sans rapport.
- Incluez des captures/GIF pour les changements UI quand pertinent.
- Exécutez les smoke tests et les vérifications navigateur locales avant une PR.

## ❤️ Support / Sponsor
Les liens de sponsor/support sont configurés dans `.github/FUNDING.yml` :
- GitHub Sponsors: https://github.com/sponsors/lachlanchen
- Lazying.art: https://lazying.art
- Chat: https://chat.lazying.art
- OnlyIdeas: https://onlyideas.art

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

Hypothèse : les conditions de licence ne sont actuellement pas spécifiées dans le dépôt ; conservez cette note jusqu’à ce que les mainteneurs ajoutent un fichier de licence explicite.
