[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


<p align="center">
  <img src="https://raw.githubusercontent.com/lachlanchen/lachlanchen/main/logos/banner.png" alt="LazyingArt banner" />
</p>

# MetaTrader QT - Стартовый набор для количественной торговли (философия Micro Quant)

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Backend](https://img.shields.io/badge/Backend-Tornado-2d7cbf)
![Database](https://img.shields.io/badge/Database-PostgreSQL-336791?logo=postgresql&logoColor=white)
![Broker](https://img.shields.io/badge/Broker%20Bridge-MetaTrader5-1f6feb)
![UI](https://img.shields.io/badge/UI-Lightweight%20Charts%20%2B%20Chart.js-0ea5e9)
![Status](https://img.shields.io/badge/README-Expanded-success)

## 📸 Скриншот
![Micro Quant UI](figures/demos/micro-quant-ui.png)

<p align="center">
  <a href="https://my.roboforex.com/en/?a=efx" target="_blank" rel="noopener noreferrer">
    <button style="padding: 0.65rem 1.25rem; font-weight: 600; border-radius: 999px; border: none; color: white; background: #0060ff; cursor: pointer;">
      DATA Source
    </button>
  </a>
</p>

## 🧭 Обзор
Micro Quant - это не про «глянцевые» дашборды, а про воспроизводимый стек торговой логики: система получает OHLC-данные из MetaTrader 5, сохраняет их в Postgres и оценивает системные решения через многослойные AI-сигналы (Basic news, Tech snapshot, trade plans и STL overlays). UI отражает эту философию: переключатели выравнивания, обоснованные закрытия, сохраненные предпочтения и насыщенная данными панель исполнения позволяют серверу безопасно выполнять периодические или модальные торговые сценарии, пока вы проверяете логи и подтверждающие данные.

Статическая посадочная страница (Quant by Lazying.art) находится в `docs/` и публикуется через GitHub Pages (`trade.lazying.art` через `docs/CNAME`). В репозитории также есть справочные материалы по промптам AI Trade Plan, заметки по интеграции и эксплуатационная документация.

### Кратко
| Область | Что делает |
|---|---|
| Data | Получает MT5 OHLC и делает upsert в PostgreSQL |
| Analytics | Запускает health/news/tech и STL-процессы |
| Decisioning | Строит AI trade plans из многослойного контекста |
| Execution | Выполняет/контролирует торговые сценарии с защитными ограничениями |
| UI | Desktop/mobile интерфейсы с синхронизированными сценариями работы с графиками |

## 🧠 Базовая философия
- **Chain of truth**: проверки Basic news (текст + score) и Tech snapshot (расширенный технический контекст + STL) формируют единый AI trade plan для каждой пары symbol/timeframe. Периодические автозапуски и ручные модальные запуски используют один и тот же pipeline и одни и те же reasoning logs.
- **Alignment-first execution**: переключатели Accept-Tech/Hold-Neutral, флаг ignore-basics и partial-close wrappers обеспечивают осознанное следование Tech, закрытие противоположных позиций перед новыми входами при необходимости и минимизацию лишних выходов.
- **Immutable data**: каждое получение данных записывается в Postgres с гигиеной `ON CONFLICT`, а `/api/data` отдает UI очищенные ряды. Предпочтения (auto volumes, `close_fraction`, hide-tech toggles, STL auto-compute) сохраняются через `/api/preferences`.
- **Safety-first trading**: `TRADING_ENABLED` и `safe_max` контролируют права для ручных/автоматических сценариев. `/api/close` и периодические раннеры могут логировать причины закрытия (tech neutral, misalignment и т.д.) для трассируемости.

## ✨ Возможности
- Загрузка MT5 OHLC в Postgres (`/api/fetch`, `/api/fetch_bulk`).
- Интерфейс графиков на `/` (desktop) и `/app` (mobile), с использованием Chart.js + Lightweight Charts в шаблонах.
- Процессы STL decomposition (`/api/stl`, `/api/stl/compute`, prune/delete endpoints).
- Загрузка и анализ новостей (`/api/news`, `/api/news/backfill_forex`, `/api/news/analyze`).
- Оркестрация AI workflows (`/api/health/run`, `/api/health/runs`, `/api/ai/trade_plan`).
- Ручное исполнение сделок (`/api/trade`, `/api/trade/execute_plan`) под контролем `TRADING_ENABLED`.
- Операции по позициям и риску (`/api/positions*`, `/api/close`, `/api/close_tickets`), при этом close-операции разрешены для безопасности.
- Поток обновлений WebSocket на `/ws/updates`.

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
├── i18n/                        # Present (currently empty)
├── .github/FUNDING.yml          # Sponsor/support metadata
└── README.md + README.*.md      # Canonical + multilingual docs
```

## ✅ Предварительные требования
- Ubuntu/Linux или Windows.
- Установленный и доступный MT5 (`terminal64.exe`), терминал запущен/авторизован.
- Python 3.10+ (для совместимости с MetaTrader5 рекомендуется 3.11).
- Экземпляр PostgreSQL.

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

Вспомогательные скрипты:
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

## ⚙️ Конфигурация
Скопируйте `.env.example` в `.env` и скорректируйте значения.

### Основные переменные
| Variable | Назначение |
|---|---|
| `DATABASE_URL` | Предпочтительный PostgreSQL DSN |
| `DATABASE_MT_URL` | Резервный DSN, если `DATABASE_URL` не задан |
| `DATABASE_QT_URL` | Второй резервный DSN |
| `MT5_PATH` | Путь к `terminal64.exe` (Wine или native) |
| `MT5_LOGIN` / `MT5_PASSWORD` / `MT5_SERVER` | Опционально, если сессия MT5 уже авторизована |
| `PORT` | Порт сервера (по умолчанию `8888`) |

### Необязательные переменные
- `FMP_API_KEY`, `ALPHAVANTAGE_API_KEY` для расширения новостных данных.
- `TRADING_ENABLED` (`0` по умолчанию, установите `1`, чтобы разрешить endpoints размещения ордеров).
- `TRADING_VOLUME` (объем по умолчанию для ручной торговли).
- `AUTO_FETCH`, `AUTO_FETCH_SYMBOL`, `AUTO_FETCH_TF`, `AUTO_FETCH_COUNT`, `AUTO_FETCH_SEC`.
- `PIN_DEFAULTS_TO_XAU_H1=1`, чтобы принудительно задать стартовые symbol/timeframe в UI.
- `LOG_LEVEL`, `LOG_BACKFILL`, а также предпочтения для аккаунтов/опроса через `/api/preferences` и окружение.

Примечания:
- `MT5_PATH` должен указывать на ваш `terminal64.exe` в Wine-префиксе, используемом скриптом установки MT5.
- Учетные данные MT5 можно не задавать, если сессия терминала уже активна; приложение попытается использовать эту сессию.

## 🚀 Использование

### Запуск сервера
```bash
python -m app.server
```

### Открытие UI
- Desktop UI: `http://localhost:8888/`
- Mobile UI: `http://localhost:8888/app`

### Типовой рабочий процесс
1. Получить бары из MT5 и сохранить их в Postgres.
2. Считать бары из БД для построения графика.
3. Запустить health/tech/news анализ.
4. Сгенерировать AI trade plan.
5. Исполнить или закрыть позиции в рамках защитных ограничений.

## 🔌 API Endpoints (практически)
- `GET /api/fetch?symbol=XAUUSD&tf=H1&count=500[&mode=inc|full][&persist=1]`
  - Получает данные из MT5 и делает upsert в БД.
  - Если `persist=1`, сервер сохраняет значения по умолчанию `last_symbol/last_tf/last_count`; bulk/background загрузки должны пропускать этот флаг, чтобы не перезаписывать выбор UI.
- `GET /api/fetch_bulk` — массовая/плановая загрузка данных.
- `GET /api/data?symbol=XAUUSD&tf=H1&limit=500` — чтение данных графика из БД.
- `GET /api/strategy/run?symbol=XAUUSD&tf=H1&fast=20&slow=50`
  - Выполняет расчет SMA(20/50) crossover и возвращает сигнал.
  - Важное замечание по реализации: размещение ордеров из этого endpoint на основе стратегии сейчас отключено в серверном коде; исполнение ордеров выполняется через trade endpoints.
- `POST /api/trade` — ручной Buy/Sell из UI, ограничено `TRADING_ENABLED`.
- `POST /api/trade/execute_plan` — исполняет сгенерированный план, включая pre-close и проверки stop-distance.
- `POST /api/close` — закрытие позиций (разрешено даже при `TRADING_ENABLED=0` для безопасности):
  - Текущий symbol: form body `symbol=...`; опционально `side=long|short|both`.
  - Все symbols: `?scope=all` и опционально `&side=...`.
  - Ответ включает `closed_count` и результаты по каждому ticket.
- `POST /api/close_tickets` — закрывает запрошенный поднабор по ticket.
- `GET /api/positions`, `GET /api/positions/all`.
- `GET /api/stl`, `POST /api/stl/compute`, `POST /api/stl/prune`, `POST /api/stl/prune_all`, `DELETE /api/stl/run/{id}`.
- `GET /api/news`, `POST /api/news/backfill_forex`, `POST /api/news/analyze`.
- `GET /api/health/freshness`, `GET /api/tech/freshness`, `GET|POST /api/health/run`, `GET /api/health/runs`.
- `POST /api/preferences` и связанные endpoints чтения настроек.
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
См. `sql/schema.sql`.

Ключевые моменты:
- Составной PK `(symbol, timeframe, ts)` в `ohlc_bars` предотвращает дубли баров.
- При загрузке используется `ON CONFLICT ... DO UPDATE`.
- Дополнительные таблицы поддерживают STL runs/components, preferences, news articles, health runs, account series, closed deals и связывание сигналов/планов ордеров.

## 🛡️ Торговые ограничения и безопасность
- Защита окружением: `TRADING_ENABLED=0` по умолчанию отключает размещение ордеров из endpoints ручного/планового исполнения.
- Поведение заголовка `Auto` в UI планирует проверки стратегии; оно не обходит торговые ограничители безопасности.
- Операции закрытия намеренно разрешены, даже когда торговля отключена.
- В потоках исполнения используются safe-max и взвешивание symbol/kind для ограничения риска.

## 📈 Переключатель STL Auto-Compute
- STL auto-compute управляется отдельно для каждой пары symbol x timeframe через переключатель `Auto STL` в STL-панели.
- По умолчанию OFF, чтобы уменьшить лаги UI на тяжелых/медленных контекстах.
- Когда ON, отсутствующий/устаревший STL может вычисляться автоматически; иначе используйте ручной пересчет.
- Состояние сохраняется через ключи `/api/preferences` вида `stl_auto_compute:SYMBOL:TF`, а также в local storage для более быстрого старта.

## 🧷 Запоминание последнего выбора
- Сервер сохраняет `last_symbol`, `last_tf`, `last_count` и подставляет значения по умолчанию в шаблоны.
- UI также сохраняет `last_symbol`/`last_tf` в `localStorage`.
- `/?reset=1` игнорирует сохраненные предпочтения при этой загрузке страницы.
- `PIN_DEFAULTS_TO_XAU_H1=1` может принудительно задать стартовые значения.

## 🤖 Контекст промпта AI Trade Plan
При запросе AI trade plan сервер гарантирует наличие свежих запусков Basic Health и Tech Snapshot для текущих symbol/timeframe (создает их при отсутствии), после чего собирает контекст промпта из:
- блока Basic health,
- блока Tech AI,
- блока live technical snapshot.

## 🧰 Заметки по разработке
- Основные runtime-зависимости: `tornado`, `asyncpg`, `MetaTrader5`, `numpy`, `python-dotenv`, `requests`, `httpx`, `statsmodels`, `openai`.
- Формальный набор автотестов пока не настроен; рабочий процесс опирается на smoke tests и ручную проверку UI.
- Рекомендуемые smoke tests:
  - `python scripts/test_mixed_ai.py`
  - `python scripts/test_fmp.py`
  - `python scripts/test_fmp_endpoints.py`
- Ручные проверки перед push:
  - синхронизация pan/zoom,
  - поведение STL overlay/period lines,
  - торговые контролы (включая безопасное поведение закрытия),
  - fallback-поведение панели новостей.

## 🧯 Устранение неполадок
| Симптом | Действие |
|---|---|
| MT5 initialize failed | Укажите `MT5_PATH` точно на `terminal64.exe`, затем хотя бы один раз запустите терминал вручную |
| MT5 login failed | Убедитесь, что `MT5_SERVER` в точности совпадает со строкой сервера в терминале, либо не передавайте учетные данные и переиспользуйте активную сессию |
| No data for symbol | Проверьте наименование символа у брокера и видимость в Market Watch (`XAUUSD`, `XAUUSD.a`, `GOLD` и т.д.) |
| Postgres connection issues | Проверьте `DATABASE_URL`, затем выполните `psql "$DATABASE_URL" -c 'select 1;'` |
| Slow or stale UI analytics | Выключите auto STL для тяжелых пар/TF и пересчитывайте вручную |

## 🛣️ Дорожная карта
- Расширить runtime-активы `i18n/` за пределы README-ориентированной многоязычной документации.
- Добавить формальные автотесты (API + integration + UI smoke automation).
- Улучшить packaging для деплоя и воспроизводимые профили окружения.
- Продолжить доработку валидации AI plan и защитных механизмов исполнения.

## 🤝 Вклад в проект
- Делайте небольшие, сфокусированные патчи.
- По возможности используйте понятные commit-префиксы (например: `UI: ...`, `Server: ...`, `References: ...`).
- Избегайте несвязанных форматирующих изменений.
- Для UI-изменений при необходимости добавляйте скриншоты/GIF.
- Перед PR запускайте smoke tests и проверку в локальном браузере.

## ❤️ Поддержка / Спонсорство
Ссылки на поддержку и спонсорство настроены в `.github/FUNDING.yml`:
- GitHub Sponsors: https://github.com/sponsors/lachlanchen
- Lazying.art: https://lazying.art
- Chat: https://chat.lazying.art
- OnlyIdeas: https://onlyideas.art

## 📚 Ссылки
- `references/ai-trader-overview.md`
- `references/database_setup_postgres.md`
- `references/mt5_python_setup_ubuntu.md`
- `references/mt4_vs_mt5.md`
- `references/llm_trading_system.md`
- `references/release_deploy.md`
- `references/pnl_debugging.md`

## 📄 Лицензия
В этом репозитории отсутствует файл `LICENSE` (по состоянию на 2026-02-28).

Допущение: условия лицензирования в репозитории пока не указаны; сохраняйте это примечание до добавления явного файла лицензии сопровождающими.
