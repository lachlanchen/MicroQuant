# MicroQuant by Lazying.art — 概要

MicroQuant by Lazying.art は Tornado + Postgres を土台にした Micro Quant プロトタイプです。MetaTrader 5 から金（XAUUSD）などの市場データを取得し、PostgreSQL に保存したうえで、Chart.js ベースの UI で AI トレードプランの判断を支援します。

`docs/` フォルダーには MicroQuant のランディングページ（`quant.lazying.art`）があり、`references/` にはドキュメントや MT5 と Python の連携メモが並びます。

`.env` とデータベースを設定した後、`python -m app.server` でローカル画面にアクセスできます。
