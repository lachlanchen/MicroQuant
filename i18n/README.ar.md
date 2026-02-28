[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


<p align="center">
  <img src="https://raw.githubusercontent.com/lachlanchen/lachlanchen/main/logos/banner.png" alt="LazyingArt banner" />
</p>

# MetaTrader QT - بداية للتداول الكمي (فلسفة Micro Quant)

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Backend](https://img.shields.io/badge/Backend-Tornado-2d7cbf)
![Database](https://img.shields.io/badge/Database-PostgreSQL-336791?logo=postgresql&logoColor=white)
![Broker](https://img.shields.io/badge/Broker%20Bridge-MetaTrader5-1f6feb)
![UI](https://img.shields.io/badge/UI-Lightweight%20Charts%20%2B%20Chart.js-0ea5e9)
![Status](https://img.shields.io/badge/README-Expanded-success)

## 📸 لقطة شاشة
![Micro Quant UI](figures/demos/micro-quant-ui.png)

<p align="center">
  <a href="https://my.roboforex.com/en/?a=efx" target="_blank" rel="noopener noreferrer">
    <button style="padding: 0.65rem 1.25rem; font-weight: 600; border-radius: 999px; border: none; color: white; background: #0060ff; cursor: pointer;">
      DATA Source
    </button>
  </a>
</p>

## 🧭 نظرة عامة
فلسفة Micro Quant أقل ارتباطًا بالواجهات اللامعة وأكثر تركيزًا على منطق تداول قابل للتكرار: يجلب بيانات OHLC من MetaTrader 5، ويحفظها في Postgres، ثم يقيّم قرارات منهجية عبر إشارات متعددة الطبقات موجّهة بالذكاء الاصطناعي (أخبار أساسية، لقطة تقنية، خطط تداول، وتراكبات STL). تعكس الواجهة هذه الفلسفة عبر مفاتيح التوافق، وأسباب الإغلاق المبررة، وتفضيلات محفوظة، ولوحة تنفيذ غنية بالبيانات بحيث يمكن للخادم تشغيل تدفقات تداول دورية أو يدوية مع إمكانية فحص السجلات والأدلة.

الصفحة الثابتة (Quant by Lazying.art) موجودة تحت `docs/` ويتم نشرها عبر GitHub Pages (`trade.lazying.art` من خلال `docs/CNAME`). يتضمن المستودع أيضًا مراجع لطلبات AI Trade Plan، وملاحظات التكامل، ووثائق تشغيلية.

### لمحة سريعة
| المجال | ما الذي يفعله |
|---|---|
| البيانات | يجلب OHLC من MT5 ويحدّثها في PostgreSQL |
| التحليلات | يشغّل مسارات health/news/tech و STL |
| اتخاذ القرار | ينشئ خطط تداول AI من سياق متعدد الطبقات |
| التنفيذ | ينفّذ/يتحكم بتدفقات التداول خلف حواجز أمان |
| الواجهة | عروض سطح مكتب/موبايل مع مزامنة سير عمل الرسوم البيانية |

## 🧠 الفلسفة الأساسية
- **سلسلة الحقيقة**: فحوصات الأخبار الأساسية (نص + درجات) ولقطات Tech (سياق تقني كثيف + STL) تغذي خطة تداول AI واحدة لكل رمز/إطار زمني. التشغيل الدوري التلقائي والتشغيل اليدوي عبر النافذة يستخدمان نفس خط المعالجة وسجلات التبرير.
- **تنفيذ قائم على التوافق أولًا**: مفاتيح Accept-Tech/Hold-Neutral، ومفتاح ignore-basics، وطبقات partial-close تضمن اتباع Tech بشكل مقصود، وإغلاق المراكز المعاكسة قبل فتح مراكز جديدة عند الحاجة، وتقليل الخروج غير الضروري.
- **بيانات غير قابلة للتلف**: كل عملية جلب تُكتب إلى Postgres مع قواعد `ON CONFLICT`، بينما `/api/data` يقرأ سلاسل منقّاة للواجهة. التفضيلات (أحجام auto، و`close_fraction`، ومفاتيح إخفاء tech، وSTL auto-compute) تُحفظ عبر `/api/preferences`.
- **تداول قائم على الأمان أولًا**: `TRADING_ENABLED` و`safe_max` يفرضان صلاحيات التداول اليدوي/التلقائي. يمكن لـ`/api/close` والمشغلات الدورية تسجيل أسباب الإغلاق (tech neutral، عدم التوافق، إلخ) لأغراض التتبع.

## ✨ الميزات
- إدخال OHLC من MT5 إلى Postgres (`/api/fetch`, `/api/fetch_bulk`).
- واجهة الرسوم عند `/` (سطح المكتب) و`/app` (الموبايل)، باستخدام Chart.js + Lightweight Charts في القوالب.
- مسارات تحليل STL (`/api/stl`, `/api/stl/compute`, ونقاط نهاية prune/delete).
- جلب الأخبار وتحليلها (`/api/news`, `/api/news/backfill_forex`, `/api/news/analyze`).
- تنسيق مسارات الذكاء الاصطناعي (`/api/health/run`, `/api/health/runs`, `/api/ai/trade_plan`).
- تنفيذ تداول يدوي (`/api/trade`, `/api/trade/execute_plan`) محمي عبر `TRADING_ENABLED`.
- عمليات مخاطر المراكز (`/api/positions*`, `/api/close`, `/api/close_tickets`) مع السماح بعمليات الإغلاق للأمان.
- تدفق تحديثات WebSocket عند `/ws/updates`.

## 🗂️ هيكل المشروع
```text
metatrader_qt/
├── app/
│   ├── server.py                # Tornado app, routes, orchestration
│   ├── db.py                    # asyncpg access layer + schema init
│   ├── mt5_client.py            # MetaTrader5 bridge + order/data operations
│   ├── news_fetcher.py          # FMP/AlphaVantage aggregation/filtering
│   └── strategy.py              # SMA crossover helper
├── templates/
│   ├── index.html               # Main desktop UI
│   └── mobile.html              # Mobile-oriented UI
├── static/                      # PWA assets (icons/manifest/service worker)
├── sql/
│   └── schema.sql               # Core DB schema
├── scripts/
│   ├── test_mixed_ai.py         # Mixed AI smoke test
│   ├── test_fmp.py              # FMP smoke test
│   ├── test_fmp_endpoints.py    # FMP endpoint probe script
│   ├── setup_windows.ps1        # Windows env bootstrap
│   ├── run_windows.ps1          # Windows run helper
│   └── bootstrap_venv311.sh     # Linux/mac Python 3.11 helper
├── docs/                        # GitHub Pages landing site
├── references/                  # Operational/setup notes
├── strategies/llm/              # Prompt/config JSON files
├── llm_model/echomind/          # LLM provider wrappers
├── i18n/                        # Present (currently empty)
├── .github/FUNDING.yml          # Sponsor/support metadata
└── README.md + README.*.md      # Canonical + multilingual docs
```

## ✅ المتطلبات المسبقة
- Ubuntu/Linux أو Windows.
- تثبيت MT5 وإمكانية الوصول إليه (`terminal64.exe`) مع تشغيل الطرفية وتسجيل الدخول.
- Python 3.10+ (ويُفضّل 3.11 لتوافق MetaTrader5).
- مثيل PostgreSQL.

## 🛠️ التثبيت

### Windows (PowerShell)
```powershell
# 1) Create venv with Python 3.11 (MetaTrader5 has no wheels for 3.13 yet)
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt

# 2) Configure env
Copy-Item .env.example .env
# Edit .env and set DATABASE_URL, MT5_PATH (e.g. C:\Program Files\MetaTrader 5\terminal64.exe), and your MT5 demo creds
# Load env for this session
Get-Content .env | Where-Object { $_ -and $_ -notmatch '^#' } | ForEach-Object { $n,$v = $_ -split '=',2; [Environment]::SetEnvironmentVariable($n, $v, 'Process') }

# 3) Run app
python -m app.server
# Open http://localhost:8888
```

Helper scripts:
```powershell
scripts\setup_windows.ps1
scripts\run_windows.ps1
```

### Linux/macOS (bash)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Alternative: local 3.11 venv (if your global/Conda Python is 3.13)
# Requires python3.11 on your system
# sudo apt install python3.11 python3.11-venv
bash scripts/bootstrap_venv311.sh
source .venv311/bin/activate

# DB (use your own user/password as needed)
# createdb -h localhost -p 5432 -U lachlan metatrader_db

# Configure env
cp .env.example .env
# edit .env with your MT5 path and credentials
set -a; source .env; set +a

# Run app
python -m app.server
# Open http://localhost:8888
```

## ⚙️ الإعداد
انسخ `.env.example` إلى `.env` ثم عدّل القيم.

### المتغيرات الأساسية
| Variable | Purpose |
|---|---|
| `DATABASE_URL` | Preferred PostgreSQL DSN |
| `DATABASE_MT_URL` | Fallback DSN if `DATABASE_URL` unset |
| `DATABASE_QT_URL` | Secondary fallback DSN |
| `MT5_PATH` | Path to `terminal64.exe` (Wine or native) |
| `MT5_LOGIN` / `MT5_PASSWORD` / `MT5_SERVER` | Optional if MT5 terminal session is already logged in |
| `PORT` | Server port (default `8888`) |

### متغيرات اختيارية
- `FMP_API_KEY`, `ALPHAVANTAGE_API_KEY` لإثراء الأخبار.
- `TRADING_ENABLED` (الافتراضي `0`، اضبطه على `1` للسماح بنقاط نهاية تنفيذ الأوامر).
- `TRADING_VOLUME` (حجم التداول اليدوي الافتراضي).
- `AUTO_FETCH`, `AUTO_FETCH_SYMBOL`, `AUTO_FETCH_TF`, `AUTO_FETCH_COUNT`, `AUTO_FETCH_SEC`.
- `PIN_DEFAULTS_TO_XAU_H1=1` لفرض رمز/إطار زمني افتراضي عند بدء الواجهة.
- `LOG_LEVEL`, `LOG_BACKFILL`، إضافة إلى تفضيلات الحساب/الاستطلاع عبر `/api/preferences` والبيئة.

ملاحظات:
- يجب أن يشير `MT5_PATH` إلى `terminal64.exe` ضمن Wine prefix المستخدم في سكربت تثبيت MT5.
- يمكنك حذف بيانات اعتماد MT5 إذا كانت جلسة الطرفية مسجّل دخولها مسبقًا؛ سيحاول التطبيق إعادة استخدام تلك الجلسة.

## 🚀 الاستخدام

### تشغيل الخادم
```bash
python -m app.server
```

### فتح الواجهة
- واجهة سطح المكتب: `http://localhost:8888/`
- واجهة الموبايل: `http://localhost:8888/app`

### سير العمل الشائع
1. جلب الشموع من MT5 وحفظها في Postgres.
2. قراءة الشموع من قاعدة البيانات للعرض البياني.
3. تشغيل تحليلات health/tech/news.
4. توليد AI trade plan.
5. تنفيذ المراكز أو إغلاقها ضمن حواجز الأمان.

## 🔌 نقاط API (عمليًا)
- `GET /api/fetch?symbol=XAUUSD&tf=H1&count=500[&mode=inc|full][&persist=1]`
  - جلب البيانات من MT5 وupsert إلى DB.
  - عند `persist=1`، يحفظ الخادم الإعدادات الافتراضية `last_symbol/last_tf/last_count`؛ يجب أن تتجنب عمليات الجلب المجمعة/الخلفية هذا الخيار حتى لا تستبدل اختيارات الواجهة.
- `GET /api/fetch_bulk` — إدخال مجمّع/مجدول.
- `GET /api/data?symbol=XAUUSD&tf=H1&limit=500` — قراءة بيانات الرسم من DB.
- `GET /api/strategy/run?symbol=XAUUSD&tf=H1&fast=20&slow=50`
  - يشغّل SMA(20/50) crossover ويُعيد signal payload.
  - ملاحظة تنفيذية مهمة: تنفيذ الأوامر من هذه النقطة الطرفية المعتمدة على الاستراتيجية مُعطّل حاليًا في كود الخادم؛ تنفيذ الأوامر يتم عبر نقاط trade.
- `POST /api/trade` — Buy/Sell يدوي من الواجهة، محكوم بـ `TRADING_ENABLED`.
- `POST /api/trade/execute_plan` — ينفّذ خطة مولّدة، ويتضمن فحوصات pre-close وstop-distance.
- `POST /api/close` — إغلاق المراكز (مسموح حتى عند `TRADING_ENABLED=0` للأمان):
  - الرمز الحالي: form body بصيغة `symbol=...`؛ اختياري `side=long|short|both`.
  - كل الرموز: `?scope=all` مع اختياري `&side=...`.
  - الاستجابة تتضمن `closed_count` ونتائج كل ticket.
- `POST /api/close_tickets` — إغلاق مجموعة محددة حسب ticket.
- `GET /api/positions`, `GET /api/positions/all`.
- `GET /api/stl`, `POST /api/stl/compute`, `POST /api/stl/prune`, `POST /api/stl/prune_all`, `DELETE /api/stl/run/{id}`.
- `GET /api/news`, `POST /api/news/backfill_forex`, `POST /api/news/analyze`.
- `GET /api/health/freshness`, `GET /api/tech/freshness`, `GET|POST /api/health/run`, `GET /api/health/runs`.
- `POST /api/preferences` واسترجاع التفضيلات ذات الصلة.
- `GET /api/ai/trade_plan`.
- `GET /api/accounts`, `GET /api/account/current`, `POST /api/account/login`.
- `GET /ws/updates`.

## 🧪 أمثلة
```bash
# Fetch 500 H1 bars for XAUUSD
curl "http://localhost:8888/api/fetch?symbol=XAUUSD&tf=H1&count=500"

# Read 200 bars from DB
curl "http://localhost:8888/api/data?symbol=XAUUSD&tf=H1&limit=200"

# Run SMA signal calculation
curl "http://localhost:8888/api/strategy/run?symbol=XAUUSD&tf=H1&fast=20&slow=50"

# Close current symbol long positions
curl -X POST "http://localhost:8888/api/close" -d "symbol=XAUUSD&side=long"

# Close all short positions across symbols
curl -X POST "http://localhost:8888/api/close?scope=all&side=short"
```

## 🗄️ قاعدة البيانات والمخطط
راجع `sql/schema.sql`.

أبرز النقاط:
- المفتاح الأساسي المركب `(symbol, timeframe, ts)` في `ohlc_bars` يمنع تكرار الشموع.
- الإدخال يستخدم `ON CONFLICT ... DO UPDATE`.
- جداول إضافية تدعم تشغيلات/مكوّنات STL، والتفضيلات، ومقالات الأخبار، وتشغيلات health، وسلاسل الحسابات، والصفقات المغلقة، وربط الإشارات بخطط/أوامر التداول.

## 🛡️ ضوابط التداول والأمان
- حماية بيئية: `TRADING_ENABLED=0` افتراضيًا يعطّل وضع الأوامر عبر نقاط التنفيذ اليدوي/الخطة.
- سلوك رأس `Auto` في الواجهة يجدول فحوصات الاستراتيجية؛ لكنه لا يتجاوز بوابات أمان التداول.
- عمليات الإغلاق مسموحة عمدًا حتى عند تعطيل التداول.
- يتم استخدام safe-max وأوزان الرمز/النوع ضمن تدفقات التنفيذ للحد من الانكشاف.

## 📈 مفتاح STL Auto-Compute
- يتم التحكم في STL auto-compute لكل symbol x timeframe عبر مفتاح `Auto STL` في لوحة STL.
- الافتراضي هو OFF لتقليل بطء الواجهة في السياقات الكبيرة/البطيئة.
- عند ON، يمكن حساب STL تلقائيًا إذا كان مفقودًا/قديمًا؛ وإلا استخدم أدوات إعادة الحساب اليدوية.
- الحالة تُحفَظ عبر مفاتيح `/api/preferences` مثل `stl_auto_compute:SYMBOL:TF` وكذلك في local storage لتسريع الإقلاع.

## 🧷 تذكر آخر اختيار
- الخادم يحفظ `last_symbol`, `last_tf`, `last_count` ويحقن القيم الافتراضية في القوالب.
- الواجهة تخزّن أيضًا `last_symbol`/`last_tf` في `localStorage`.
- `/?reset=1` يتجاهل التفضيلات المحفوظة لهذه الحمولة فقط.
- يمكن لـ `PIN_DEFAULTS_TO_XAU_H1=1` فرض إعدادات بدء التشغيل.

## 🤖 سياق AI Trade Plan Prompt
عند طلب AI trade plan، يتأكد الخادم من وجود تشغيلات حديثة لـ Basic Health وTech Snapshot للرمز/الإطار الحالي (ويُنشئها إذا كانت مفقودة)، ثم يبني سياق الطلب من:
- Basic health block,
- Tech AI block,
- Live technical snapshot block.

## 🧰 ملاحظات التطوير
- اعتماديات التشغيل الأساسية: `tornado`, `asyncpg`, `MetaTrader5`, `numpy`, `python-dotenv`, `requests`, `httpx`, `statsmodels`, `openai`.
- لا توجد حاليًا مجموعة اختبارات آلية رسمية؛ يعتمد سير العمل على اختبارات smoke والتحقق اليدوي من الواجهة.
- اختبارات smoke الموصى بها:
  - `python scripts/test_mixed_ai.py`
  - `python scripts/test_fmp.py`
  - `python scripts/test_fmp_endpoints.py`
- فحوصات يدوية قبل الرفع:
  - مزامنة pan/zoom،
  - سلوك STL overlay/period lines،
  - ضوابط التداول (بما فيها سلوك أمان الإغلاق)،
  - سلوك fallback في لوحة الأخبار.

## 🧯 استكشاف الأخطاء وإصلاحها
| Symptom | Action |
|---|---|
| MT5 initialize failed | Set `MT5_PATH` to exact `terminal64.exe`, then run terminal manually at least once |
| MT5 login failed | Ensure `MT5_SERVER` exactly matches terminal server string, or omit credentials and reuse an active session |
| No data for symbol | Verify broker symbol naming and Market Watch visibility (`XAUUSD`, `XAUUSD.a`, `GOLD`, etc.) |
| Postgres connection issues | Verify `DATABASE_URL`, then run `psql "$DATABASE_URL" -c 'select 1;'` |
| Slow or stale UI analytics | Disable auto STL on heavy pairs/TFs and recalc manually |

## 🛣️ خارطة الطريق
- توسيع أصول تشغيل `i18n/` إلى ما هو أبعد من وثائق README متعددة اللغات.
- إضافة اختبارات آلية رسمية (API + تكامل + أتمتة smoke للواجهة).
- تحسين حزم النشر وملفات البيئة القابلة لإعادة الإنتاج.
- الاستمرار في تحسين التحقق من خطط AI وضمانات التنفيذ.

## 🤝 المساهمة
- اجعل التعديلات صغيرة ومحددة.
- استخدم بادئات commit واضحة عند الحاجة (مثل: `UI: ...`, `Server: ...`, `References: ...`).
- تجنب تغييرات التنسيق غير المرتبطة.
- أرفق لقطات شاشة/GIF لتغييرات الواجهة عند الملاءمة.
- شغّل smoke tests وتحقق من المتصفح محليًا قبل PR.

## ❤️ الدعم / الرعاية
روابط الدعم والرعاية مضبوطة في `.github/FUNDING.yml`:
- GitHub Sponsors: https://github.com/sponsors/lachlanchen
- Lazying.art: https://lazying.art
- Chat: https://chat.lazying.art
- OnlyIdeas: https://onlyideas.art

## 📚 المراجع
- `references/ai-trader-overview.md`
- `references/database_setup_postgres.md`
- `references/mt5_python_setup_ubuntu.md`
- `references/mt4_vs_mt5.md`
- `references/llm_trading_system.md`
- `references/release_deploy.md`
- `references/pnl_debugging.md`

## 📄 الترخيص
لا يوجد ملف `LICENSE` في هذا المستودع حتى تاريخ 2026-02-28.

Assumption: شروط الترخيص غير محددة حاليًا داخل المستودع؛ أبقِ هذه الملاحظة حتى يضيف المشرفون ملف ترخيص صريح.
