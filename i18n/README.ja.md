[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


<p align="center">
  <img src="https://raw.githubusercontent.com/lachlanchen/lachlanchen/main/logos/banner.png" alt="LazyingArt banner" />
</p>

# MetaTrader QT - クオンツ取引スターター（Micro Quant Philosophy）

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Backend](https://img.shields.io/badge/Backend-Tornado-2d7cbf)
![Database](https://img.shields.io/badge/Database-PostgreSQL-336791?logo=postgresql&logoColor=white)
![Broker](https://img.shields.io/badge/Broker%20Bridge-MetaTrader5-1f6feb)
![UI](https://img.shields.io/badge/UI-Lightweight%20Charts%20%2B%20Chart.js-0ea5e9)
![Status](https://img.shields.io/badge/README-Expanded-success)

## 📸 スクリーンショット
![Micro Quant UI](figures/demos/micro-quant-ui.png)

<p align="center">
  <a href="https://my.roboforex.com/en/?a=efx" target="_blank" rel="noopener noreferrer">
    <button style="padding: 0.65rem 1.25rem; font-weight: 600; border-radius: 999px; border: none; color: white; background: #0060ff; cursor: pointer;">
      DATA Source
    </button>
  </a>
</p>

## 🧭 概要
Micro Quant は派手なダッシュボードよりも、再現可能な取引ロジックの積み上げを重視します。MetaTrader 5 から OHLC データを取得し、Postgres に永続化し、レイヤー化された AI ガイド信号（Basic news、Tech snapshot、trade plans、STL overlays）で体系的な意思決定を評価します。UI もこの思想に沿っており、アラインメント切り替え、理由付きクローズ、設定の永続化、情報量の多い執行ペインを備え、ログと根拠を確認しながらサーバー側で定期実行・モーダル実行のフローを安全に回せます。

静的ランディングページ（Quant by Lazying.art）は `docs/` 配下にあり、GitHub Pages（`docs/CNAME` 経由の `trade.lazying.art`）で公開されています。リポジトリには AI Trade Plan のプロンプト、連携メモ、運用ドキュメントも含まれます。

### ひと目で分かる構成
| Area | What it does |
|---|---|
| Data | MT5 の OHLC を取得して PostgreSQL に upsert |
| Analytics | health/news/tech と STL ワークフローを実行 |
| Decisioning | 多層コンテキストから AI trade plan を生成 |
| Execution | 安全ガードの背後で取引フローを実行・制御 |
| UI | チャート同期ワークフロー付きのデスクトップ/モバイル画面 |

## 🧠 コア哲学
- **Chain of truth**: Basic news checks（テキスト + スコア）と Tech snapshots（重いテクニカル文脈 + STL）を、銘柄/時間足ごとの単一 AI trade plan に集約します。定期 auto-run と手動 modal run は同じパイプラインと reasoning logs を共有します。
- **Alignment-first execution**: Accept-Tech/Hold-Neutral トグル、ignore-basics スイッチ、partial-close ラッパーによって、Tech を意図的に追従し、必要時は新規エントリー前に反対ポジションをクローズし、不要な手仕舞いを最小化します。
- **Immutable data**: すべての fetch は `ON CONFLICT` 運用で Postgres に書き込み、`/api/data` は UI 向けにサニタイズ済み系列を読み出します。設定（auto volume、`close_fraction`、hide-tech トグル、STL auto-compute）は `/api/preferences` で永続化されます。
- **Safety-first trading**: `TRADING_ENABLED` と `safe_max` が手動/自動の許可範囲を制御します。`/api/close` と periodic runner はクローズ理由（tech neutral、misalignment など）を記録でき、追跡可能性を確保します。

## ✨ 機能
- MT5 OHLC の Postgres 取り込み（`/api/fetch`, `/api/fetch_bulk`）。
- `/`（デスクトップ）と `/app`（モバイル）のチャート UI。テンプレートで Chart.js + Lightweight Charts を使用。
- STL 分解ワークフロー（`/api/stl`, `/api/stl/compute`, prune/delete 系エンドポイント）。
- ニュース取得と分析（`/api/news`, `/api/news/backfill_forex`, `/api/news/analyze`）。
- AI ワークフロー統合（`/api/health/run`, `/api/health/runs`, `/api/ai/trade_plan`）。
- 手動取引実行（`/api/trade`, `/api/trade/execute_plan`）。`TRADING_ENABLED` で保護。
- ポジションリスク操作（`/api/positions*`, `/api/close`, `/api/close_tickets`）。安全性のため close 操作は許可。
- `/ws/updates` で WebSocket 更新ストリームを配信。

## 🗂️ プロジェクト構成
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

## ✅ 前提条件
- Ubuntu/Linux または Windows。
- MT5 がインストール済みでアクセス可能（`terminal64.exe`）、かつターミナルが起動・ログイン済み。
- Python 3.10+（MetaTrader5 互換性の観点で 3.11 推奨）。
- PostgreSQL インスタンス。

## 🛠️ インストール

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

補助スクリプト:
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
`.env.example` を `.env` にコピーし、値を調整してください。

### コア変数
| Variable | Purpose |
|---|---|
| `DATABASE_URL` | 優先される PostgreSQL DSN |
| `DATABASE_MT_URL` | `DATABASE_URL` 未設定時のフォールバック DSN |
| `DATABASE_QT_URL` | 第2フォールバック DSN |
| `MT5_PATH` | `terminal64.exe` のパス（Wine またはネイティブ） |
| `MT5_LOGIN` / `MT5_PASSWORD` / `MT5_SERVER` | MT5 端末セッションが既にログイン済みなら任意 |
| `PORT` | サーバーポート（デフォルト `8888`） |

### 任意変数
- ニュース拡張用 `FMP_API_KEY`, `ALPHAVANTAGE_API_KEY`。
- `TRADING_ENABLED`（デフォルト `0`。注文系エンドポイントを許可するには `1`）。
- `TRADING_VOLUME`（手動取引のデフォルト数量）。
- `AUTO_FETCH`, `AUTO_FETCH_SYMBOL`, `AUTO_FETCH_TF`, `AUTO_FETCH_COUNT`, `AUTO_FETCH_SEC`。
- `PIN_DEFAULTS_TO_XAU_H1=1` で UI 起動時のデフォルト銘柄/時間足を固定。
- `LOG_LEVEL`, `LOG_BACKFILL`、および `/api/preferences` と環境変数経由の account/poll 関連設定。

注記:
- `MT5_PATH` は、MT5 インストールスクリプトで使う Wine prefix 内の `terminal64.exe` を指す必要があります。
- ターミナルセッションが既にログイン済みなら MT5 認証情報は省略可能で、アプリはそのセッションの再利用を試みます。

## 🚀 使い方

### サーバー起動
```bash
python -m app.server
```

### UI を開く
- デスクトップ UI: `http://localhost:8888/`
- モバイル UI: `http://localhost:8888/app`

### 一般的なワークフロー
1. MT5 からバーを取得して Postgres に保存。
2. チャート表示のため DB からバーを読み込み。
3. health/tech/news 分析を実行。
4. AI trade plan を生成。
5. 安全ガード下でポジションの実行またはクローズ。

## 🔌 API エンドポイント（実践）
- `GET /api/fetch?symbol=XAUUSD&tf=H1&count=500[&mode=inc|full][&persist=1]`
  - MT5 から取得して DB に upsert。
  - `persist=1` の場合、サーバーは `last_symbol/last_tf/last_count` を保存します。bulk/background fetch では UI 選択を上書きしないよう省略してください。
- `GET /api/fetch_bulk` — 一括/定期取り込み。
- `GET /api/data?symbol=XAUUSD&tf=H1&limit=500` — DB からチャートデータを読み込み。
- `GET /api/strategy/run?symbol=XAUUSD&tf=H1&fast=20&slow=50`
  - SMA(20/50) クロスオーバーを実行し、シグナル payload を返します。
  - 重要実装メモ: このエンドポイントからの strategy 駆動注文は現在サーバーコードで無効化されており、注文実行は trade 系エンドポイントで処理されます。
- `POST /api/trade` — UI からの手動 Buy/Sell。`TRADING_ENABLED` でゲート。
- `POST /api/trade/execute_plan` — 生成済み plan を実行。事前クローズと stop-distance チェックを含みます。
- `POST /api/close` — ポジション全決済（安全性のため `TRADING_ENABLED=0` でも許可）:
  - 現在銘柄: form body `symbol=...`; 任意で `side=long|short|both`。
  - 全銘柄: `?scope=all` と任意の `&side=...`。
  - レスポンスには `closed_count` とチケットごとの結果が含まれます。
- `POST /api/close_tickets` — 指定したチケット集合のみクローズ。
- `GET /api/positions`, `GET /api/positions/all`。
- `GET /api/stl`, `POST /api/stl/compute`, `POST /api/stl/prune`, `POST /api/stl/prune_all`, `DELETE /api/stl/run/{id}`。
- `GET /api/news`, `POST /api/news/backfill_forex`, `POST /api/news/analyze`。
- `GET /api/health/freshness`, `GET /api/tech/freshness`, `GET|POST /api/health/run`, `GET /api/health/runs`。
- `POST /api/preferences` と関連の設定取得。
- `GET /api/ai/trade_plan`。
- `GET /api/accounts`, `GET /api/account/current`, `POST /api/account/login`。
- `GET /ws/updates`。

## 🧪 例
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

## 🗄️ データベースとスキーマ
`sql/schema.sql` を参照してください。

要点:
- `ohlc_bars` の複合 PK `(symbol, timeframe, ts)` が重複バーを防止。
- 取り込みは `ON CONFLICT ... DO UPDATE` を使用。
- 追加テーブルで STL run/components、preferences、news articles、health runs、account series、closed deals、signal/order-plan linking をサポート。

## 🛡️ 取引制御と安全性
- 環境ガード: `TRADING_ENABLED=0`（デフォルト）では manual/plan execution エンドポイントからの注文発行を無効化。
- UI の `Auto` ヘッダー挙動は strategy チェックをスケジュールしますが、取引安全ゲートをバイパスしません。
- close 操作は、取引無効時でも意図的に許可されています。
- safe-max と symbol/kind weighting により、執行フロー内でエクスポージャを制限します。

## 📈 STL Auto-Compute トグル
- STL 自動計算は STL パネルの `Auto STL` スイッチで、symbol x timeframe ごとに制御されます。
- 大きい/重い文脈での UI 遅延を抑えるため、デフォルトは OFF。
- ON の場合は欠損/古い STL を自動計算でき、OFF の場合は手動再計算を使います。
- 状態は `/api/preferences` の `stl_auto_compute:SYMBOL:TF` などのキーと、起動高速化のための local storage に保存されます。

## 🧷 最後の選択状態を記憶
- サーバーは `last_symbol`, `last_tf`, `last_count` を保存し、テンプレートにデフォルト注入します。
- UI も `localStorage` に `last_symbol`/`last_tf` を保存します。
- `/?reset=1` を付けると、そのページ読み込みでは保存済み設定を無視します。
- `PIN_DEFAULTS_TO_XAU_H1=1` で起動デフォルトを強制できます。

## 🤖 AI Trade Plan プロンプト文脈
AI trade plan の要求時、サーバーは現在の symbol/timeframe に対して新しい Basic Health と Tech Snapshot run があることを保証し（なければ作成）、次の文脈からプロンプトを構築します。
- Basic health block,
- Tech AI block,
- Live technical snapshot block.

## 🧰 開発メモ
- 主な実行時依存: `tornado`, `asyncpg`, `MetaTrader5`, `numpy`, `python-dotenv`, `requests`, `httpx`, `statsmodels`, `openai`。
- 現状、正式な自動テストスイートは未構成。smoke test と手動 UI 検証が実運用フローです。
- 推奨 smoke tests:
  - `python scripts/test_mixed_ai.py`
  - `python scripts/test_fmp.py`
  - `python scripts/test_fmp_endpoints.py`
- push 前に行う手動確認:
  - pan/zoom 同期,
  - STL overlay/period line の挙動,
  - trading controls（close safety behavior を含む）, 
  - news panel のフォールバック挙動。

## 🧯 トラブルシューティング
| Symptom | Action |
|---|---|
| MT5 initialize failed | `MT5_PATH` を正確な `terminal64.exe` に設定し、まずは端末を手動で少なくとも一度起動 |
| MT5 login failed | `MT5_SERVER` が端末のサーバー文字列と完全一致するか確認。もしくは認証情報を省略してアクティブセッションを再利用 |
| No data for symbol | ブローカー側シンボル名と Market Watch 表示を確認（`XAUUSD`, `XAUUSD.a`, `GOLD` など） |
| Postgres connection issues | `DATABASE_URL` を確認し、`psql "$DATABASE_URL" -c 'select 1;'` を実行 |
| Slow or stale UI analytics | 重い pair/TF では auto STL を無効化し、必要時に手動再計算 |

## 🛣️ ロードマップ
- README ベースの多言語ドキュメントを超えて、`i18n/` の実行時アセットを拡張。
- 正式な自動テスト（API + integration + UI smoke automation）を追加。
- デプロイ用パッケージングと再現可能な環境プロファイルを改善。
- AI plan の検証と実行セーフガードを継続的に洗練。

## 🤝 コントリビュート
- パッチは小さくスコープを明確に。
- 必要に応じて明確なコミット接頭辞を使用（例: `UI: ...`, `Server: ...`, `References: ...`）。
- 関連のないフォーマット変更は避ける。
- UI 変更時は必要に応じてスクリーンショット/GIF を添付。
- PR 前に smoke tests とローカルブラウザ確認を実施。

## ❤️ Support / Sponsor
スポンサー/サポートリンクは `.github/FUNDING.yml` で設定されています。
- GitHub Sponsors: https://github.com/sponsors/lachlanchen
- Lazying.art: https://lazying.art
- Chat: https://chat.lazying.art
- OnlyIdeas: https://onlyideas.art

## 📚 参考資料
- `references/ai-trader-overview.md`
- `references/database_setup_postgres.md`
- `references/mt5_python_setup_ubuntu.md`
- `references/mt4_vs_mt5.md`
- `references/llm_trading_system.md`
- `references/release_deploy.md`
- `references/pnl_debugging.md`

## 📄 ライセンス
このリポジトリには 2026-02-28 時点で `LICENSE` ファイルが存在しません。

Assumption: ライセンス条件は現在リポジトリ内で未指定です。メンテナーが明示的なライセンスファイルを追加するまで、この注記を維持します。
