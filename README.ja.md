<p>
  <b>言語：</b>
  <a href="README.en.md">English</a>
  · <a href="README.zh-Hant.md">中文（繁體）</a>
  · <a href="README.zh-Hans.md">中文 (简体)</a>
  · <a href="README.ja.md">日本語</a>
  · <a href="README.ko.md">한국어</a>
  · <a href="README.vi.md">Tiếng Việt</a>
  · <a href="README.ar.md">العربية</a>
  · <a href="README.fr.md">Français</a>
  · <a href="README.es.md">Español</a>
</p>

# MicroQuant by Lazying.art — 概要

MicroQuant by Lazying.art は Tornado + Postgres を土台にした Micro Quant プロトタイプです。MetaTrader 5 から金（XAUUSD）などの市場データを取得し、PostgreSQL に保存したうえで、Chart.js ベースの UI で AI トレードプランの判断を支援します。

`docs/` フォルダーには MicroQuant のランディングページ（`quant.lazying.art`）があり、`references/` にはドキュメントや MT5 と Python の連携メモが並びます。

`.env` とデータベースを設定した後、`python -m app.server` でローカル画面にアクセスできます。
