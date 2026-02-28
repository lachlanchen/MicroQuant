[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# MetaTrader QT - 量化交易入門（Micro Quant 哲學）

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Backend](https://img.shields.io/badge/Backend-Tornado-2d7cbf)
![Database](https://img.shields.io/badge/Database-PostgreSQL-336791?logo=postgresql&logoColor=white)
![Broker](https://img.shields.io/badge/Broker%20Bridge-MetaTrader5-1f6feb)
![UI](https://img.shields.io/badge/UI-Lightweight%20Charts%20%2B%20Chart.js-0ea5e9)
![Status](https://img.shields.io/badge/README-Expanded-success)
![GitHub%20Stars](https://img.shields.io/github/stars/lachlanchen/MicroQuant?style=for-the-badge&logo=github&logoColor=white&labelColor=0f172a&color=0ea5e9)
![GitHub%20Issues](https://img.shields.io/github/issues/lachlanchen/MicroQuant?style=for-the-badge&logo=github&logoColor=white&labelColor=0f172a&color=ef4444)

## 🎯 專案快照

| 焦點 | 技術棧 |
|---|---|
| 執行環境 | Tornado + asyncpg + WebSocket |
| 交易 | MetaTrader5 + 分層 AI / 技術 / 新聞上下文 |
| 儲存 | PostgreSQL + 決定性 upsert 管線 |
| 部署 | PWA 資源 + 桌機/行動瀏覽器為先的 UI |

## 目錄
- [📸 畫面截圖](#-screenshot)
- [概覽](#-overview)
- [核心理念](#-core-philosophy)
- [功能](#-features)
- [專案結構](#-project-structure)
- [先決條件](#-prerequisites)
- [安裝](#-installation)
- [組態設定](#️-configuration)
- [使用方式](#-usage)
- [API 端點（實用）](#-api-endpoints-practical)
- [範例](#-examples)
- [資料庫與 Schema](#-database--schema)
- [交易控管與安全性](#️-trading-controls--safety)
- [STL 自動計算開關](#-stl-auto-compute-toggle)
- [記住上次選擇](#-remembering-last-selection)
- [AI 交易計畫上下文](#️-ai-trade-plan-prompt-context)
- [開發備註](#-development-notes)
- [故障排除](#-troubleshooting)
- [路線圖](#-roadmap)
- [貢獻](#-contributing)
- [參考資料](#-references)
- [支援](#️-support)
- [授權](#-license)

## 📸 畫面截圖
![Micro Quant UI](figures/demos/micro-quant-ui.png)

[![DATA Source](https://img.shields.io/badge/Data_Source-RoboForex-0060ff?style=for-the-badge&labelColor=0a4eb3)](https://my.roboforex.com/en/?a=efx)

## 🧭 概覽
Micro Quant 不只是在堆疊亮眼的儀表板，而是要打造可重複的交易邏輯堆疊：從 MetaTrader 5 抓取 OHLC 資料，寫入 PostgreSQL，並透過分層 AI 輔助訊號（基礎新聞、技術快照、交易計畫與 STL 疊加）來做系統化決策判斷。UI 也循此理念設計，提供對齊切換、可追溯的平倉、偏好持久化，以及資料豐富的執行面板，讓伺服器可在你檢視日誌與證據時安全執行定期或手動模組式交易流程。

靜態著陸頁（Quant by Lazying.art）位於 `docs/`，由 GitHub Pages 發佈（透過 `docs/CNAME`，網域 `trade.lazying.art`）。本庫同時也包含 AI Trade Plan 提示詞、整合說明與營運文件。

### 一覽
| 領域 | 功能 |
|---|---|
| 資料 | 從 MT5 取得 OHLC 並 upsert 到 PostgreSQL |
| 分析 | 執行 health/news/tech 與 STL 工作流程 |
| 決策 | 根據分層上下文建立 AI 交易計畫 |
| 執行 | 在風險防護下執行／控管交易流程 |
| UI | 桌機與行動端介面，並提供圖表流程同步 |

## 🧠 核心理念
- **真相鏈（Chain of truth）**：基礎新聞檢查（文字＋分數）與技術快照（深入技術背景＋STL）共同輸出每個商品/時間週期的單一 AI 交易計畫。定期自動執行與手動模態執行共用同一套管線與推理紀錄。
- **先對齊再執行**：Accept-Tech/Hold-Neutral 切換、ignore-basics 開關，以及局部平倉包裝器可確保技術面方向被有意識地遵循；必要時先平掉反向部位再開新倉，並盡量避免不必要的出場。
- **不可變資料（Immutable data）**：每次抓取都透過 `ON CONFLICT` 規則寫入 Postgres；`/api/data` 為 UI 回傳清理後的序列。使用者偏好（`auto` 設定、`close_fraction`、hide-tech 開關、STL 自動計算）皆透過 `/api/preferences` 持久化。
- **安全優先交易**：`TRADING_ENABLED` 與 `safe_max` 負責手動／自動權限控管。`/api/close` 與定期任務會記錄平倉原因（如 tech neutral、misalignment）以方便追蹤。

## ✨ 功能
- MT5 OHLC 載入 PostgreSQL（`/api/fetch`、`/api/fetch_bulk`）。
- 根路徑 `/`（桌機）與 `/app`（行動）提供圖表介面，`templates` 內使用 Chart.js 與 Lightweight Charts。
- STL 分解流程（`/api/stl`、`/api/stl/compute`、prune/delete 相關端點）。
- 新聞擷取與分析（`/api/news`、`/api/news/backfill_forex`、`/api/news/analyze`）。
- AI 流程編排（`/api/health/run`、`/api/health/runs`、`/api/ai/trade_plan`）。
- 手動交易執行（`/api/trade`、`/api/trade/execute_plan`），受 `TRADING_ENABLED` 保護。
- 倉位風險操作（`/api/positions*`、`/api/close`、`/api/close_tickets`）在明確安全規則下可執行平倉。
- `/ws/updates` 提供即時提示與刷新訊號的 WebSocket 更新串流。
- 提供可安裝的 PWA 與靜態資源儀表板。

## 🗂️ 專案結構
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

## ✅ 先決條件
- Ubuntu/Linux 或可使用終端機的 Windows 環境。
- 已安裝 MetaTrader 5（`terminal64.exe`）並在需要時登入。
- Python 3.10+（建議 Python 3.11，以提高與 MetaTrader5 wheels 的相容性）。
- 伺服器可連線的 PostgreSQL 實例。
- 可選新聞來源 API Key：
  - FMP
  - Alpha Vantage

## 🛠️ 安裝

### Windows（PowerShell）
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

輔助腳本：
```powershell
scripts\setup_windows.ps1
scripts\run_windows.ps1
```

### Linux/macOS（bash）
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

## ⚙️ 組態設定
將 `.env.example` 複製為 `.env` 後依需求調整。

### 核心變數
| 變數 | 用途 |
|---|---|
| `DATABASE_URL` | 首選 PostgreSQL DSN |
| `DATABASE_MT_URL` | `DATABASE_URL` 未設定時的備援 DSN |
| `DATABASE_QT_URL` | 次要備援 DSN |
| `MT5_PATH` | 指向 `terminal64.exe` 的路徑（Wine 或原生） |
| `MT5_LOGIN` / `MT5_PASSWORD` / `MT5_SERVER` | 若 MT5 工作階段已登入可留空 |
| `PORT` | 伺服器埠號（預設 `8888`） |

### 可選變數
- `FMP_API_KEY`、`ALPHAVANTAGE_API_KEY` 用於新聞增強。
- `TRADING_ENABLED`（預設 `0`，設為 `1` 才會開啟下單端點）。
- `TRADING_VOLUME`（預設為手動交易數量）。
- `AUTO_FETCH`、`AUTO_FETCH_SYMBOL`、`AUTO_FETCH_TF`、`AUTO_FETCH_COUNT`、`AUTO_FETCH_SEC`。
- `PIN_DEFAULTS_TO_XAU_H1=1` 可強制 UI 啟動時預設商品/時間週期。
- `LOG_LEVEL`、`LOG_BACKFILL`，以及透過 `/api/preferences` 與環境變數設定的帳戶／輪詢偏好。

備註：
- `MT5_PATH` 應指向你在 MT5 安裝腳本所用 Wine 前綴下的 `terminal64.exe`。
- 當終端機會話已登入時可省略 MT5 認證資料，系統會嘗試重用該會話。

## 🚀 使用方式

### 啟動服務
```bash
python -m app.server
```

### 開啟 UI
- 桌機 UI：`http://localhost:8888/`
- 行動 UI：`http://localhost:8888/app`

### 主要網址
| 畫面 | URL | 用途 |
|---|---|---|
| 桌機 | `http://localhost:8888/` | K 線圖與桌機化交易流程 |
| 行動 | `http://localhost:8888/app` | 以觸控為先的布局，控制項較精簡 |
| API 健康檢查 | `http://localhost:8888/api/health/freshness` | 快速檢查資料與服務就緒狀態 |

### 一般流程
1. 從 MT5 抓取 K 線並持久化到 Postgres。
2. 從資料庫讀取 K 線用於圖表。
3. 執行 health/tech/news 分析。
4. 產生 AI 交易計畫。
5. 在安全控管下執行交易或平倉。

## 🔌 API 介面（實用）
- `GET /api/fetch?symbol=XAUUSD&tf=H1&count=500[&mode=inc|full][&persist=1]`
  - 從 MT5 抓取並 upsert 到資料庫。
  - 若 `persist=1`，伺服器會儲存 `last_symbol/last_tf/last_count` 作為預設值；批次或背景抓取請不要加此參數，以免覆寫 UI 選擇。
- `GET /api/fetch_bulk` — 批次／排程抓取。
- `GET /api/data?symbol=XAUUSD&tf=H1&limit=500` — 從資料庫讀取圖表資料。
- `GET /api/strategy/run?symbol=XAUUSD&tf=H1&fast=20&slow=50`
  - 執行 SMA(20/50) 交叉並回傳 signal payload。
  - 重要實作註解：策略驅動下單目前在伺服器端已停用；交易執行以交易端點為主。
- `POST /api/trade` — 從 UI 進行手動 Buy/Sell，受 `TRADING_ENABLED` 限制。
- `POST /api/trade/execute_plan` — 執行已產生的計畫，包含預先平倉與停損距離檢查。
- `POST /api/close` — 平倉（出於安全考量，`TRADING_ENABLED=0` 時也允許）：
  - 當前商品：form body `symbol=...`；可選 `side=long|short|both`。
  - 全部商品：`?scope=all`，可選 `&side=...`。
  - 回應會包含 `closed_count` 與逐 ticket 結果。
- `POST /api/close_tickets` — 依 ticket 批次關閉指定倉位。
- `GET /api/positions`, `GET /api/positions/all`。
- `GET /api/stl`, `POST /api/stl/compute`, `POST /api/stl/prune`, `POST /api/stl/prune_all`, `DELETE /api/stl/run/{id}`。
- `GET /api/news`, `POST /api/news/backfill_forex`, `POST /api/news/analyze`。
- `GET /api/health/freshness`, `GET /api/tech/freshness`, `GET|POST /api/health/run`, `GET /api/health/runs`。
- `POST /api/preferences` 及相關偏好讀取。
- `GET /api/ai/trade_plan`。
- `GET /api/accounts`, `GET /api/account/current`, `POST /api/account/login`。
- `GET /ws/updates`。

## 🧪 範例
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

## 🗄️ 資料庫與 Schema
參見 `sql/schema.sql`。

重點：
- `ohlc_bars` 的複合主鍵 `(symbol, timeframe, ts)` 用來避免重複 K 線。
- 資料寫入使用 `ON CONFLICT ... DO UPDATE`。
- 其他資料表支援 STL 執行/元件、偏好設定、新聞文章、健康檢查執行、帳戶序列、平倉交易與訊號/委託計畫關聯。

## 🛡️ 交易控管與安全性
- 環境變數保護：預設 `TRADING_ENABLED=0`，會停用手動／計畫執行端點的下單。
- UI 的 `Auto` 行為僅安排策略檢查，不會繞過交易安全門檻。
- 平倉操作在停用交易時也會被允許，設計上刻意如此。
- safe-max 與商品／方向權重會在執行流程中限制部位暴露。

## 📈 STL 自動計算開關
- STL 自動計算可透過 STL 面板中的 `Auto STL` 開關按「商品 × 時間週期」設定。
- 預設為 OFF，以降低大型/慢速情境下的 UI 卡頓。
- 開啟時可對缺失或過期 STL 自動計算；否則請使用手動重算控制項。
- 狀態會透過 `/api/preferences` 的 `stl_auto_compute:SYMBOL:TF` 等鍵儲存，也會寫入 localStorage 以加快啟動速度。

## 🧷 記住上次選擇
- 伺服器會持久化 `last_symbol`、`last_tf`、`last_count`，並注入預設值到模板。
- UI 也會把 `last_symbol`、`last_tf` 存在 `localStorage`。
- 加上 `/?reset=1` 可以在該次頁面載入時忽略已儲存偏好。
- `PIN_DEFAULTS_TO_XAU_H1=1` 可強制起始預設。

## 🤖 AI 交易計畫提示上下文
當請求 AI 交易計畫時，伺服器會先確保目前商品與時間週期有新鮮的 Basic Health 與 Tech Snapshot 執行結果（若缺漏則自動建立），再從下列區塊建構提示內容：
- Basic health 區塊
- Tech AI 區塊
- 即時技術快照區塊

## 🧰 開發備註
- 主要執行時相依套件：`tornado`、`asyncpg`、`MetaTrader5`、`numpy`、`python-dotenv`、`requests`、`httpx`、`statsmodels`、`openai`。
- 目前尚未建置正式自動化測試；主要以 smoke test 與人工 UI 驗證為主。
- 建議執行的 smoke test：
  - `python scripts/test_mixed_ai.py`
  - `python scripts/test_fmp.py`
  - `python scripts/test_fmp_endpoints.py`
- 發佈前人工檢查：
  - pan/zoom 同步
  - STL 疊加（period line）行為
  - 交易控管（含平倉安全行為）
  - 新聞面板 fallback 行為

## 🧯 故障排除
| 症狀 | 處理方式 |
|---|---|
| MT5 初始化失敗 | 將 `MT5_PATH` 設為精準的 `terminal64.exe` 路徑，並先手動啟動一次終端機 |
| MT5 登入失敗 | 確認 `MT5_SERVER` 與終端機上伺服字串完全一致，或省略憑證直接重用已登入會話 |
| 商品無資料 | 確認券商商品命名與是否在 Market Watch 可見（如 `XAUUSD`、`XAUUSD.a`、`GOLD`） |
| Postgres 連線問題 | 確認 `DATABASE_URL`，再執行 `psql "$DATABASE_URL" -c 'select 1;'` |
| UI 分析更新緩慢或延遲 | 對重度幣對／時間框關閉 auto STL，改為手動重算 |

## 🛣️ 路線圖
- 將 `i18n/` 擴展到除 README 外的執行期多語資源。
- 建立正式自動測試（API + 整合 + UI smoke automation）。
- 改善部署打包流程與可重現環境設定檔。
- 持續優化 AI 計畫驗證與交易安全控制。

## 🤝 貢獻
- 保持補丁小而集中。
- 在適合情況下使用清楚的提交前綴（例如：`UI: ...`、`Server: ...`、`References: ...`）。
- 避免無關的格式重構。
- 有需要時請附上 UI 變更截圖／GIF。
- 提交 PR 前請執行 smoke test 並在瀏覽器本機驗證。

## 📚 參考資料
- `references/ai-trader-overview.md`
- `references/database_setup_postgres.md`
- `references/mt5_python_setup_ubuntu.md`
- `references/mt4_vs_mt5.md`
- `references/llm_trading_system.md`
- `references/release_deploy.md`
- `references/pnl_debugging.md`

## 📄 授權
目前儲存庫尚未包含 `LICENSE` 檔案，日期截至 2026-02-28。

現階段授權條款仍未在儲存庫中明確規範；請等維護者補上正式授權檔後再更新。


## ❤️ Support

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://camo.githubusercontent.com/24a4914f0b42c6f435f9e101621f1e52535b02c225764b2f6cc99416926004b7/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f446f6e6174652d4c617a79696e674172742d3045413545393f7374796c653d666f722d7468652d6261646765266c6f676f3d6b6f2d6669266c6f676f436f6c6f723d7768697465)](https://chat.lazying.art/donate) | [![PayPal](https://camo.githubusercontent.com/d0f57e8b016517a4b06961b24d0ca87d62fdba16e18bbdb6aba28e978dc0ea21/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f50617950616c2d526f6e677a686f754368656e2d3030343537433f7374796c653d666f722d7468652d6261646765266c6f676f3d70617970616c266c6f676f436f6c6f723d7768697465)](https://paypal.me/RongzhouChen) | [![Stripe](https://camo.githubusercontent.com/1152dfe04b6943afe3a8d2953676749603fb9f95e24088c92c97a01a897b4942/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f5374726970652d446f6e6174652d3633354246463f7374796c653d666f722d7468652d6261646765266c6f676f3d737472697065266c6f676f436f6c6f723d7768697465)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |
