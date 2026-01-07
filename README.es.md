# MicroQuant by Lazying.art — Descripción

MicroQuant by Lazying.art es un prototipo Micro Quant sobre Tornado + Postgres. Toma datos de mercado (como oro XAUUSD) desde MetaTrader 5, los guarda en PostgreSQL y muestra una UI con Chart.js para seguir los planes de trading guiados por LLM.

La carpeta `docs/` aloja la landing de MicroQuant (`quant.lazying.art`), mientras que `references/` contiene notas sobre prompts, base de datos e integración MT5 + Python.

Después de preparar `.env` y la base de datos, ejecuta `python -m app.server` para ver la interfaz localmente.
