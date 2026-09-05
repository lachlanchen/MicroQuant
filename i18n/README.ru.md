[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# MetaTrader QT — Стартовый комплект для количественной торговли (философия Micro Quant)

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Backend](https://img.shields.io/badge/Backend-Tornado-2d7cbf)
![Database](https://img.shields.io/badge/Database-PostgreSQL-336791?logo=postgresql&logoColor=white)
![Broker](https://img.shields.io/badge/Broker%20Bridge-MetaTrader5-1f6feb)
![UI](https://img.shields.io/badge/UI-Lightweight%20Charts%20%2B%20Chart.js-0ea5e9)
![Status](https://img.shields.io/badge/README-Expanded-success)
![GitHub%20Stars](https://img.shields.io/github/stars/lachlanchen/MicroQuant?style=for-the-badge&logo=github&logoColor=white&labelColor=0f172a&color=0ea5e9)
![GitHub%20Issues](https://img.shields.io/github/issues/lachlanchen/MicroQuant?style=for-the-badge&logo=github&logoColor=white&labelColor=0f172a&color=ef4444)

## 🎯 Сводка проекта

| Фокус | Стек |
|---|---|
| Runtime | Tornado + asyncpg + WebSocket |
| Trading | MetaTrader5 + слоистый AI/tech/news контекст |
| Storage | PostgreSQL с детерминированным upsert пайплайном |
| Deployment | PWA-ресурсы + desktop/mobile интерфейсы в браузере |

## Оглавление
- [Скриншот](#-скриншот)
- [Обзор](#-обзор)
- [Основная философия](#-основная-философия)
- [Функции](#-функции)
- [Структура проекта](#-структура-проекта)
- [Требования](#-требования)
- [Установка](#-установка)
- [Конфигурация](#️-конфигурация)
- [Использование](#-использование)
- [API-эндпоинты (на практике)](#-api-эндпоинты-на-практике)
- [Примеры](#-примеры)
- [База данных и схема](#-база-данных-и-схема)
- [Контроль торговли и безопасность](#️-контроль-торговли-и-безопасность)
- [Переключатель авто-вычисления STL](#-переключатель-авто-вычисления-stl)
- [Запоминание последнего выбора](#-запоминание-последнего-выбора)
- [Контекст prompt для AI Trade Plan](#️-контекст-prompt-для-ai-trade-plan)
- [Заметки по разработке](#-заметки-по-разработке)
- [Устранение неполадок](#-устранение-неполадок)
- [Дорожная карта](#-дорожная-карта)
- [Вклад в проект](#-вклад-в-проект)
- [Источники](#-источники)
- [Поддержка](#️-support)
- [Лицензия](#-лицензия)

## 📸 Скриншот
![Micro Quant UI](figures/demos/micro-quant-ui.png)

[![DATA Source](https://img.shields.io/badge/Data_Source-RoboForex-0060ff?style=for-the-badge&labelColor=0a4eb3)](https://my.roboforex.com/en/?a=efx)

Раскрытие партнёрской связи: кнопка RoboForex выше содержит мой партнёрский код (`efx`), поэтому я могу получать комиссию за торговую активность привлечённых пользователей. Использование ссылки необязательно и не влияет на работу MicroQuant. Торговля с кредитным плечом связана с высоким риском убытков; этот проект — экспериментальное программное обеспечение, а не инвестиционная рекомендация или обещание доходности. Ознакомьтесь с [актуальной партнёрской программой](https://roboforex.com/partner-program/) и [раскрытием рисков](https://roboforex.com/about/company/documents/).

## 🧭 Обзор
Micro Quant — это не про глянцевые дашборды, а про повторяемый стек торговой логики: он получает OHLC-данные из MetaTrader 5, сохраняет их в PostgreSQL и принимает системные решения на основе многослойных AI-сигналов (Basic news, Tech snapshot, торговые планы и STL overlays). Интерфейс отражает эту философию через переключатели выравнивания, обоснованные закрытия, сохранённые настройки и информативную панель исполнения, чтобы сервер мог безопасно запускать периодические или модальные потоки торговли, пока вы контролируете логи и доказательства.

Статическая стартовая страница (Quant by Lazying.art) находится в `docs/` и публикуется через GitHub Pages (`quant.lazying.art` через `docs/CNAME`). Репозиторий также содержит справки по prompts AI Trade Plan, заметки по интеграции и эксплуатационную документацию.

### Кратко
| Область | Что делает |
|---|---|
| Данные | Извлекает OHLC из MT5 и выполняет upsert в PostgreSQL |
| Аналитика | Запускает health/news/tech и STL пайплайны |
| Принятие решений | Формирует AI trade plans из многослойного контекста |
| Выполнение | Выполняет и контролирует торговые потоки с защитами |
| UI | Desktop/mobile интерфейсы с синхронизированными сценариями работы с графиками |

## 🧠 Основная философия
- **Цепочка истины**: проверки Basic news (тексты и оценки) и Tech snapshot (богатый технический контекст + STL) формируют единый AI trade plan для каждого символа/таймфрейма. Периодические автозапуски и ручные модальные прогоны используют один pipeline и одни и те же логи обоснования.
- **Выполнение с приоритетом выравнивания**: переключатели Accept-Tech/Hold-Neutral, переключатель ignore-basics и обёртки частичного закрытия обеспечивают осознанное следование техничекским сигналам; противоположные позиции закрываются перед новыми входами при необходимости, а лишние выходы минимизируются.
- **Неподвижные данные**: каждый fetch пишет в Postgres с `ON CONFLICT`-гигиеной, а `/api/data` читает очищенные для UI ряды. Настройки (`auto`, `close_fraction`, переключатели скрытия тех-виджета, авто-вычисление STL) сохраняются через `/api/preferences`.
- **Безопасность прежде всего**: `TRADING_ENABLED` и `safe_max` управляют разрешениями для ручного и авто-режимов. `/api/close` и периодические раннеры логируют причины закрытий (нейтральный tech, рассогласование и т.д.) для трассируемости.

## ✨ Функции
- Импорт OHLC из MT5 в Postgres (`/api/fetch`, `/api/fetch_bulk`).
- Desktop UI на `/` и `/app` (mobile) с использованием Chart.js + Lightweight Charts в шаблонах.
- Процессы разложения STL (`/api/stl`, `/api/stl/compute`, endpoints prune/delete).
- Сбор и анализ новостей (`/api/news`, `/api/news/backfill_forex`, `/api/news/analyze`).
- Оркестрация AI workflow (`/api/health/run`, `/api/health/runs`, `/api/ai/trade_plan`).
- Ручное исполнение сделок (`/api/trade`, `/api/trade/execute_plan`) с защитой через `TRADING_ENABLED`.
- Операции с риском по позициям (`/api/positions*`, `/api/close`, `/api/close_tickets`) с закрытиями только при явном безопасном поведении.
- WebSocket-стрим обновлений на `/ws/updates` для realtime-уведомлений и сигналов обновления.
- PWA- и статические активы для установки дашборда.

## 🗂️ Структура проекта
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
├── i18n/                        # Translated docs (currently language only)
├── .github/FUNDING.yml          # Sponsor/support metadata
└── README.md + README.*.md      # Canonical + multilingual docs
```

## ✅ Требования
- Ubuntu/Linux или Windows с доступом к терминалу.
- MetaTrader 5 установлен (`terminal64.exe`) и сессия авторизации при необходимости.
- Python 3.10+ (рекомендуется 3.11 для лучшей совместимости с MetaTrader5 wheels).
- Доступный PostgreSQL-инстанс для серверного приложения.
- Необязательные ключи API для новостных провайдеров:
  - FMP
  - Alpha Vantage

## 🛠️ Установка

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

## ⚙️ Конфигурация
Copy `.env.example` to `.env` and adjust values.

### Базовые переменные
| Переменная | Назначение |
|---|---|
| `DATABASE_URL` | Предпочтительный DSN PostgreSQL |
| `DATABASE_MT_URL` | Резервный DSN, если `DATABASE_URL` не указан |
| `DATABASE_QT_URL` | Вторичный резервный DSN |
| `MT5_PATH` | Путь к `terminal64.exe` (Wine или native) |
| `MT5_LOGIN` / `MT5_PASSWORD` / `MT5_SERVER` | Необязательно, если сессия MT5 уже вошла |
| `PORT` | Порт сервера (по умолчанию `8888`) |

### Дополнительные переменные
- `FMP_API_KEY`, `ALPHAVANTAGE_API_KEY` для обогащения новостной аналитики.
- `TRADING_ENABLED` (`0` по умолчанию, установите `1`, чтобы разрешить endpoints размещения ордеров).
- `TRADING_VOLUME` (объём ручной торговли по умолчанию).
- `AUTO_FETCH`, `AUTO_FETCH_SYMBOL`, `AUTO_FETCH_TF`, `AUTO_FETCH_COUNT`, `AUTO_FETCH_SEC`.
- `PIN_DEFAULTS_TO_XAU_H1=1`, чтобы принудительно задавать стартовые символ/таймфрейм в UI.
- `LOG_LEVEL`, `LOG_BACKFILL`, а также account/poll предпочтения через `/api/preferences` и переменные окружения.

Notes:
- `MT5_PATH` должен указывать на `terminal64.exe` внутри Wine prefix, используемого вашим скриптом установки MT5.
- Если сессия терминала уже активна, учётные данные MT5 можно не указывать; приложение попытается переиспользовать текущую сессию.

## 🚀 Использование

### Запуск сервера
```bash
python -m app.server
```

### Открытие UI
- Desktop UI: `http://localhost:8888/`
- Mobile UI: `http://localhost:8888/app`

### Ключевые URL
| Интерфейс | URL | Назначение |
|---|---|---|
| Desktop | `http://localhost:8888/` | Графики и управляемые desktop-настройки |
| Mobile | `http://localhost:8888/app` | Тач-ориентированный интерфейс с компактными контролами |
| API Health | `http://localhost:8888/api/health/freshness` | Быстрая проверка готовности данных и сервиса |

### Стандартный рабочий процесс
1. Получите бары из MT5 и сохраните их в Postgres.
2. Читайте бары из БД для построения графиков.
3. Запускайте анализ health/tech/news.
4. Генерируйте AI trade plan.
5. Исполняйте или закрывайте позиции с учётом защит.

## 🔌 API-эндпоинты (на практике)
- `GET /api/fetch?symbol=XAUUSD&tf=H1&count=500[&mode=inc|full][&persist=1]`
  - Извлекает из MT5 и выполняет upsert в БД.
  - Если `persist=1`, сервер сохраняет `last_symbol/last_tf/last_count` как значения по умолчанию; массовые/фоновый fetch лучше отправлять без этого флага, чтобы не перезаписывать пользовательские настройки.
- `GET /api/fetch_bulk` — массовый/периодический импорт.
- `GET /api/data?symbol=XAUUSD&tf=H1&limit=500` — чтение данных для графиков из БД.
- `GET /api/strategy/run?symbol=XAUUSD&tf=H1&fast=20&slow=50`
  - Запускает пересечение SMA(20/50) и возвращает payload сигнала.
  - Важно: placement ордеров из этого endpoint пока отключён в коде сервера; исполнение сделок идёт через trade-endpoints.
- `POST /api/trade` — ручной Buy/Sell из UI, защищённый `TRADING_ENABLED`.
- `POST /api/trade/execute_plan` — выполняет сгенерированный план, включает проверки pre-close и расстояния до stop.
- `POST /api/close` — закрывает позиции (разрешено даже при `TRADING_ENABLED=0` для безопасности):
  - Текущий символ: тело запроса `symbol=...`; необязательный `side=long|short|both`.
  - Все символы: `?scope=all` и опционально `&side=...`.
  - В ответе возвращается `closed_count` и результаты по каждому тикету.
- `POST /api/close_tickets` — закрыть выбранный поднабор тикетов.
- `GET /api/positions`, `GET /api/positions/all`.
- `GET /api/stl`, `POST /api/stl/compute`, `POST /api/stl/prune`, `POST /api/stl/prune_all`, `DELETE /api/stl/run/{id}`.
- `GET /api/news`, `POST /api/news/backfill_forex`, `POST /api/news/analyze`.
- `GET /api/health/freshness`, `GET /api/tech/freshness`, `GET|POST /api/health/run`, `GET /api/health/runs`.
- `POST /api/preferences` и получение сохранённых настроек.
- `GET /api/ai/trade_plan`.
- `GET /api/accounts`, `GET /api/account/current`, `POST /api/account/login`.
- `GET /ws/updates`.

## 🧪 Примеры
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

## 🗄️ База данных и схема
See `sql/schema.sql`.

Ключевые моменты:
- Составной PK `(symbol, timeframe, ts)` в `ohlc_bars` предотвращает дублирование баров.
- Ingestion uses `ON CONFLICT ... DO UPDATE`.
- Дополнительные таблицы поддерживают STL runs/components, preferences, news articles, health runs, account series, closed deals и связь signal/order-plan.

## 🛡️ Контроль торговли и безопасность
- Защита окружения: `TRADING_ENABLED=0` по умолчанию отключает размещение ордеров из ручных/plan execution endpoint-ов.
- UI-переключатель Auto планирует проверки стратегии; он не обходйт правила безопасности торговли.
- Операции закрытия намеренно разрешены даже при выключенном торговом режиме.
- В потоки исполнения встроены safe-max и взвешивание symbol/kind для ограничения экспозиции.

## 📈 Переключатель авто-вычисления STL
- Автовычисление STL настраивается по символу × таймфрейму через switch `Auto STL` в панели STL.
- По умолчанию OFF, чтобы уменьшить лаги интерфейса на больших/медленных контекстах.
- При ON отсутствующий/устаревший STL может вычисляться автоматически; в остальных случаях используйте ручной пересчёт.
- Состояние сохраняется через ключи `/api/preferences` вида `stl_auto_compute:SYMBOL:TF`, а также в `localStorage` для быстрого старта.

## 🧷 Запоминание последнего выбора
- Сервер сохраняет `last_symbol`, `last_tf`, `last_count` и внедряет значения по умолчанию в шаблоны.
- UI также сохраняет `last_symbol`/`last_tf` в `localStorage`.
- `/?reset=1` игнорирует сохранённые настройки только для этой загрузки страницы.
- `PIN_DEFAULTS_TO_XAU_H1=1` может принудительно задавать стартовые значения.

## 🤖 Контекст prompt для AI Trade Plan
При запросе AI trade plan сервер сначала гарантирует наличие актуальных запусков Basic Health и Tech Snapshot для текущего symbol/timeframe (создаёт их при необходимости), затем строит контекст запроса из:
- блока Basic health,
- Tech AI-блока,
- блока Live technical snapshot.

## 🧰 Заметки по разработке
- Основные runtime-зависимости: `tornado`, `asyncpg`, `MetaTrader5`, `numpy`, `python-dotenv`, `requests`, `httpx`, `statsmodels`, `openai`.
- Формального автоматического test suite пока не настроено; активный workflow — smoke-тесты и ручная UI-проверка.
- Рекомендуемые smoke-тесты:
  - `python scripts/test_mixed_ai.py`
  - `python scripts/test_fmp.py`
  - `python scripts/test_fmp_endpoints.py`
- Ручные проверки перед релизом:
  - pan/zoom sync,
  - поведение STL overlay/period-line,
  - торговые настройки (включая поведение close safety),
  - fallback-поведение панели новостей.

## 🧯 Устранение неполадок
| Симптом | Действие |
|---|---|
| Не удалось инициализировать MT5 | Укажите `MT5_PATH` точно до `terminal64.exe`, затем вручную запустите терминал хотя бы один раз |
| Не удалось войти в MT5 | Проверьте, что `MT5_SERVER` точно совпадает со строкой сервера терминала, или пропустите креды и повторно используйте активную сессию |
| Нет данных по символу | Проверьте имя символа у брокера и его видимость в Market Watch (`XAUUSD`, `XAUUSD.a`, `GOLD` и т.д.) |
| Ошибки подключения к Postgres | Проверьте `DATABASE_URL`, затем выполните `psql "$DATABASE_URL" -c 'select 1;'` |
| Медленная или устаревшая аналитика в UI | Отключите auto STL на тяжелых парах/TF и пересчитывайте вручную |

## 🛣️ Дорожная карта
- Расширить runtime-ресурсы в `i18n/` за пределами README-переводов.
- Добавить формальные автоматические тесты (API + integration + UI smoke).
- Улучшить сборку деплоя и воспроизводимые профили окружения.
- Дальнейшая доработка валидации AI-планов и мер безопасности исполнения.

## 🤝 Вклад в проект
- Делайте изменения небольшими и целевыми.
- Используйте понятные префиксы коммитов, где это применимо (например: `UI: ...`, `Server: ...`, `References: ...`).
- Избегайте ненужного форматного шума.
- Добавляйте скриншоты/GIF для изменений UI, где это уместно.
- Запускайте smoke-тесты и локальные браузерные проверки перед PR.

## 📚 Источники
- `references/ai-trader-overview.md`
- `references/database_setup_postgres.md`
- `references/mt5_python_setup_ubuntu.md`
- `references/mt4_vs_mt5.md`
- `references/llm_trading_system.md`
- `references/release_deploy.md`
- `references/pnl_debugging.md`

## 📄 Лицензия
No `LICENSE` file is present in this repository as of 2026-02-28.

Предположение: условия лицензирования в репозитории на данный момент не указаны; сохраните эту заметку, пока мейнтейнеры не добавят явный файл лицензии.


## ❤️ Support

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://camo.githubusercontent.com/24a4914f0b42c6f435f9e101621f1e52535b02c225764b2f6cc99416926004b7/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f446f6e6174652d4c617a79696e674172742d3045413545393f7374796c653d666f722d7468652d6261646765266c6f676f3d6b6f2d6669266c6f676f436f6c6f723d7768697465)](https://chat.lazying.art/donate) | [![PayPal](https://camo.githubusercontent.com/d0f57e8b016517a4b06961b24d0ca87d62fdba16e18bbdb6aba28e978dc0ea21/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f50617950616c2d526f6e677a686f754368656e2d3030343537433f7374796c653d666f722d7468652d6261646765266c6f676f3d70617970616c266c6f676f436f6c6f723d7768697465)](https://paypal.me/RongzhouChen) | [![Stripe](https://camo.githubusercontent.com/1152dfe04b6943afe3a8d2953676749603fb9f95e24088c92c97a01a897b4942/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f5374726970652d446f6e6174652d3633354246463f7374796c653d666f722d7468652d6261646765266c6f676f3d737472697065266c6f676f436f6c6f723d7768697465)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |
