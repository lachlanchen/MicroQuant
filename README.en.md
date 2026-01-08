<p>
  <b>Languages:</b>
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

# MicroQuant by Lazying.art — Overview

MicroQuant by Lazying.art is a Micro Quant philosophy wrapped around a Tornado + Postgres prototype. It fetches market data (XAUUSD, etc.) from MetaTrader 5, persists it into PostgreSQL, and exposes a Chart.js-powered UI so the AI trade plan stack can breathe through a data-rich signal console.

The `docs/` directory holds the MicroQuant landing page (`quant.lazying.art`), while `references/` stores supporting notes about trading prompts, DB setup, and MT5+Python integration.

Use `python -m app.server` after configuring the `.env` variables and Postgres schema to explore the Quant UI locally.
