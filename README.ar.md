<p>
  <b>اللغات:</b>
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

# MicroQuant by Lazying.art — نظرة عامة

MicroQuant by Lazying.art هو نموذج أولي Micro Quant مبني على Tornado + Postgres. يستخرج بيانات السوق (مثل الذهب) من MetaTrader 5 ويحفظها في PostgreSQL، ثم يعرض واجهة Chart.js تسمح بتتبع خطط التداول المدعومة بالذكاء الاصطناعي.

تحتوي مجلد `docs/` على صفحة الهبوط MicroQuant (`quant.lazying.art`)، بينما `references/` يجمع الملاحظات التقنية وشرح إعداد قواعد البيانات وتكامل MT5 + Python.

بعد إعداد `.env` وقاعدة البيانات، شغّل `python -m app.server` وسترى الواجهة محليًا.
