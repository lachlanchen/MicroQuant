<p>
  <b>語言：</b>
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

# MicroQuant by Lazying.art — 概覽

MicroQuant by Lazying.art 是一套以 Tornado 與 Postgres 為核心的 Micro Quant 原型。它從 MetaTrader 5 擷取市場資料（例如黃金），寫入 PostgreSQL，並提供 Chart.js 驅動的介面，讓 AI 交易計畫在資料豐富的儀表板中操作。

`docs/` 目錄收藏了 MicroQuant 首頁（也即 `quant.lazying.art`），`references/` 則保留教學、資料庫與 MT5 + Python 整合筆記。

配置好 `.env` 與資料庫後，執行 `python -m app.server`，即可在本機探索這套量化介面。
