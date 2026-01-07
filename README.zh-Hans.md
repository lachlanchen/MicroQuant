# MicroQuant by Lazying.art — 概览

MicroQuant by Lazying.art 是一套基于 Tornado 和 Postgres 的 Micro Quant 原型。它从 MetaTrader 5 获取市场数据（例如黄金），写入 PostgreSQL，并提供 Chart.js 驱动的界面，让 AI 交易计划在数据丰富的仪表板中运行。

`docs/` 目录保存 MicroQuant 登陆页（即 `quant.lazying.art`），`references/` 则存放教学、数据库以及 MT5 + Python 集成笔记。

配置好 `.env` 与数据库后，运行 `python -m app.server`，即可在本地查看这一量化界面。
