[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://lazying.art)

# MetaTrader QT - نظام تداول كمي عملي (فلسفة Micro Quant)

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Backend](https://img.shields.io/badge/Backend-Tornado-2d7cbf)
![Database](https://img.shields.io/badge/Database-PostgreSQL-336791?logo=postgresql&logoColor=white)
![Broker](https://img.shields.io/badge/Broker%20Bridge-MetaTrader5-1f6feb)
![UI](https://img.shields.io/badge/UI-Lightweight%20Charts%20%2B%20Chart.js-0ea5e9)
![Status](https://img.shields.io/badge/README-Expanded-success)
![GitHub%20Stars](https://img.shields.io/github/stars/lachlanchen/MicroQuant?style=for-the-badge&logo=github&logoColor=white&labelColor=0f172a&color=0ea5e9)
![GitHub%20Issues](https://img.shields.io/github/issues/lachlanchen/MicroQuant?style=for-the-badge&logo=github&logoColor=white&labelColor=0f172a&color=ef4444)

## 🎯 لمحة المشروع

| التركيز | المكدس |
|---|---|
| Runtime | Tornado + asyncpg + WebSocket |
| Trading | MetaTrader5 + سياق AI/تقني/أخبار متعدد الطبقات |
| Storage | PostgreSQL مع خط أنابيب upsert حتمي |
| Deployment | أصول PWA + واجهات سطح المكتب/الجوال الأولى للأجهزة المتصفحة |

## جدول المحتويات
- [📸 لقطة الشاشة](#-لقطة-الشاشة)
- [🧭 الملخص](#-الملخص)
- [🧠 الفلسفة الأساسية](#-الفلسفة-الأساسية)
- [✨ الميزات](#-الميزات)
- [🗂️ هيكلة المشروع](#️-هيكلة-المشروع)
- [✅ المتطلبات الأساسية](#-المتطلبات-الأساسية)
- [🛠️ التثبيت](#️-التثبيت)
- [⚙️ الإعدادات](#️-الإعدادات)
- [🚀 الاستخدام](#-الاستخدام)
- [🔌 واجهات API (عملي)](#-واجهات-api-عملي)
- [🧪 أمثلة](#-أمثلة)
- [🗄️ قاعدة البيانات والمخطط](#️-قاعدة-البيانات-والمخطط)
- [🛡️ ضبط الأمان والتداول](#️-ضبط-الأمان-والتداول)
- [📈 تبديل تشغيل STL التلقائي](#-تبديل-تشغيل-stl-التلقائي)
- [🧷 تذكر آخر اختيار](#-تذكر-آخر-اختيار)
- [🤖 سياق خطة تداول AI](#️-سياق-خطة-تداول-ai)
- [🧰 ملاحظات التطوير](#-ملاحظات-التطوير)
- [🧯 استكشاف الأخطاء](#-استكشاف-الأخطاء)
- [🛣️ خارطة الطريق](#️-خارطة-الطريق)
- [🤝 المساهمة](#-المساهمة)
- [📚 المراجع](#-المراجع)
- [❤️ الدعم](#️-support)
- [📄 الترخيص](#-الترخيص)

## 📸 لقطة الشاشة
![Micro Quant UI](figures/demos/micro-quant-ui.png)

[![DATA Source](https://img.shields.io/badge/Data_Source-RoboForex-0060ff?style=for-the-badge&labelColor=0a4eb3)](https://my.roboforex.com/en/?a=efx)

إفصاح عن الشراكة: يحتوي زر RoboForex أعلاه على رمز الشريك الخاص بي (`efx`)، ولذلك قد أتلقى عمولة من نشاط التداول للمستخدمين المُحالين. استخدامه اختياري ولا يؤثر في طريقة عمل MicroQuant. ينطوي التداول بالرافعة المالية على مخاطر مرتفعة للخسارة؛ وهذا المشروع برنامج تجريبي، وليس نصيحة استثمارية ولا وعدًا بعوائد. راجع [برنامج الشراكة الحالي](https://roboforex.com/partner-program/) و[بيان المخاطر](https://roboforex.com/about/company/documents/).

## 🧭 الملخص
Micro Quant ليس مشروعًا لواجهات لامعة بقدر ما هو بنية منطق تداول قابلة للتكرار: يجلب بيانات OHLC من MetaTrader 5، ويحفظها في PostgreSQL، ثم يقيم قرارات منهجية عبر إشارات AI متعددة الطبقات (الأخبار الأساسية، لقطة تقنية، خطط التداول، وطبقات STL). تعكس واجهة المستخدم هذه الفلسفة عبر مفاتيح محاذاة، وأوامر إغلاق مبررة، وتفضيلات ثابتة، ولوحة تنفيذ غنية بالبيانات بحيث يستطيع الخادم تشغيل مسارات التداول الدورية أو اليدوية بأمان بينما تراجع السجلات والأدلة.

صفحة الهبوط الثابتة (Quant by Lazying.art) موجودة في `docs/` وتنشر عبر GitHub Pages (`quant.lazying.art` عبر `docs/CNAME`). المستودع يضم أيضًا مراجع لطلبات AI Trade Plan، ملاحظات التكامل، والتوثيق التشغيلي.

### نظرة سريعة
| المجال | الوصف |
|---|---|
| البيانات | يجلب OHLC من MT5 ويعمل upsert في PostgreSQL |
| التحليل | يشغّل سلاسل Health/News/Tech وSTL |
| اتخاذ القرار | يبني خطط AI التداول من سياق متعدد المستويات |
| التنفيذ | ينفذ/يضبط مسارات التداول خلف ضوابط الأمان |
| الواجهة | عرض سطح المكتب والجوال مع سير عمل مخطط متزامن |

## 🧠 الفلسفة الأساسية
- **سلسلة الحقيقة**: فحوص الأخبار الأساسية (نص + نقاط) ولقطات Tech (سياق تقني موسع + STL) تغذي خطة تداول AI واحدة لكل رمز/إطار زمني. التشغيل الدوري التلقائي والتشغيل اليدوي عبر النافذة يشاركان نفس خط الأنابيب وسجلات التبرير.
- **تنفيذ يعتمد على المحاذاة**: مفاتيح Accept-Tech/Hold-Neutral، ومفتاح تجاهل الأساسيات، وأدوات الإغلاق الجزئي تضمن اتباع التحليل الفني عن قصد، وإغلاق المراكز العكسية قبل فتح صفقات جديدة عند الحاجة، وتقليل الإغلاقات غير الضرورية.
- **بيانات ثابتة**: كل جلب يكتب إلى Postgres مع ضبط `ON CONFLICT`، بينما تقرأ `/api/data` سلاسل نظيفة للواجهة. تفضل المستخدمين (`auto` settings، `close_fraction`، مفاتيح إخفاء التحليل الفني، Auto STL) تُحفظ عبر `/api/preferences`.
- **تداول يضع السلامة أولًا**: `TRADING_ENABLED` و`safe_max` يفرضان أذونات الوضع اليدوي/التلقائي. تسجّل `/api/close` والمدراء الدوريون أسباب الإغلاق (حياد فني، عدم محاذاة...) لضمان تتبع واضح.

## ✨ الميزات
- استيراد OHLC من MT5 إلى Postgres (`/api/fetch`, `/api/fetch_bulk`).
- واجهة المخطط في `/` (desktop) بالإضافة إلى `/app` (mobile)، مع استخدام Chart.js + Lightweight Charts في القوالب.
- تدفق تفكيك STL (`/api/stl`, `/api/stl/compute`, endpoints للحذف/القص).
- جمع الأخبار وتحليلها (`/api/news`, `/api/news/backfill_forex`, `/api/news/analyze`).
- تنسيق مسار AI (`/api/health/run`, `/api/health/runs`, `/api/ai/trade_plan`).
- تنفيذ تداول يدوي (`/api/trade`, `/api/trade/execute_plan`) محمي بواسطة `TRADING_ENABLED`.
- عمليات مخاطر المراكز (`/api/positions*`, `/api/close`, `/api/close_tickets`) مع السماح بعمليات الإغلاق ضمن سلوك أمني صريح.
- تدفق تحديث WebSocket على `/ws/updates` للتنبيهات اللحظية وإشارات التحديث.
- أصول PWA/ثابتة للوحة تحكم قابلة للتثبيت.

## 🗂️ هيكلة المشروع
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
├── strategies/
│   ├── llm/
│   ├── # Prompt/config JSON files
├── llm_model/
│   ├── echomind/
│   ├── # LLM provider wrappers
i18n/
│   ├── # Translated docs (currently language only)
├── .github/FUNDING.yml          # Sponsor/support metadata
└── README.md + README.*.md      # Canonical + multilingual docs
```

## ✅ المتطلبات الأساسية
- Ubuntu/Linux أو Windows مع وصول إلى الطرفية.
- MetaTrader 5 مثبت (`terminal64.exe`) ومسجّل الدخول عند الحاجة.
- Python 3.10+ (يفضل Python 3.11 لتوافق أفضل مع حزم MetaTrader5).
- نسخة PostgreSQL يمكن الوصول إليها من خادم التطبيق.
- مفاتيح API اختيارية لمزودي الأخبار:
  - FMP
  - Alpha Vantage

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

# Alternative: local 3.11 venv (if global Python is newer)
# Requires python3.11 on your system
# sudo apt install python3.11 python3.11-venv
bash scripts/bootstrap_venv311.sh
source .venv311/bin/activate

# DB (use your own user/password as needed)
# createdb -h localhost -p 5432 -U lachlan metatrader_db

# Configure env
cp .env.example .env
# edit .env with your MT5 path and credentials
test -f .env && set -a; source .env; set +a

# Run app
python -m app.server
# Open http://localhost:8888
```

## ⚙️ الإعدادات
انسخ `.env.example` إلى `.env` وقم بتعديل القيم.

### المتغيرات الأساسية
| المتغير | الغرض |
|---|---|
| `DATABASE_URL` | DSN المفضل لـ PostgreSQL |
| `DATABASE_MT_URL` | DSN احتياطي إذا لم يُضبط `DATABASE_URL` |
| `DATABASE_QT_URL` | DSN احتياطي ثانٍ |
| `MT5_PATH` | المسار إلى `terminal64.exe` (Wine أو النظام الأصلي) |
| `MT5_LOGIN` / `MT5_PASSWORD` / `MT5_SERVER` | اختيارية إذا كانت جلسة MT5 مُفتوحة بالفعل |
| `PORT` | منفذ الخادم (الافتراضي `8888`) |

### المتغيرات الاختيارية
- `FMP_API_KEY`, `ALPHAVANTAGE_API_KEY` لتعزيز الأخبار.
- `TRADING_ENABLED` (`0` افتراضي، اضبط `1` للسماح بنقاط تنفيذ الأوامر).
- `TRADING_VOLUME` (الحجم اليدوي الافتراضي).
- `AUTO_FETCH`, `AUTO_FETCH_SYMBOL`, `AUTO_FETCH_TF`, `AUTO_FETCH_COUNT`, `AUTO_FETCH_SEC`.
- `PIN_DEFAULTS_TO_XAU_H1=1` لفرض رمز/إطار افتراضي عند بدء الواجهة.
- `LOG_LEVEL`, `LOG_BACKFILL`، بالإضافة إلى تفضيلات الحساب وpoll عبر `/api/preferences` والبيئة.

ملاحظات:
- يجب أن يشير `MT5_PATH` إلى `terminal64.exe` الصحيح داخل بريفكس Wine المستخدم في سكربت تثبيت MT5.
- يمكن حذف بيانات اعتماد MT5 عندما تكون جلسة الطرفية مفعّلة بالفعل؛ سيحاول التطبيق إعادة استخدام نفس الجلسة.

## 🚀 الاستخدام

### تشغيل الخادم
```bash
python -m app.server
```

### فتح الواجهة
- واجهة سطح المكتب: `http://localhost:8888/`
- واجهة الجوال: `http://localhost:8888/app`

### الروابط المهمة
| السطح | الرابط | الغرض |
|---|---|---|
| desktop | `http://localhost:8888/` | مخطط الشموع وعناصر التحكم في سير عمل سطح المكتب |
| mobile | `http://localhost:8888/app` | واجهة لمس أولية بواجهات تحكم مضغوطة |
| API Health | `http://localhost:8888/api/health/freshness` | فحص سريع لخدمات البيانات وجاهزية الخدمة |

### سير العمل المعتاد
1. جلب الشموع من MT5 وحفظها في Postgres.
2. قراءة الشموع من قاعدة البيانات للرسم.
3. تشغيل تحليلات الصحة/المؤشرات الفنية/الأخبار.
4. توليد خطة تداول AI.
5. تنفيذ أو إغلاق المراكز وفق ضوابط الأمان.

## 🔌 واجهات API (عملي)
- `GET /api/fetch?symbol=XAUUSD&tf=H1&count=500[&mode=inc|full][&persist=1]`
  - جلب البيانات من MT5 و upsert إلى قاعدة البيانات.
  - إذا كانت `persist=1`، يحفظ الخادم افتراضيات `last_symbol/last_tf/last_count`؛ يجب استبعاد هذا في جلبات bulk/background حتى لا تُستبدل اختيارات الواجهة.
- `GET /api/fetch_bulk` — استيعاب/جدولة الاستيراد بالجملة.
- `GET /api/data?symbol=XAUUSD&tf=H1&limit=500` — قراءة بيانات الشارت من قاعدة البيانات.
- `GET /api/strategy/run?symbol=XAUUSD&tf=H1&fast=20&slow=50`
  - يشغّل تقاطع SMA(20/50) ويعيد حمولة الإشارة.
  - ملاحظة تنفيذية: تنفيذ الأوامر المبني على الاستراتيجية من هذا المسار معطّل حاليًا في كود الخادم؛ التنفيذ الفعلي عبر مسارات التداول.
- `POST /api/trade` — شراء/بيع يدوي من الواجهة، محمي بواسطة `TRADING_ENABLED`.
- `POST /api/trade/execute_plan` — ينفذ خطة مولدة، ويشمل فحوص الإغلاق المسبق ومسافة الوقف.
- `POST /api/close` — إغلاق المراكز (مسموح حتى مع `TRADING_ENABLED=0` لأسباب سلامة):
  - الرمز الحالي: body `symbol=...`; `side=long|short|both` اختياري.
  - كل الرموز: `?scope=all` و `&side=...` اختياري.
  - الاستجابة تتضمن `closed_count` ونتائج كل تذكرة.
- `POST /api/close_tickets` — إغلاق مجموعة محددة حسب التذكرة.
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
انظر `sql/schema.sql`.

النقاط البارزة:
- المفتاح المركب `(symbol, timeframe, ts)` في `ohlc_bars` يمنع تكرار الشموع.
- ingestion يستخدم `ON CONFLICT ... DO UPDATE`.
- هناك جداول إضافية تدعم عمليات STL/المكونات، التفضيلات، أخبار، health runs، series الحساب، الصفقات المغلقة، وربط إشارات/الخطط بالأوامر.

## 🛡️ ضبط الأمان والتداول
- حماية البيئة: `TRADING_ENABLED=0` افتراضياً، وتعطل وضع أوامر التنفيذ عبر واجهات manual/plan execution.
- سلوك `Auto` في الواجهة يحدد فحوص الاستراتيجية؛ لكنه لا يتجاوز بوابات أمان التداول.
- عمليات الإغلاق مفعلة بشكل مقصود حتى عند تعطيل التداول.
- يتم استخدام Safe-max وترجيحات الرمز/النوع في مسارات التنفيذ لتقييد التعرض.

## 📈 تبديل تشغيل STL التلقائي
- تشغيل STL التلقائي مضبوط لكل رمـز/إطار عبر مفتاح `Auto STL` في لوحة STL.
- الإعداد الافتراضي معطّل لتقليل بطء الواجهة في سياقات بطيئة أو كبيرة.
- عند التفعيل، STL المفقود/القديم يُحسَب تلقائيًا، وإلا استخدم أزرار إعادة الحساب اليدوية.
- الحالة محفوظة عبر مفاتيح `/api/preferences` مثل `stl_auto_compute:SYMBOL:TF` وكذلك عبر localStorage لبدء أسرع.

## 🧷 تذكر آخر اختيار
- الخادم يحفظ `last_symbol` و`last_tf` و`last_count` ويدمج القيم الافتراضية في القوالب.
- الواجهة أيضًا تخزن `last_symbol`/`last_tf` في `localStorage`.
- `/?reset=1` تتجاهل التفضيلات المخزنة في تلك التحميلة.
- `PIN_DEFAULTS_TO_XAU_H1=1` يمكنها فرض الإعداد الافتراضي.

## 🤖 سياق خطة تداول AI
عند طلب خطة AI trading، يضمن الخادم وجود نتائج Health أساسية وTech Snapshot حديثة للإطار والرمز الحالي (وإعدادها إذا كانت مفقودة)، ثم يبني سياق الطلب من:
- كتلة الصحة الأساسية,
- كتلة AI الفنية,
- كتلة snapshot الفني المباشر.

## 🧰 ملاحظات التطوير
- التبعيات الأساسية في التشغيل: `tornado`, `asyncpg`, `MetaTrader5`, `numpy`, `python-dotenv`, `requests`, `httpx`, `statsmodels`, `openai`.
- لا توجد حالياً مجموعة اختبارات آلية رسمية؛ فاختبارات Smoke وعمليات تحقق يدوي للواجهة هي سير العمل الفعلي.
- اختبارات smoke المقترحة:
  - `python scripts/test_mixed_ai.py`
  - `python scripts/test_fmp.py`
  - `python scripts/test_fmp_endpoints.py`
- فحوص يدوية قبل الإطلاق:
  - مزامنة pan/zoom
  - سلوك STL overlay/period line
  - controls التداول (بما فيها سلوك الإغلاق الآمن)
  - fallback لوحة الأخبار

## 🧯 استكشاف الأخطاء
| عرض | الإجراء |
|---|---|
| فشل تهيئة MT5 | اضبط `MT5_PATH` على `terminal64.exe` بالضبط، ثم شغّل terminal يدويًا مرة واحدة على الأقل |
| فشل تسجيل دخول MT5 | تأكد من `MT5_SERVER` مطابقًا تمامًا لاسم الخادم في terminal، أو اترك بيانات الدخول واستخدم جلسة نشطة |
| لا توجد بيانات للرمز | تأكد من أسماء الرموز في الوسيط وظهورها في Market Watch (`XAUUSD`, `XAUUSD.a`, `GOLD`, وغيرها) |
| مشاكل اتصال Postgres | تحقق من `DATABASE_URL` ثم نفذ `psql "$DATABASE_URL" -c 'select 1;'` |
| تحليلات الواجهة بطيئة أو قديمة | أوقف Auto STL على الأزواج/الأطر الثقيلة وأعد الحساب يدويًا |

## 🛣️ خارطة الطريق
- توسيع أصول `i18n/` ليشمل عناصر runtime إلى جانب ترجمة ملفات README.
- إضافة اختبارات آلية رسمية (API + integration + UI smoke automation).
- تحسين حزم النشر وملفات البيئة القابلة لإعادة التكرار.
- الاستمرار في صقل تحقق خطة AI وأمان التنفيذ.

## 🤝 المساهمة
- اجعل التعديلات صغيرة ومركزة.
- استخدم بادئات commit واضحة حيث تنطبق (مثل: `UI: ...`, `Server: ...`, `References: ...`).
- تجنب تعديل تنسيق غير مرتبط.
- أرفق لقطات شاشة أو GIFs لتغييرات الواجهة إن كانت ذات صلة.
- شغل smoke tests وفحوص المتصفح محليًا قبل PRs.

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

الافتراض: شروط الترخيص غير محددة حاليًا داخل المستودع؛ احتفظ بهذه الملاحظة حتى يضيف المشرفون ملف ترخيص صريح.


## ❤️ Support

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://camo.githubusercontent.com/24a4914f0b42c6f435f9e101621f1e52535b02c225764b2f6cc99416926004b7/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f446f6e6174652d4c617a79696e674172742d3045413545393f7374796c653d666f722d7468652d6261646765266c6f676f3d6b6f2d6669266c6f676f436f6c6f723d7768697465)](https://chat.lazying.art/donate) | [![PayPal](https://camo.githubusercontent.com/d0f57e8b016517a4b06961b24d0ca87d62fdba16e18bbdb6aba28e978dc0ea21/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f50617950616c2d526f6e677a686f754368656e2d3030343537433f7374796c653d666f722d7468652d6261646765266c6f676f3d70617970616c266c6f676f436f6c6f723d7768697465)](https://paypal.me/RongzhouChen) | [![Stripe](https://camo.githubusercontent.com/1152dfe04b6943afe3a8d2953676749603fb9f95e24088c92c97a01a897b4942/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f5374726970652d446f6e6174652d3633354246463f7374796c653d666f722d7468652d6261646765266c6f676f3d737472697065266c6f676f436f6c6f723d7768697465)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |
