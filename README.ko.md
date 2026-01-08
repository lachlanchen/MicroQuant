<p>
  <b>언어:</b>
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

# MicroQuant by Lazying.art — 개요

MicroQuant by Lazying.art 는 Tornado + Postgres 기반의 Micro Quant 프로토타입입니다. MetaTrader 5 에서 금(XAUUSD) 등 시장 데이터를 가져와 PostgreSQL 에 저장하고, Chart.js 기반 UI 를 통해 AI 거래 계획을 관찰할 수 있습니다.

`docs/` 폴더는 MicroQuant 랜딩 페이지(`quant.lazying.art`)를 담고 있으며, `references/` 에는 문서, DB 설정, MT5+Python 통합 노트가 정리되어 있습니다.

`.env` 와 데이터베이스를 맞춘 뒤 `python -m app.server` 를 실행하면 로컬에서 인터페이스를 살펴볼 수 있습니다.
