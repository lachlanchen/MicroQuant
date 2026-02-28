[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# MetaTrader QT - 量化交易入门（Micro Quant 哲学）

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Backend](https://img.shields.io/badge/Backend-Tornado-2d7cbf)
![Database](https://img.shields.io/badge/Database-PostgreSQL-336791?logo=postgresql&logoColor=white)
![Broker](https://img.shields.io/badge/Broker%20Bridge-MetaTrader5-1f6feb)
![UI](https://img.shields.io/badge/UI-Lightweight%20Charts%20%2B%20Chart.js-0ea5e9)
![Status](https://img.shields.io/badge/README-Expanded-success)
![GitHub%20Stars](https://img.shields.io/github/stars/lachlanchen/MicroQuant?style=for-the-badge&logo=github&logoColor=white&labelColor=0f172a&color=0ea5e9)
![GitHub%20Issues](https://img.shields.io/github/issues/lachlanchen/MicroQuant?style=for-the-badge&logo=github&logoColor=white&labelColor=0f172a&color=ef4444)

## 🎯 项目快照

| 关注点 | 技术栈 |
|---|---|
| 运行环境 | Tornado + asyncpg + WebSocket |
| 交易 | MetaTrader5 + 分层 AI/新闻/技术上下文 |
| 存储 | 使用确定性 upsert 的 PostgreSQL |
| 部署 | PWA 资源 + 适配桌面/移动的浏览器优先界面 |

## 目录
- [📸 截图](#-screenshot)
- [概览](#-overview)
- [核心理念](#-core-philosophy)
- [功能](#-features)
- [项目结构](#-project-structure)
- [先决条件](#-prerequisites)
- [安装](#-installation)
- [配置](#️-configuration)
- [使用](#-usage)
- [API 接口（实用）](#-api-endpoints-practical)
- [示例](#-examples)
- [数据库与 Schema](#-database--schema)
- [交易控制与安全](#️-trading-controls--safety)
- [STL 自动计算开关](#-stl-auto-compute-toggle)
- [记住上次选择](#-remembering-last-selection)
- [AI 交易计划上下文](#️-ai-trade-plan-prompt-context)
- [开发说明](#-development-notes)
- [故障排查](#-troubleshooting)
- [路线图](#-roadmap)
- [贡献](#-contributing)
- [参考资料](#-references)
- [支持](#️-support)
- [许可证](#-license)

## 📸 截图
![Micro Quant UI](figures/demos/micro-quant-ui.png)

[![DATA Source](https://img.shields.io/badge/Data_Source-RoboForex-0060ff?style=for-the-badge&labelColor=0a4eb3)](https://my.roboforex.com/en/?a=efx)

## 🧭 概览
Micro Quant 的核心不是炫目的面板，而是可复用的交易逻辑栈：它从 MetaTrader 5 拉取 OHLC 数据，写入 PostgreSQL，并基于分层 AI 辅助信号（基础新闻、技术快照、交易计划与 STL 覆盖）进行系统化决策评估。界面设计也遵循这一理念，提供对齐切换、带原因的平仓、偏好持久化和数据丰富的执行面板，便于你在查看日志与证据时，让服务端安全地运行周期化或模态化交易流。

静态落地页（Quant by Lazying.art）位于 `docs/`，通过 GitHub Pages 发布（`trade.lazying.art`，由 `docs/CNAME` 承载）。仓库还包含 AI 交易计划提示词、集成说明和运营文档。

### 一览
| 模块 | 职能 |
|---|---|
| 数据 | 拉取 MT5 OHLC 并 upsert 到 PostgreSQL |
| 分析 | 运行 health/news/tech 与 STL 工作流 |
| 决策 | 使用分层上下文构建 AI 交易计划 |
| 执行 | 在风控保护下执行/管控交易流 |
| 界面 | 提供桌面与移动端视图，支持图表流程同步 |

## 🧠 核心理念
- **事实链（Chain of truth）**：基础新闻校验（文本 + 打分）与技术快照（完整技术上下文 + STL）共同生成每个品种/周期的单一 AI 交易计划。周期性自动运行和手动模态运行共享同一条流水线与推理日志。
- **先对齐再执行**：`Accept-Tech` / `Hold-Neutral` 切换、`ignore-basics` 开关与部分平仓封装器确保技术方向被有意遵循；必要时先平掉反向仓位再开新仓，同时减少非必要离场。
- **不可变数据（Immutable data）**：每次抓取都通过 `ON CONFLICT` 规则写入 Postgres；`/api/data` 向界面返回清洗后的序列。偏好项（`auto` 设置、`close_fraction`、`hide-tech` 切换、STL 自动计算）通过 `/api/preferences` 持久化。
- **安全优先交易（Safety-first）**：`TRADING_ENABLED` 与 `safe_max` 负责手动/自动权限控制。`/api/close` 与周期任务会记录平仓原因（如 tech neutral、misalignment）以便追溯。

## ✨ 功能
- MT5 OHLC 采集到 Postgres（`/api/fetch`, `/api/fetch_bulk`）。
- 根路由 `/`（桌面）与 `/app`（移动）提供图表界面，模板里使用 Chart.js + Lightweight Charts。
- STL 分解工作流（`/api/stl`, `/api/stl/compute`，含 prune/delete 相关端点）。
- 新闻采集与分析（`/api/news`, `/api/news/backfill_forex`, `/api/news/analyze`）。
- AI 工作流编排（`/api/health/run`, `/api/health/runs`, `/api/ai/trade_plan`）。
- 手动交易执行（`/api/trade`, `/api/trade/execute_plan`），受 `TRADING_ENABLED` 控制。
- 持仓风险操作（`/api/positions*`, `/api/close`, `/api/close_tickets`）在明确安全规则下允许平仓。
- `/ws/updates` 的 WebSocket 更新流提供实时提示与刷新信号。
- 提供可安装的 PWA 与静态资源 Dashboard。

## 🗂️ 项目结构
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

## ✅ 先决条件
- Ubuntu/Linux 或可访问终端的 Windows 环境。
- 已安装 MetaTrader 5（`terminal64.exe`）并按需登录。
- Python 3.10+（建议 3.11 以提升与 MetaTrader5 wheels 的兼容性）。
- 可供应用服务器访问的 PostgreSQL 实例。
- 可选新闻接口 API Key：
  - FMP
  - Alpha Vantage

## 🛠️ 安装

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

辅助脚本：
```powershell
scripts\setup_windows.ps1
scripts\run_windows.ps1
```

### Linux/macOS（bash）
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Alternative: local 3.11 venv (if your global Python is newer)
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

## ⚙️ 配置
将 `.env.example` 复制为 `.env` 并按需调整。

### 核心变量
| 变量 | 用途 |
|---|---|
| `DATABASE_URL` | 首选 PostgreSQL DSN |
| `DATABASE_MT_URL` | `DATABASE_URL` 未设置时的备选 DSN |
| `DATABASE_QT_URL` | 次级备选 DSN |
| `MT5_PATH` | `terminal64.exe` 路径（Wine 或原生） |
| `MT5_LOGIN` / `MT5_PASSWORD` / `MT5_SERVER` | 若 MT5 会话已登录可留空 |
| `PORT` | 服务器端口（默认 `8888`） |

### 可选变量
- `FMP_API_KEY`, `ALPHAVANTAGE_API_KEY` 用于新闻增强。
- `TRADING_ENABLED`（默认 `0`，设置 `1` 以启用下单端点）。
- `TRADING_VOLUME`（默认手动下单量）。
- `AUTO_FETCH`, `AUTO_FETCH_SYMBOL`, `AUTO_FETCH_TF`, `AUTO_FETCH_COUNT`, `AUTO_FETCH_SEC`。
- `PIN_DEFAULTS_TO_XAU_H1=1` 强制 UI 启动默认品种/周期。
- `LOG_LEVEL`, `LOG_BACKFILL`，以及通过 `/api/preferences` 与环境变量设置的账户和轮询偏好。

注意：
- `MT5_PATH` 应指向你在 MT5 安装脚本使用的 Wine 前缀中的 `terminal64.exe`。
- 当终端会话已登录时，可省略 MT5 凭据，系统会尝试复用该会话。

## 🚀 使用

### 启动服务
```bash
python -m app.server
```

### 打开界面
- 桌面 UI：`http://localhost:8888/`
- 移动 UI：`http://localhost:8888/app`

### 常用 API 地址
| 界面 | URL | 用途 |
|---|---|---|
| 桌面 | `http://localhost:8888/` | K 线图与桌面化交易流程 |
| 移动 | `http://localhost:8888/app` | 触控优先布局，控件更紧凑 |
| API 健康检查 | `http://localhost:8888/api/health/freshness` | 快速检查数据与服务就绪度 |

### 常规流程
1. 从 MT5 抓取 K 线并持久化到 Postgres。
2. 从数据库读取 K 线用于图表。
3. 运行 health/tech/news 分析。
4. 生成 AI 交易计划。
5. 在安全规则下执行交易或平仓。

## 🔌 API 接口（实用）
- `GET /api/fetch?symbol=XAUUSD&tf=H1&count=500[&mode=inc|full][&persist=1]`
  - 从 MT5 拉取数据并 upsert 到数据库。
  - 若 `persist=1`，服务端会保存 `last_symbol/last_tf/last_count` 作为默认值；批量/后台抓取应避免该参数，以免覆盖 UI 选择。
- `GET /api/fetch_bulk` — 批量/定时抓取。
- `GET /api/data?symbol=XAUUSD&tf=H1&limit=500` — 从数据库读取图表数据。
- `GET /api/strategy/run?symbol=XAUUSD&tf=H1&fast=20&slow=50`
  - 执行 SMA(20/50) 交叉计算并返回 signal payload。
  - 重要实现说明：当前该端点在服务端代码中已禁用策略驱动下单；下单执行由交易相关端点处理。
- `POST /api/trade` — 由 UI 手动 Buy/Sell，受 `TRADING_ENABLED` 保护。
- `POST /api/trade/execute_plan` — 执行已生成的计划，包含预先平仓和止损距离检查。
- `POST /api/close` — 平仓（出于安全考虑，即使 `TRADING_ENABLED=0` 也可使用）：
  - 当前品种：form body `symbol=...`；可选 `side=long|short|both`。
  - 全部品种：`?scope=all`，可选 `&side=...`。
  - 响应包含 `closed_count` 与逐 ticket 结果。
- `POST /api/close_tickets` — 按 ticket 关闭指定子集。
- `GET /api/positions`, `GET /api/positions/all`。
- `GET /api/stl`, `POST /api/stl/compute`, `POST /api/stl/prune`, `POST /api/stl/prune_all`, `DELETE /api/stl/run/{id}`。
- `GET /api/news`, `POST /api/news/backfill_forex`, `POST /api/news/analyze`。
- `GET /api/health/freshness`, `GET /api/tech/freshness`, `GET|POST /api/health/run`, `GET /api/health/runs`。
- `POST /api/preferences` 及相关偏好读取端点。
- `GET /api/ai/trade_plan`。
- `GET /api/accounts`, `GET /api/account/current`, `POST /api/account/login`。
- `GET /ws/updates`。

## 🧪 示例
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

## 🗄️ 数据库与 Schema
参见 `sql/schema.sql`。

要点：
- `ohlc_bars` 的复合主键 `(symbol, timeframe, ts)` 防止重复 K 线。
- 入库流程使用 `ON CONFLICT ... DO UPDATE`。
- 其他表支持 STL 运行/组件、偏好设置、新闻文章、健康检查运行、账户序列、已平仓交易，以及信号与交易计划关联。

## 🛡️ 交易控制与安全
- 环境保护：默认 `TRADING_ENABLED=0` 会禁用手动/计划执行端点中的下单能力。
- UI 顶部 `Auto` 行为仅用于调度策略检查，不会绕过交易安全网关。
- 即使关闭交易，平仓操作也被故意允许。
- 执行流程使用 safe-max 与品种/类型权重控制风险敞口。

## 📈 STL 自动计算开关
- STL 自动计算通过 STL 面板中的 `Auto STL` 开关按品种 × 周期控制。
- 默认关闭，以降低大规模或慢速场景下的界面卡顿。
- 开启后可自动补算缺失或过期 STL；否则请使用手动重算控件。
- 状态通过 `/api/preferences` 的 `stl_auto_compute:SYMBOL:TF` 键持久化，并会写入本地存储以加快启动。

## 🧷 记住上次选择
- 服务端持久化 `last_symbol`、`last_tf`、`last_count` 并注入模板默认值。
- UI 也在 `localStorage` 存储 `last_symbol` 与 `last_tf`。
- `/?reset=1` 会忽略本次页面加载的存储偏好。
- `PIN_DEFAULTS_TO_XAU_H1=1` 可强制设置启动默认值。

## 🤖 AI 交易计划提示上下文
请求 AI 交易计划时，服务端先确保当前品种/周期有最新的 Basic Health 与 Tech Snapshot 运行结果（缺失则先创建），再使用以下内容构建提示上下文：
- Basic health block
- Tech AI block
- Live technical snapshot block

## 🧰 开发说明
- 主要运行依赖：`tornado`, `asyncpg`, `MetaTrader5`, `numpy`, `python-dotenv`, `requests`, `httpx`, `statsmodels`, `openai`。
- 当前尚未配置正式自动化测试套件；冒烟测试与手动 UI 校验是主要流程。
- 推荐冒烟测试：
  - `python scripts/test_mixed_ai.py`
  - `python scripts/test_fmp.py`
  - `python scripts/test_fmp_endpoints.py`
- 发布前手工检查：
  - pan/zoom 同步
  - STL overlay/period-line 行为
  - 交易控制（含平仓安全行为）
  - 新闻面板 fallback 行为

## 🧯 故障排查
| 症状 | 处理 |
|---|---|
| MT5 初始化失败 | 将 `MT5_PATH` 指向精确的 `terminal64.exe`，并至少手动启动一次终端 |
| MT5 登录失败 | 确认 `MT5_SERVER` 与终端服务器字符串完全一致，或省略凭据并复用当前活动会话 |
| 无法读取某品种数据 | 检查经纪商的品种命名及 Market Watch 可见性（如 `XAUUSD`, `XAUUSD.a`, `GOLD`） |
| Postgres 连接问题 | 检查 `DATABASE_URL`，然后运行 `psql "$DATABASE_URL" -c 'select 1;'` |
| UI 分析缓慢或卡顿 | 在高负荷品种/周期关闭自动 STL，改为手动重算 |

## 🛣️ 路线图
- 扩展 `i18n/` 运行时资产，不仅限于 README 多语言文档。
- 增加正式自动化测试（API + 集成 + UI 冒烟自动化）。
- 改进部署打包与可复现环境配置。
- 持续优化 AI 计划校验与执行安全机制。

## 🤝 贡献
- 保持补丁小而聚焦。
- 按场景使用清晰的提交前缀（例如：`UI: ...`, `Server: ...`, `References: ...`）。
- 避免无关的格式化变动。
- UI 变更可附截图/GIF。
- 发起 PR 前请执行冒烟测试并进行本地浏览器校验。

## 📚 参考资料
- `references/ai-trader-overview.md`
- `references/database_setup_postgres.md`
- `references/mt5_python_setup_ubuntu.md`
- `references/mt4_vs_mt5.md`
- `references/llm_trading_system.md`
- `references/release_deploy.md`
- `references/pnl_debugging.md`

## 📄 许可证
截至 2026-02-28，本仓库尚未提供 `LICENSE` 文件。

当前仓库中的许可条款尚未明确；请在维护者补充显式许可文件前保留此说明。


## ❤️ Support

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://camo.githubusercontent.com/24a4914f0b42c6f435f9e101621f1e52535b02c225764b2f6cc99416926004b7/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f446f6e6174652d4c617a79696e674172742d3045413545393f7374796c653d666f722d7468652d6261646765266c6f676f3d6b6f2d6669266c6f676f436f6c6f723d7768697465)](https://chat.lazying.art/donate) | [![PayPal](https://camo.githubusercontent.com/d0f57e8b016517a4b06961b24d0ca87d62fdba16e18bbdb6aba28e978dc0ea21/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f50617950616c2d526f6e677a686f754368656e2d3030343537433f7374796c653d666f722d7468652d6261646765266c6f676f3d70617970616c266c6f676f436f6c6f723d7768697465)](https://paypal.me/RongzhouChen) | [![Stripe](https://camo.githubusercontent.com/1152dfe04b6943afe3a8d2953676749603fb9f95e24088c92c97a01a897b4942/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f5374726970652d446f6e6174652d3633354246463f7374796c653d666f722d7468652d6261646765266c6f676f3d737472697065266c6f676f436f6c6f723d7768697465)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |
