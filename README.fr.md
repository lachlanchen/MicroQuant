# MicroQuant by Lazying.art — Présentation

MicroQuant by Lazying.art est un prototype Micro Quant basé sur Tornado + Postgres. Il récupère les cours (par exemple l’or XAUUSD) depuis MetaTrader 5, les stocke dans PostgreSQL, puis expose une interface Chart.js afin de visualiser les plans de trading guidés par l’IA.

Le dossier `docs/` contient la page MicroQuant (`quant.lazying.art`), et `references/` héberge les notes sur les prompts, la configuration PostgreSQL et l’intégration MT5 + Python.

Après avoir configuré votre `.env` et la base de données, lancez `python -m app.server` pour naviguer dans l’interface localement.
