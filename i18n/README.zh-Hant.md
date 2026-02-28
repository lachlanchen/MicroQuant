[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


<p align="center">
  <img src="https://raw.githubusercontent.com/lachlanchen/lachlanchen/main/logos/banner.png" alt="LazyingArt banner" />
</p>

# MetaTrader QT - 量化交易起手式（Micro Quant 哲學）

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Backend](https://img.shields.io/badge/Backend-Tornado-2d7cbf)
![Database](https://img.shields.io/badge/Database-PostgreSQL-336791?logo=postgresql&logoColor=white)
![Broker](https://img.shields.io/badge/Broker%20Bridge-MetaTrader5-1f6feb)
![UI](https://img.shields.io/badge/UI-Lightweight%20Charts%20%2B%20Chart.js-0ea5e9)
![Status](https://img.shields.io/badge/README-Expanded-success)

## 📸 截圖
![Micro Quant UI](figures/demos/micro-quant-ui.png)

<p align="center">
  <a href="https://my.roboforex.com/en/?a=efx" target="_blank" rel="noopener noreferrer">
    <button style="padding: 0.65rem 1.25rem; font-weight: 600; border-radius: 999px; border: none; color: white; background: #0060ff; cursor: pointer;">
      DATA Source
    </button>
  </a>
</p>

## 🧭 專案概覽
Micro Quant 重點不在華麗儀表板，而在可重複執行的交易邏輯堆疊：它從 MetaTrader 5 拉取 OHLC 資料、寫入 Postgres，並透過分層的 AI 導引訊號（Basic news、Tech snapshot、trade plans、STL overlays）評估系統化決策。UI 也體現這個哲學，提供對齊切換、具理由的平倉、偏好持久化與資訊密集的執行面板，讓伺服器可安全執行定期或 modal 交易流程，同時保留可供檢視的日誌與證據。

靜態落地頁（Quant by Lazying.art）位於 `docs/`，並透過 GitHub Pages 發佈（`trade.lazying.art`，由 `docs/CNAME` 設定）。本倉庫同時包含 AI Trade Plan 提示詞、整合筆記與操作文件。

### 快速總覽
| 區域 | 功能 |
|---|---|
| Data | 從 MT5 拉取 OHLC 並 upsert 到 PostgreSQL |
| Analytics | 執行 health/news/tech 與 STL 流程 |
| Decisioning | 基於分層上下文建立 AI trade plans |
| Execution | 在安全防護下執行/控制交易流程 |
| UI | 提供桌機/行動介面與同步圖表流程 |

## 🧠 核心哲學
- **真實鏈（Chain of truth）**：Basic news 檢查（文字 + 分數）與 Tech snapshots（重技術上下文 + STL）會匯入同一份 symbol/timeframe 專屬的 AI trade plan。週期性自動執行與手動 modal 執行共用同一條管線與推理日誌。
- **先對齊再執行（Alignment-first execution）**：Accept-Tech/Hold-Neutral 切換、ignore-basics 開關與 partial-close 封裝，確保有意識地遵循 Tech、必要時先關閉反向倉位再開新單，並降低不必要平倉。
- **不可變資料（Immutable data）**：每次抓取都以 `ON CONFLICT` 衛生規則寫入 Postgres，而 `/api/data` 讀取供 UI 使用的淨化序列。偏好設定（auto volumes、`close_fraction`、hide-tech 切換、STL auto-compute）透過 `/api/preferences` 持久化。
- **交易安全優先（Safety-first trading）**：`TRADING_ENABLED` 與 `safe_max` 負責手動/自動權限管控。`/api/close` 與週期性 runner 可記錄平倉原因（tech neutral、misalignment 等）以供追溯。

## ✨ 功能
- MT5 OHLC 匯入 Postgres（`/api/fetch`, `/api/fetch_bulk`）。
- 圖表 UI：`/`（桌機）與 `/app`（行動），模板中使用 Chart.js + Lightweight Charts。
- STL 分解流程（`/api/stl`, `/api/stl/compute`, prune/delete 端點）。
- 新聞抓取與分析（`/api/news`, `/api/news/backfill_forex`, `/api/news/analyze`）。
- AI 工作流協調（`/api/health/run`, `/api/health/runs`, `/api/ai/trade_plan`）。
- 手動交易執行（`/api/trade`, `/api/trade/execute_plan`），受 `TRADING_ENABLED` 保護。
- 倉位風險操作（`/api/positions*`, `/api/close`, `/api/close_tickets`），且為安全起見可進行平倉操作。
- WebSocket 更新串流於 `/ws/updates`。

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
├── i18n/                        # Present (currently empty)
├── .github/FUNDING.yml          # Sponsor/support metadata
└── README.md + README.*.md      # Canonical + multilingual docs
```

## ✅ 先決條件
- Ubuntu/Linux 或 Windows。
- 已安裝且可存取 MT5（`terminal64.exe`），並且終端已啟動/登入。
- Python 3.10+（建議 3.11 以符合 MetaTrader5 相容性）。
- PostgreSQL 實例。

## 🛠️ 安裝

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

輔助腳本：
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

## ⚙️ 設定
將 `.env.example` 複製為 `.env`，並調整變數。

### 核心變數
| Variable | Purpose |
|---|---|
| `DATABASE_URL` | 首選 PostgreSQL DSN |
| `DATABASE_MT_URL` | `DATABASE_URL` 未設定時的備援 DSN |
| `DATABASE_QT_URL` | 第二層備援 DSN |
| `MT5_PATH` | `terminal64.exe` 路徑（Wine 或原生） |
| `MT5_LOGIN` / `MT5_PASSWORD` / `MT5_SERVER` | 若 MT5 終端會話已登入可選填 |
| `PORT` | 伺服器埠（預設 `8888`） |

### 可選變數
- `FMP_API_KEY`, `ALPHAVANTAGE_API_KEY`：用於新聞增強。
- `TRADING_ENABLED`（預設 `0`，設為 `1` 允許下單端點）。
- `TRADING_VOLUME`（預設手動交易量）。
- `AUTO_FETCH`, `AUTO_FETCH_SYMBOL`, `AUTO_FETCH_TF`, `AUTO_FETCH_COUNT`, `AUTO_FETCH_SEC`。
- `PIN_DEFAULTS_TO_XAU_H1=1`：強制 UI 啟動預設 symbol/timeframe。
- `LOG_LEVEL`, `LOG_BACKFILL`，以及透過 `/api/preferences` 與環境設定的帳戶/輪詢偏好。

備註：
- `MT5_PATH` 應指向 MT5 安裝腳本所使用 Wine prefix 中的 `terminal64.exe`。
- 若終端會話已登入，可省略 MT5 憑證；應用程式會嘗試重用該會話。

## 🚀 使用方式

### 啟動伺服器
```bash
python -m app.server
```

### 開啟 UI
- 桌機 UI：`http://localhost:8888/`
- 行動 UI：`http://localhost:8888/app`

### 常見流程
1. 從 MT5 抓取 bars 並持久化到 Postgres。
2. 從 DB 讀取 bars 供圖表使用。
3. 執行 health/tech/news 分析。
4. 產生 AI trade plan。
5. 在安全防護下執行或平倉。

## 🔌 API 端點（實務）
- `GET /api/fetch?symbol=XAUUSD&tf=H1&count=500[&mode=inc|full][&persist=1]`
  - 從 MT5 抓取並 upsert 到 DB。
  - 若 `persist=1`，伺服器會保存 `last_symbol/last_tf/last_count` 預設值；bulk/background 抓取應省略此參數以避免覆蓋 UI 選擇。
- `GET /api/fetch_bulk`：批次/排程匯入。
- `GET /api/data?symbol=XAUUSD&tf=H1&limit=500`：從 DB 讀取圖表資料。
- `GET /api/strategy/run?symbol=XAUUSD&tf=H1&fast=20&slow=50`
  - 執行 SMA(20/50) crossover 並回傳 signal payload。
  - 重要實作說明：目前此端點在 server 程式碼中已停用 strategy 驅動下單；下單執行改由 trade 端點處理。
- `POST /api/trade`：從 UI 手動 Buy/Sell，受 `TRADING_ENABLED` 管控。
- `POST /api/trade/execute_plan`：執行已生成計畫，包含 pre-close 與 stop-distance 檢查。
- `POST /api/close`：平掉持倉（為安全起見，即使 `TRADING_ENABLED=0` 也允許）：
  - 目前 symbol：form body `symbol=...`；可選 `side=long|short|both`。
  - 全部 symbols：`?scope=all`，可選 `&side=...`。
  - 回應包含 `closed_count` 與各 ticket 結果。
- `POST /api/close_tickets`：按 ticket 關閉指定子集合。
- `GET /api/positions`, `GET /api/positions/all`。
- `GET /api/stl`, `POST /api/stl/compute`, `POST /api/stl/prune`, `POST /api/stl/prune_all`, `DELETE /api/stl/run/{id}`。
- `GET /api/news`, `POST /api/news/backfill_forex`, `POST /api/news/analyze`。
- `GET /api/health/freshness`, `GET /api/tech/freshness`, `GET|POST /api/health/run`, `GET /api/health/runs`。
- `POST /api/preferences` 與相關偏好讀取端點。
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
請參考 `sql/schema.sql`。

重點：
- `ohlc_bars` 的複合主鍵 `(symbol, timeframe, ts)` 可防止重複 bars。
- 匯入流程使用 `ON CONFLICT ... DO UPDATE`。
- 其他資料表支援 STL runs/components、preferences、news articles、health runs、account series、closed deals，以及 signal/order-plan 關聯。

## 🛡️ 交易控制與安全
- 環境防護：`TRADING_ENABLED=0` 為預設，會停用手動/計畫執行端點的下單行為。
- UI 的 `Auto` 表頭行為會排程 strategy 檢查，但不會繞過交易安全閘。
- 即使停用交易，仍刻意允許平倉操作。
- 執行流程使用 safe-max 與 symbol/kind 權重限制曝險。

## 📈 STL 自動計算切換
- STL 自動計算可透過 STL 面板的 `Auto STL` 開關，按 symbol x timeframe 控制。
- 預設為 OFF，以降低大型/慢速情境的 UI 延遲。
- 開啟後，缺失或過舊 STL 可自動計算；否則請使用手動重算控制。
- 狀態會透過 `/api/preferences` 的 `stl_auto_compute:SYMBOL:TF` 等鍵持久化，也會寫入 local storage 以加速啟動。

## 🧷 記住上次選擇
- 伺服器會保存 `last_symbol`, `last_tf`, `last_count`，並將預設值注入模板。
- UI 也會把 `last_symbol`/`last_tf` 存入 `localStorage`。
- `/?reset=1` 會在該次載入忽略已保存偏好。
- `PIN_DEFAULTS_TO_XAU_H1=1` 可強制啟動預設值。

## 🤖 AI Trade Plan 提示上下文
請求 AI trade plan 時，伺服器會先確保目前 symbol/timeframe 具備最新的 Basic Health 與 Tech Snapshot runs（若缺失會先建立），接著從以下區塊建立提示上下文：
- Basic health 區塊，
- Tech AI 區塊，
- 即時 technical snapshot 區塊。

## 🧰 開發備註
- 主要執行期依賴：`tornado`, `asyncpg`, `MetaTrader5`, `numpy`, `python-dotenv`, `requests`, `httpx`, `statsmodels`, `openai`。
- 目前尚未配置正式自動化測試套件；現行流程以 smoke tests 與手動 UI 驗證為主。
- 建議 smoke tests：
  - `python scripts/test_mixed_ai.py`
  - `python scripts/test_fmp.py`
  - `python scripts/test_fmp_endpoints.py`
- 推送前建議手動檢查：
  - 平移/縮放同步，
  - STL overlay/period line 行為，
  - 交易控制（含平倉安全行為），
  - 新聞面板 fallback 行為。

## 🧯 疑難排解
| Symptom | Action |
|---|---|
| MT5 initialize failed | 將 `MT5_PATH` 設為正確 `terminal64.exe`，並至少手動啟動終端一次 |
| MT5 login failed | 確認 `MT5_SERVER` 與終端伺服器字串完全一致，或省略憑證並重用現有登入會話 |
| No data for symbol | 檢查券商 symbol 命名與 Market Watch 可見性（`XAUUSD`, `XAUUSD.a`, `GOLD` 等） |
| Postgres connection issues | 驗證 `DATABASE_URL`，再執行 `psql "$DATABASE_URL" -c 'select 1;'` |
| Slow or stale UI analytics | 在重負載 pairs/TFs 關閉 auto STL，改用手動重算 |

## 🛣️ 路線圖
- 將 `i18n/` 執行期資產擴展到 README 以外的多語文件。
- 新增正式自動化測試（API + 整合 + UI smoke automation）。
- 改善部署打包與可重現環境設定檔。
- 持續強化 AI 計畫驗證與執行安全防護。

## 🤝 貢獻
- 保持 patch 小而聚焦。
- 在適用時使用清楚的 commit 前綴（例如：`UI: ...`, `Server: ...`, `References: ...`）。
- 避免無關的格式化變動。
- UI 變更相關時請附上 screenshots/GIFs。
- PR 前請執行 smoke tests 與本機瀏覽器檢查。

## ❤️ 支援 / 贊助
贊助與支援連結設定於 `.github/FUNDING.yml`：
- GitHub Sponsors: https://github.com/sponsors/lachlanchen
- Lazying.art: https://lazying.art
- Chat: https://chat.lazying.art
- OnlyIdeas: https://onlyideas.art

## 📚 參考資料
- `references/ai-trader-overview.md`
- `references/database_setup_postgres.md`
- `references/mt5_python_setup_ubuntu.md`
- `references/mt4_vs_mt5.md`
- `references/llm_trading_system.md`
- `references/release_deploy.md`
- `references/pnl_debugging.md`

## 📄 授權
截至 2026-02-28，此倉庫中不存在 `LICENSE` 檔案。

假設：倉庫內目前尚未明確指定授權條款；在維護者加入正式授權檔案前，保留此說明。
