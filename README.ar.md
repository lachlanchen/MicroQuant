# MicroQuant by Lazying.art — نظرة عامة

MicroQuant by Lazying.art هو نموذج أولي Micro Quant مبني على Tornado + Postgres. يستخرج بيانات السوق (مثل الذهب) من MetaTrader 5 ويحفظها في PostgreSQL، ثم يعرض واجهة Chart.js تسمح بتتبع خطط التداول المدعومة بالذكاء الاصطناعي.

تحتوي مجلد `docs/` على صفحة الهبوط MicroQuant (`quant.lazying.art`)، بينما `references/` يجمع الملاحظات التقنية وشرح إعداد قواعد البيانات وتكامل MT5 + Python.

بعد إعداد `.env` وقاعدة البيانات، شغّل `python -m app.server` وسترى الواجهة محليًا.
