[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


<p align="center">
  <img src="https://raw.githubusercontent.com/lachlanchen/lachlanchen/main/logos/banner.png" alt="LazyingArt banner" />
</p>

# MetaTrader QT - 量化交易入门套件（Micro Quant 哲学）

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Backend](https://img.shields.io/badge/Backend-Tornado-2d7cbf)
![Database](https://img.shields.io/badge/Database-PostgreSQL-336791?logo=postgresql&logoColor=white)
![Broker](https://img.shields.io/badge/Broker%20Bridge-MetaTrader5-1f6feb)
![UI](https://img.shields.io/badge/UI-Lightweight%20Charts%20%2B%20Chart.js-0ea5e9)
![Status](https://img.shields.io/badge/README-Expanded-success)

## 📸 截图
![Micro Quant UI](figures/demos/micro-quant-ui.png)

<p align="center">
  <a href="https://my.roboforex.com/en/?a=efx" target="_blank" rel="noopener noreferrer">
    <button style="padding: 0.65rem 1.25rem; font-weight: 600; border-radius: 999px; border: none; color: white; background: #0060ff; cursor: pointer;">
      DATA Source
    </button>
  </a>
</p>

## 🧭 概览
Micro Quant 的重点不在炫目的仪表盘，而在可重复的交易逻辑栈：它从 MetaTrader 5 拉取 OHLC 数据，持久化到 Postgres，并通过分层的 AI 引导信号（基础新闻、技术快照、交易计划、STL 叠加）评估系统化决策。UI 也围绕这一理念设计，提供对齐切换、带理由的平仓、持久化偏好设置和信息密集的执行面板，让服务端在你检查日志与证据时也能安全运行周期任务或模态交易流程。

静态落地页（Quant by Lazying.art）位于 `docs/`，通过 GitHub Pages 发布（`trade.lazying.art`，由 `docs/CNAME` 指向）。仓库还包含 AI Trade Plan 提示词参考、集成说明和运维文档。

### 快速一览
| 区域 | 作用 |
|---|---|
| Data | 拉取 MT5 OHLC 并 upsert 到 PostgreSQL |
| Analytics | 运行 health/news/tech 与 STL 工作流 |
| Decisioning | 基于分层上下文生成 AI trade plan |
| Execution | 在安全保护下执行/控制交易流程 |
| UI | 桌面与移动端视图，图表流程同步 |

## 🧠 核心理念
- **Chain of truth**：基础新闻检查（文本 + 分数）与技术快照（重技术上下文 + STL）共同输入到每个 symbol/timeframe 的单一 AI trade plan。周期自动运行与手动模态运行共享同一条流水线和推理日志。
- **Alignment-first execution**：Accept-Tech/Hold-Neutral 切换、ignore-basics 开关和 partial-close 包装器确保有意识地遵循 Tech，在需要时先平反向仓再开新仓，并尽量减少不必要离场。
- **Immutable data**：每次抓取都通过 `ON CONFLICT` 规范写入 Postgres，而 `/api/data` 为 UI 读取清洗后的序列。偏好项（auto volumes、`close_fraction`、hide-tech 开关、STL auto-compute）通过 `/api/preferences` 持久化。
- **Safety-first trading**：`TRADING_ENABLED` 与 `safe_max` 强制手动/自动权限控制。`/api/close` 和周期运行器可记录平仓原因（tech neutral、misalignment 等）以支持追溯。

## ✨ 功能
- MT5 OHLC 入库到 Postgres（`/api/fetch`, `/api/fetch_bulk`）。
- 图表 UI：`/`（桌面）与 `/app`（移动），模板中使用 Chart.js + Lightweight Charts。
- STL 分解工作流（`/api/stl`, `/api/stl/compute`, prune/delete 相关端点）。
- 新闻抓取与分析（`/api/news`, `/api/news/backfill_forex`, `/api/news/analyze`）。
- AI 工作流编排（`/api/health/run`, `/api/health/runs`, `/api/ai/trade_plan`）。
- 手动交易执行（`/api/trade`, `/api/trade/execute_plan`），由 `TRADING_ENABLED` 保护。
- 仓位风险操作（`/api/positions*`, `/api/close`, `/api/close_tickets`），为安全起见允许执行平仓操作。
- WebSocket 更新流：`/ws/updates`。

## 🗂️ 项目结构
```text
metatrader_qt/
├── app/
│   ├── server.py                # Tornado 应用、路由、编排
│   ├── db.py                    # asyncpg 访问层 + schema 初始化
│   ├── mt5_client.py            # MetaTrader5 桥接 + 下单/数据操作
│   ├── news_fetcher.py          # FMP/AlphaVantage 聚合与过滤
│   └── strategy.py              # SMA crossover 辅助器
├── templates/
│   ├── index.html               # 桌面端主 UI
│   └── mobile.html              # 面向移动端的 UI
├── static/                      # PWA 资源（icons/manifest/service worker）
├── sql/
│   └── schema.sql               # 核心数据库 schema
├── scripts/
│   ├── test_mixed_ai.py         # Mixed AI 冒烟测试
│   ├── test_fmp.py              # FMP 冒烟测试
│   ├── test_fmp_endpoints.py    # FMP 端点探测脚本
│   ├── setup_windows.ps1        # Windows 环境初始化
│   ├── run_windows.ps1          # Windows 运行辅助脚本
│   └── bootstrap_venv311.sh     # Linux/mac Python 3.11 辅助脚本
├── docs/                        # GitHub Pages 落地站点
├── references/                  # 运维/安装说明
├── strategies/llm/              # Prompt/config JSON 文件
├── llm_model/echomind/          # LLM provider 封装
├── i18n/                        # 已存在（当前为空）
├── .github/FUNDING.yml          # 赞助/支持元数据
└── README.md + README.*.md      # 主 README + 多语言文档
```

## ✅ 前置条件
- Ubuntu/Linux 或 Windows。
- 已安装并可访问 MT5（`terminal64.exe`），且终端已运行/登录。
- Python 3.10+（建议 3.11 以获得 MetaTrader5 兼容性）。
- PostgreSQL 实例。

## 🛠️ 安装

### Windows（PowerShell）
```powershell
# 1) 使用 Python 3.11 创建 venv（MetaTrader5 尚无 3.13 wheel）
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt

# 2) 配置环境变量
Copy-Item .env.example .env
# 编辑 .env，设置 DATABASE_URL、MT5_PATH（例如 C:\Program Files\MetaTrader 5\terminal64.exe）以及你的 MT5 模拟账户凭据
# 为当前会话加载 env
Get-Content .env | Where-Object { $_ -and $_ -notmatch '^#' } | ForEach-Object { $n,$v = $_ -split '=',2; [Environment]::SetEnvironmentVariable($n, $v, 'Process') }

# 3) 启动应用
python -m app.server
# 打开 http://localhost:8888
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

# 可选：本地 3.11 venv（如果你的全局/Conda Python 是 3.13）
# 系统中需要有 python3.11
# sudo apt install python3.11 python3.11-venv
bash scripts/bootstrap_venv311.sh
source .venv311/bin/activate

# DB（按需替换为你的用户名/密码）
# createdb -h localhost -p 5432 -U lachlan metatrader_db

# 配置环境变量
cp .env.example .env
# 在 .env 中填写 MT5 路径和凭据
set -a; source .env; set +a

# 启动应用
python -m app.server
# 打开 http://localhost:8888
```

## ⚙️ 配置
将 `.env.example` 复制为 `.env` 并调整对应值。

### 核心变量
| 变量 | 用途 |
|---|---|
| `DATABASE_URL` | 首选 PostgreSQL DSN |
| `DATABASE_MT_URL` | 当 `DATABASE_URL` 未设置时的回退 DSN |
| `DATABASE_QT_URL` | 二级回退 DSN |
| `MT5_PATH` | `terminal64.exe` 路径（Wine 或原生） |
| `MT5_LOGIN` / `MT5_PASSWORD` / `MT5_SERVER` | 若 MT5 终端会话已登录则可选 |
| `PORT` | 服务端口（默认 `8888`） |

### 可选变量
- `FMP_API_KEY`, `ALPHAVANTAGE_API_KEY`：用于新闻增强。
- `TRADING_ENABLED`（默认 `0`，设为 `1` 才允许下单端点）。
- `TRADING_VOLUME`（手动交易默认手数）。
- `AUTO_FETCH`, `AUTO_FETCH_SYMBOL`, `AUTO_FETCH_TF`, `AUTO_FETCH_COUNT`, `AUTO_FETCH_SEC`。
- `PIN_DEFAULTS_TO_XAU_H1=1`：强制 UI 启动默认 symbol/timeframe。
- `LOG_LEVEL`, `LOG_BACKFILL`，以及通过 `/api/preferences` 和环境变量设置的账户/轮询相关偏好。

说明：
- `MT5_PATH` 应指向 MT5 安装脚本所用 Wine 前缀下的 `terminal64.exe`。
- 如果终端会话已登录，可不填 MT5 凭据；应用会尝试复用该会话。

## 🚀 使用

### 启动服务
```bash
python -m app.server
```

### 打开 UI
- 桌面端 UI：`http://localhost:8888/`
- 移动端 UI：`http://localhost:8888/app`

### 常见流程
1. 从 MT5 抓取 K 线并持久化到 Postgres。
2. 从 DB 读取 K 线用于图表展示。
3. 运行 health/tech/news 分析。
4. 生成 AI trade plan。
5. 在安全保护下执行交易或平仓。

## 🔌 API 端点（实用）
- `GET /api/fetch?symbol=XAUUSD&tf=H1&count=500[&mode=inc|full][&persist=1]`
  - 从 MT5 拉取并 upsert 到 DB。
  - 若 `persist=1`，服务端会保存 `last_symbol/last_tf/last_count` 默认值；bulk/background 抓取应省略此参数，避免覆盖 UI 选择。
- `GET /api/fetch_bulk`：批量/定时抓取。
- `GET /api/data?symbol=XAUUSD&tf=H1&limit=500`：从 DB 读取图表数据。
- `GET /api/strategy/run?symbol=XAUUSD&tf=H1&fast=20&slow=50`
  - 运行 SMA(20/50) crossover 并返回信号负载。
  - 重要实现说明：该端点当前在服务端代码中已禁用基于策略的直接下单；订单执行由 trade 相关端点处理。
- `POST /api/trade`：来自 UI 的手动 Buy/Sell，受 `TRADING_ENABLED` 限制。
- `POST /api/trade/execute_plan`：执行已生成计划，包含预平仓和止损距离检查。
- `POST /api/close`：平掉仓位（出于安全考虑，即使 `TRADING_ENABLED=0` 也允许）：
  - 当前 symbol：表单体 `symbol=...`；可选 `side=long|short|both`。
  - 全部 symbols：`?scope=all`，可选 `&side=...`。
  - 响应包含 `closed_count` 和逐 ticket 结果。
- `POST /api/close_tickets`：按请求的 ticket 子集平仓。
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
# 拉取 XAUUSD 的 500 根 H1 K 线
curl "http://localhost:8888/api/fetch?symbol=XAUUSD&tf=H1&count=500"

# 从 DB 读取 200 根 K 线
curl "http://localhost:8888/api/data?symbol=XAUUSD&tf=H1&limit=200"

# 运行 SMA 信号计算
curl "http://localhost:8888/api/strategy/run?symbol=XAUUSD&tf=H1&fast=20&slow=50"

# 平掉当前 symbol 的 long 仓位
curl -X POST "http://localhost:8888/api/close" -d "symbol=XAUUSD&side=long"

# 平掉所有 symbol 的 short 仓位
curl -X POST "http://localhost:8888/api/close?scope=all&side=short"
```

## 🗄️ 数据库与 Schema
参见 `sql/schema.sql`。

要点：
- `ohlc_bars` 中的复合主键 `(symbol, timeframe, ts)` 可防止重复 K 线。
- 入库使用 `ON CONFLICT ... DO UPDATE`。
- 其他表支持 STL runs/components、preferences、news articles、health runs、account series、closed deals，以及 signal/order-plan 关联。

## 🛡️ 交易控制与安全
- 环境保护：默认 `TRADING_ENABLED=0`，禁用手动/计划执行端点的下单。
- UI 中 `Auto` 头部行为只负责调度策略检查，不会绕过交易安全门。
- 即使禁用交易，也有意保留平仓能力。
- 执行流程使用 safe-max 与 symbol/kind 权重以限制风险敞口。

## 📈 STL 自动计算开关
- STL 自动计算按 symbol x timeframe 粒度控制，对应 STL 面板中的 `Auto STL` 开关。
- 默认 OFF，以降低大数据/慢场景下的 UI 卡顿。
- 开启后，缺失或过期 STL 可自动计算；否则请使用手动重算控件。
- 状态通过 `/api/preferences` 中类似 `stl_auto_compute:SYMBOL:TF` 的键持久化，同时写入本地存储以加快启动。

## 🧷 记住上次选择
- 服务端会持久化 `last_symbol`、`last_tf`、`last_count` 并注入模板默认值。
- UI 也会在 `localStorage` 中保存 `last_symbol`/`last_tf`。
- `/?reset=1` 会在本次页面加载时忽略已存偏好。
- `PIN_DEFAULTS_TO_XAU_H1=1` 可强制启动默认值。

## 🤖 AI Trade Plan 提示词上下文
请求 AI trade plan 时，服务端会确保当前 symbol/timeframe 有最新 Basic Health 与 Tech Snapshot 运行结果（缺失时自动创建），然后使用以下内容构建提示词上下文：
- Basic health block，
- Tech AI block，
- Live technical snapshot block。

## 🧰 开发说明
- 主要运行时依赖：`tornado`, `asyncpg`, `MetaTrader5`, `numpy`, `python-dotenv`, `requests`, `httpx`, `statsmodels`, `openai`。
- 目前尚未配置正式自动化测试套件；当前流程以冒烟测试与手动 UI 校验为主。
- 推荐冒烟测试：
  - `python scripts/test_mixed_ai.py`
  - `python scripts/test_fmp.py`
  - `python scripts/test_fmp_endpoints.py`
- 推送前建议手动检查：
  - 平移/缩放同步，
  - STL 叠加/周期线行为，
  - 交易控制（含平仓安全行为），
  - 新闻面板回退行为。

## 🧯 故障排查
| 症状 | 处理方式 |
|---|---|
| MT5 initialize failed | 将 `MT5_PATH` 设为准确的 `terminal64.exe`，并至少手动运行一次终端 |
| MT5 login failed | 确保 `MT5_SERVER` 与终端内服务器字符串完全一致，或省略凭据并复用活动会话 |
| No data for symbol | 检查券商符号命名与 Market Watch 可见性（`XAUUSD`, `XAUUSD.a`, `GOLD` 等） |
| Postgres connection issues | 检查 `DATABASE_URL`，然后运行 `psql "$DATABASE_URL" -c 'select 1;'` |
| Slow or stale UI analytics | 在重负载品种/周期关闭自动 STL 并手动重算 |

## 🛣️ 路线图
- 将 `i18n/` 运行时资源扩展到 README 多语言文档之外。
- 增加正式自动化测试（API + 集成 + UI 冒烟自动化）。
- 改进部署打包与可复现环境配置。
- 持续完善 AI 计划校验与执行安全防护。

## 🤝 贡献
- 保持补丁小且聚焦。
- 适用时使用清晰的提交前缀（例如：`UI: ...`, `Server: ...`, `References: ...`）。
- 避免无关的格式化噪音。
- UI 变更相关时附带截图/GIF。
- 提交 PR 前运行冒烟测试并在本地浏览器完成检查。

## ❤️ 支持 / 赞助
赞助与支持链接配置在 `.github/FUNDING.yml`：
- GitHub Sponsors: https://github.com/sponsors/lachlanchen
- Lazying.art: https://lazying.art
- Chat: https://chat.lazying.art
- OnlyIdeas: https://onlyideas.art

## 📚 参考资料
- `references/ai-trader-overview.md`
- `references/database_setup_postgres.md`
- `references/mt5_python_setup_ubuntu.md`
- `references/mt4_vs_mt5.md`
- `references/llm_trading_system.md`
- `references/release_deploy.md`
- `references/pnl_debugging.md`

## 📄 许可证
截至 2026-02-28，本仓库中不存在 `LICENSE` 文件。

Assumption：仓库内目前未明确许可证条款；在维护者添加显式许可证文件之前保留此说明。
