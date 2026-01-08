<p>
  <b>Langues :</b>
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

# MicroQuant by Lazying.art — Présentation

MicroQuant by Lazying.art est un prototype Micro Quant basé sur Tornado + Postgres. Il récupère les cours (par exemple l’or XAUUSD) depuis MetaTrader 5, les stocke dans PostgreSQL, puis expose une interface Chart.js afin de visualiser les plans de trading guidés par l’IA.

Le dossier `docs/` contient la page MicroQuant (`quant.lazying.art`), et `references/` héberge les notes sur les prompts, la configuration PostgreSQL et l’intégration MT5 + Python.

Après avoir configuré votre `.env` et la base de données, lancez `python -m app.server` pour naviguer dans l’interface localement.
