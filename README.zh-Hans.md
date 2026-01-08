<p>
  <b>语言：</b>
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

# MicroQuant by Lazying.art — 概览

MicroQuant by Lazying.art 是一套基于 Tornado 和 Postgres 的 Micro Quant 原型。它从 MetaTrader 5 获取市场数据（例如黄金），写入 PostgreSQL，并提供 Chart.js 驱动的界面，让 AI 交易计划在数据丰富的仪表板中运行。

`docs/` 目录保存 MicroQuant 登陆页（即 `quant.lazying.art`），`references/` 则存放教学、数据库以及 MT5 + Python 集成笔记。

配置好 `.env` 与数据库后，运行 `python -m app.server`，即可在本地查看这一量化界面。
