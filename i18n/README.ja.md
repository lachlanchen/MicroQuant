[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# MetaTrader QT - 定量トレーディングスターター（Micro Quant Philosophy）

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Backend](https://img.shields.io/badge/Backend-Tornado-2d7cbf)
![Database](https://img.shields.io/badge/Database-PostgreSQL-336791?logo=postgresql&logoColor=white)
![Broker](https://img.shields.io/badge/Broker%20Bridge-MetaTrader5-1f6feb)
![UI](https://img.shields.io/badge/UI-Lightweight%20Charts%20%2B%20Chart.js-0ea5e9)
![Status](https://img.shields.io/badge/README-Expanded-success)
![GitHub%20Stars](https://img.shields.io/github/stars/lachlanchen/MicroQuant?style=for-the-badge&logo=github&logoColor=white&labelColor=0f172a&color=0ea5e9)
![GitHub%20Issues](https://img.shields.io/github/issues/lachlanchen/MicroQuant?style=for-the-badge&logo=github&logoColor=white&labelColor=0f172a&color=ef4444)

## 🎯 プロジェクトスナップショット

| フォーカス | スタック |
|---|---|
| 実行環境 | Tornado + asyncpg + WebSocket |
| 取引 | MetaTrader5 + レイヤー化されたAI/技術/ニュース文脈 |
| ストレージ | ON CONFLICT付きアップサートを備えたPostgreSQL |
| 配備 | PWAアセット + ブラウザ優先のデスクトップ/モバイルUI |

## 目次
- [📸 スクリーンショット](#-screenshot)
- [概要](#-overview)
- [中核思想](#-core-philosophy)
- [特徴](#-features)
- [プロジェクト構成](#-project-structure)
- [前提条件](#-prerequisites)
- [インストール](#-installation)
- [設定](#️-configuration)
- [使用方法](#-usage)
- [APIエンドポイント（実践）](#-api-endpoints-practical)
- [例](#-examples)
- [データベースとスキーマ](#-database--schema)
- [トレード制御と安全性](#️-trading-controls--safety)
- [STL自動計算トグル](#-stl-auto-compute-toggle)
- [最終選択の保持](#-remembering-last-selection)
- [AIトレードプランのプロンプト文脈](#️-ai-trade-plan-prompt-context)
- [開発メモ](#-development-notes)
- [トラブルシューティング](#-troubleshooting)
- [ロードマップ](#-roadmap)
- [貢献](#-contributing)
- [参考情報](#-references)
- [サポート](#️-support)
- [ライセンス](#-license)

## 📸 スクリーンショット
![Micro Quant UI](figures/demos/micro-quant-ui.png)

[![DATA Source](https://img.shields.io/badge/Data_Source-RoboForex-0060ff?style=for-the-badge&labelColor=0a4eb3)](https://my.roboforex.com/en/?a=efx)

## 🧭 概要
Micro Quantは、派手なダッシュボードよりも再現性の高い取引ロジックスタックを重視します。MetaTrader 5からOHLCデータを取得し、PostgreSQLへ永続化し、レイヤー化されたAI支援シグナル（Basicニュース、テクニカルスナップショット、取引プラン、STLオーバーレイ）を用いて体系的な意思決定を評価します。UIには、整列トグル、根拠付きクローズ、保存された設定、データ豊富な実行パネルを備え、サーバーが定期実行またはモーダル実行フローを安全に回しつつ、ログと根拠を確認できるよう設計されています。

静的ランディングページ（Quant by Lazying.art）は `docs/` 配下にあり、GitHub Pages (`trade.lazying.art` via `docs/CNAME`) で公開されています。リポジトリには、AIトレードプランのプロンプト、統合メモ、運用ドキュメントも含まれます。

### 一覧
| 領域 | 役割 |
|---|---|
| データ | MT5 OHLCを取得しPostgreSQLへupsert |
| 分析 | ヘルス/ニュース/テクニカルおよびSTLワークフローを実行 |
| 判断 | レイヤー化された文脈からAIトレードプランを構築 |
| 実行 | 安全ガード付きで取引フローを実行・制御 |
| UI | チャートワークフローを同期したデスクトップ/モバイル表示 |

## 🧠 中核思想
- **真実の連鎖**: Basicニュースチェック（テキスト＋スコア）とテクニカルスナップショット（豊富なテクニカル文脈＋STL）で、シンボル・時間足ごとに単一のAIトレードプランを生成します。定期自動実行と手動モーダル実行は同じパイプラインと根拠ログを共有します。
- **整合優先実行**: Accept-Tech/Hold-Neutralトグル、ignore-basicsスイッチ、部分クローズラッパーにより、技術シグナルを意図的に遵守し、必要時に逆方向のポジションを先にクローズし、新規エントリー時の不要なクローズを最小化します。
- **不変データ**: すべての取得結果は`ON CONFLICT`による整合性を保ってPostgresへ書き込みます。UI向けの`/api/data`はサニタイズ済み系列を返します。設定（`auto`設定、`close_fraction`、テック非表示トグル、STL自動計算）は`/api/preferences`で永続化されます。
- **安全第一の取引**: `TRADING_ENABLED`と`safe_max`が手動・自動の権限を制御します。`/api/close`や定期ランナーは終了理由（テック中立、整合不一致など）をログ化し、追跡性を担保します。

## ✨ 特徴
- MT5 OHLCのPostgres取り込み（`/api/fetch`、`/api/fetch_bulk`）。
- `/`（デスクトップ）と`/app`（モバイル）のチャートUI。テンプレート内でChart.js + Lightweight Chartsを使用。
- STL分解ワークフロー（`/api/stl`、`/api/stl/compute`、prune/delete エンドポイント）。
- ニュース取り込みと分析（`/api/news`、`/api/news/backfill_forex`、`/api/news/analyze`）。
- AIワークフロー統制（`/api/health/run`、`/api/health/runs`、`/api/ai/trade_plan`）。
- 手動取引実行（`/api/trade`、`/api/trade/execute_plan`）。`TRADING_ENABLED`でガードされます。
- ポジションリスク操作（`/api/positions*`、`/api/close`、`/api/close_tickets`）は明示的な安全挙動下でクローズを許可。
- WebSocket更新ストリーム（`/ws/updates`）でリアルタイムヒントと更新シグナルを配信。
- インストール可能なダッシュボード向けPWA/静的アセット。

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
├── i18n/                        # Translated docs (currently language only)
├── .github/FUNDING.yml          # Sponsor/support metadata
└── README.md + README.*.md      # Canonical + multilingual docs
```

## ✅ 前提条件
- Ubuntu/Linuxまたはターミナルアクセス可能なWindows。
- MetaTrader 5がインストール済み（`terminal64.exe`）で必要ならログイン済み。
- Python 3.10+（MetaTrader5のホイール互換性のためPython 3.11推奨）。
- アプリサーバーからアクセス可能なPostgreSQLインスタンス。
- ニュース提供者向けAPIキー（任意）:
  - FMP
  - Alpha Vantage

## 🛠️ インストール

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

ヘルパースクリプト:
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

## ⚙️ 設定
`.env.example` を `.env` にコピーして値を調整します。

### 主要変数
| 変数 | 用途 |
|---|---|
| `DATABASE_URL` | 推奨PostgreSQL DSN |
| `DATABASE_MT_URL` | `DATABASE_URL`未設定時の代替DSN |
| `DATABASE_QT_URL` | 二次代替DSN |
| `MT5_PATH` | `terminal64.exe` のパス（Wineまたはネイティブ） |
| `MT5_LOGIN` / `MT5_PASSWORD` / `MT5_SERVER` | MT5セッションが既にログイン済みの場合は任意 |
| `PORT` | サーバーポート（デフォルト `8888`） |

### 任意変数
- ニュース拡張用: `FMP_API_KEY`、`ALPHAVANTAGE_API_KEY`
- `TRADING_ENABLED`（デフォルト`0`、注文実行を許可するには`1`に設定）
- `TRADING_VOLUME`（手動時の既定ロット）
- `AUTO_FETCH`、`AUTO_FETCH_SYMBOL`、`AUTO_FETCH_TF`、`AUTO_FETCH_COUNT`、`AUTO_FETCH_SEC`
- `PIN_DEFAULTS_TO_XAU_H1=1` でUI起動時の初期シンボル/時間足を固定
- `LOG_LEVEL`、`LOG_BACKFILL`、および`/api/preferences`経由または環境変数によるアカウント/ポーリング関連設定

補足:
- `MT5_PATH` は、MT5インストールスクリプトで使用するWineプレフィックス内の正確な `terminal64.exe` を指す必要があります。
- 既に有効なターミナルセッションがある場合、MT5認証情報を省略できます。アプリはそのセッションを再利用しようとします。

## 🚀 使用方法

### サーバー起動
```bash
python -m app.server
```

### UIを開く
- デスクトップUI: `http://localhost:8888/`
- モバイルUI: `http://localhost:8888/app`

### 主要URL
| 利用箇所 | URL | 用途 |
|---|---|---|
| Desktop | `http://localhost:8888/` | ローソク足チャートとデスクトップ向けワークフロー |
| Mobile | `http://localhost:8888/app` | コンパクトなタッチ操作向けレイアウト |
| APIヘルス | `http://localhost:8888/api/health/freshness` | データとサービス準備状態の簡易チェック |

### 一般的な手順
1. MT5からバーを取得してPostgresへ永続化
2. DBからバーを読み取り、チャート描画
3. ヘルス／テクニカル／ニュース分析を実行
4. AIトレードプランを生成
5. 安全ガード下でエグゼキューションまたはクローズを実施

## 🔌 APIエンドポイント（実践）
- `GET /api/fetch?symbol=XAUUSD&tf=H1&count=500[&mode=inc|full][&persist=1]`
  - MT5から取得し、DBへupsert
  - `persist=1` の場合、サーバーは`last_symbol`/`last_tf`/`last_count`を既定値として保存します。バルク/定期取得ではUI設定を上書きしないようこの値は送信しないでください。
- `GET /api/fetch_bulk` — バルク/定期取り込み。
- `GET /api/data?symbol=XAUUSD&tf=H1&limit=500` — DBからチャートデータを取得。
- `GET /api/strategy/run?symbol=XAUUSD&tf=H1&fast=20&slow=50`
  - SMA(20/50)クロスを実行し、シグナルペイロードを返します。
  - 重要: このエンドポイントでの戦略駆動注文配置は現在サーバー側で無効化されており、実際の注文実行はトレード系エンドポイントで行います。
- `POST /api/trade` — UIからの手動Buy/Sell。`TRADING_ENABLED`でガード。
- `POST /api/trade/execute_plan` — 生成済みプランを実行。事前クローズとストップ距離チェックを含む。
- `POST /api/close` — 全ポジションクローズ（`TRADING_ENABLED=0`時でも安全上許可）:
  - 現在シンボル: リクエスト本文 `symbol=...`、`side=long|short|both` は任意。
  - 全シンボル: `?scope=all` と任意の`&side=...`。
  - レスポンスには`closed_count`とチケット単位の結果が含まれます。
- `POST /api/close_tickets` — 指定チケットを一部クローズ。
- `GET /api/positions`、`GET /api/positions/all`
- `GET /api/stl`、`POST /api/stl/compute`、`POST /api/stl/prune`、`POST /api/stl/prune_all`、`DELETE /api/stl/run/{id}`
- `GET /api/news`、`POST /api/news/backfill_forex`、`POST /api/news/analyze`
- `GET /api/health/freshness`、`GET /api/tech/freshness`、`GET|POST /api/health/run`、`GET /api/health/runs`
- `POST /api/preferences` および関連する設定取得
- `GET /api/ai/trade_plan`
- `GET /api/accounts`、`GET /api/account/current`、`POST /api/account/login`
- `GET /ws/updates`

## 🧪 例
```bash
# XAUUSDのH1バーを500本取得
curl "http://localhost:8888/api/fetch?symbol=XAUUSD&tf=H1&count=500"

# DBから200本のバーを取得
curl "http://localhost:8888/api/data?symbol=XAUUSD&tf=H1&limit=200"

# SMAシグナル計算を実行
curl "http://localhost:8888/api/strategy/run?symbol=XAUUSD&tf=H1&fast=20&slow=50"

# 現在シンボルのロングポジションをクローズ
curl -X POST "http://localhost:8888/api/close" -d "symbol=XAUUSD&side=long"

# 全シンボルのショートポジションをクローズ
curl -X POST "http://localhost:8888/api/close?scope=all&side=short"
```

## 🗄️ データベースとスキーマ
`sql/schema.sql`を参照してください。

要点:
- `ohlc_bars` の複合主キー `(symbol, timeframe, ts)` により重複バーを防止します。
- 取り込みは `ON CONFLICT ... DO UPDATE` を使用します。
- STL実行/構成要素、設定、ニュース記事、ヘルス実行、アカウント履歴、クローズ済み取引、シグナルと注文プランの紐付けをサポートする追加テーブルがあります。

## 🛡️ トレード制御と安全性
- 環境ガード: `TRADING_ENABLED=0`（デフォルト）では、手動・プラン実行エンドポイントの注文送信を無効化。
- UIヘッダーの`Auto`は戦略チェックを定期実行しますが、取引の安全ゲートを迂回しません。
- トレーディングが無効でも、クローズ操作は意図的に許可。
- Safe-maxとシンボル/種別のウェイトが実行フローでエクスポージャーを抑えるために使われます。

## 📈 STL自動計算トグル
- STLの自動計算は、STLパネルの`Auto STL`スイッチでシンボル×時間足ごとに制御されます。
- 既定はOFFで、データ量が多い/処理が重い場合のUI遅延を抑えます。
- ON時は欠損または古いSTLを自動計算し、OFF時は手動再計算コントロールを使用。
- 状態は`/api/preferences`のキー（`stl_auto_compute:SYMBOL:TF`）および高速起動用のローカルストレージで永続化されます。

## 🧷 最後の選択の記憶
- サーバーは`last_symbol`、`last_tf`、`last_count`を保存し、テンプレートへ既定値を注入します。
- UI側も`localStorage`に`last_symbol`/`last_tf`を保存します。
- `/?reset=1` はそのページロード時に保存設定を無視します。
- `PIN_DEFAULTS_TO_XAU_H1=1` を使うと起動時の既定値を固定できます。

## 🤖 AIトレードプランのプロンプト文脈
AIトレードプランを要求すると、サーバーは現在のシンボル/時間足で最新のBasic HealthとTech Snapshot実行結果を確認し（不足時は生成）、以下を使ってプロンプト文脈を作成します。
- Basic healthブロック
- Tech AIブロック
- リアルタイムの技術スナップショットブロック

## 🧰 開発メモ
- 主要ランタイム依存: `tornado`、`asyncpg`、`MetaTrader5`、`numpy`、`python-dotenv`、`requests`、`httpx`、`statsmodels`、`openai`
- 現在、正式な自動テストスイートは構成されていません。スモークテストと手動UI検証が運用フローです。
- 推奨スモークテスト:
  - `python scripts/test_mixed_ai.py`
  - `python scripts/test_fmp.py`
  - `python scripts/test_fmp_endpoints.py`
- リリース前の手動確認:
  - pan/zoom同期
  - STLオーバーレイ/周期線の挙動
  - 取引操作（クローズの安全動作を含む）
  - ニュースパネルのフォールバック

## 🧯 トラブルシューティング
| 症状 | 対処 |
|---|---|
| MT5の初期化に失敗 | `MT5_PATH`を正確な`terminal64.exe`に設定し、少なくとも一度手動で端末を起動 |
| MT5ログインに失敗 | `MT5_SERVER` が端末のサーバー文字列と完全一致するか確認。あるいは認証情報を省略し有効なセッションを再利用 |
| シンボルにデータがない | ブローカー側シンボル命名とMarket Watch表示状態を確認（`XAUUSD`、`XAUUSD.a`、`GOLD`など） |
| Postgres接続の問題 | `DATABASE_URL`を確認し、`psql "$DATABASE_URL" -c 'select 1;'` |
| UIの分析が遅い/古い | 重い通貨ペアやTFでAuto STLを無効化し、手動再計算を実行 |

## 🛣️ ロードマップ
- `i18n/` 実行時資産をREADMEベースの多言語ドキュメントから拡張。
- 本格的な自動テストを追加（API + 統合 + UIスモーク自動化）。
- デプロイ構成と再現性の高い環境プロファイルを改善。
- AIプラン検証と実行セーフガードを継続改善。

## 🤝 貢献
- 変更は小さくスコープを限定する。
- 必要であれば明確なコミット接頭辞を使用（例: `UI: ...`、`Server: ...`、`References: ...`）。
- 無関係なフォーマット変更を避ける。
- UI変更時は必要に応じてスクリーンショット/GIFを添付。
- PR前にスモークテストとローカルブラウザ検証を実施。

## 📚 参考情報
- `references/ai-trader-overview.md`
- `references/database_setup_postgres.md`
- `references/mt5_python_setup_ubuntu.md`
- `references/mt4_vs_mt5.md`
- `references/llm_trading_system.md`
- `references/release_deploy.md`
- `references/pnl_debugging.md`

## 📄 ライセンス
このリポジトリには2026-02-28時点で`LICENSE`ファイルはありません。

ライセンス条件は現時点では本リポジトリ内で未定義のため、明示的なライセンスファイルが追加されるまでこの注記を保持してください。


## ❤️ Support

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://camo.githubusercontent.com/24a4914f0b42c6f435f9e101621f1e52535b02c225764b2f6cc99416926004b7/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f446f6e6174652d4c617a79696e674172742d3045413545393f7374796c653d666f722d7468652d6261646765266c6f676f3d6b6f2d6669266c6f676f436f6c6f723d7768697465)](https://chat.lazying.art/donate) | [![PayPal](https://camo.githubusercontent.com/d0f57e8b016517a4b06961b24d0ca87d62fdba16e18bbdb6aba28e978dc0ea21/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f50617950616c2d526f6e677a686f754368656e2d3030343537433f7374796c653d666f722d7468652d6261646765266c6f676f3d70617970616c266c6f676f436f6c6f723d7768697465)](https://paypal.me/RongzhouChen) | [![Stripe](https://camo.githubusercontent.com/1152dfe04b6943afe3a8d2953676749603fb9f95e24088c92c97a01a897b4942/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f5374726970652d446f6e6174652d3633354246463f7374796c653d666f722d7468652d6261646765266c6f676f3d737472697065266c6f676f436f6c6f723d7768697465)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |
