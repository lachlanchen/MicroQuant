[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# MetaTrader QT - Inicio de trading cuantitativo (Filosofía de Micro Quant)

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Backend](https://img.shields.io/badge/Backend-Tornado-2d7cbf)
![Database](https://img.shields.io/badge/Database-PostgreSQL-336791?logo=postgresql&logoColor=white)
![Broker](https://img.shields.io/badge/Broker%20Bridge-MetaTrader5-1f6feb)
![UI](https://img.shields.io/badge/UI-Lightweight%20Charts%20%2B%20Chart.js-0ea5e9)
![Status](https://img.shields.io/badge/README-Expanded-success)
![GitHub%20Stars](https://img.shields.io/github/stars/lachlanchen/MicroQuant?style=for-the-badge&logo=github&logoColor=white&labelColor=0f172a&color=0ea5e9)
![GitHub%20Issues](https://img.shields.io/github/issues/lachlanchen/MicroQuant?style=for-the-badge&logo=github&logoColor=white&labelColor=0f172a&color=ef4444)

## 🎯 Resumen del proyecto

| Enfoque | Stack |
|---|---|
| Runtime | Tornado + asyncpg + WebSocket |
| Trading | MetaTrader5 + contexto en capas de AI/técnico/noticias |
| Almacenamiento | PostgreSQL con pipeline determinista de upsert |
| Despliegue | Activos PWA + UI desktop/móvil centrada en navegador |

## Tabla de contenidos
- [📸 Captura de pantalla](#-captura-de-pantalla)
- [🧭 Resumen](#-resumen)
- [🧠 Filosofía central](#-filosofia-central)
- [✨ Características](#-caracteristicas)
- [🗂️ Estructura del proyecto](#-estructura-del-proyecto)
- [✅ Requisitos previos](#-requisitos-previos)
- [🛠️ Instalación](#-instalacion)
- [⚙️ Configuración](#️-configuracion)
- [🚀 Uso](#-uso)
- [🔌 Endpoints de API (Práctico)](#-endpoints-de-api-práctico)
- [🧪 Ejemplos](#-ejemplos)
- [🗄️ Base de datos y esquema](#-base-de-datos-y-esquema)
- [🛡️ Controles de trading y seguridad](#️-controles-de-trading--seguridad)
- [📈 Interruptor de auto-cálculo STL](#-interruptor-de-auto-calculo-stl)
- [🧷 Recordar la última selección](#-recordar-la-ultima-seleccion)
- [🤖 Contexto del plan de trading con IA](#️-contexto-del-plan-de-trading-con-ia)
- [🧰 Notas de desarrollo](#-notas-de-desarrollo)
- [🧯 Solución de problemas](#-solucion-de-problemas)
- [🛣️ Hoja de ruta](#-hoja-de-ruta)
- [🤝 Contribuir](#-contribuir)
- [📚 Referencias](#-referencias)
- [❤️ Support](#️-support)
- [📄 Licencia](#-licencia)

## 📸 Captura de pantalla
![Micro Quant UI](figures/demos/micro-quant-ui.png)

[![DATA Source](https://img.shields.io/badge/Data_Source-RoboForex-0060ff?style=for-the-badge&labelColor=0a4eb3)](https://my.roboforex.com/en/?a=efx)

## 🧭 Resumen
Micro Quant no busca tableros vistosos, sino una capa repetible de lógica de trading: obtiene datos OHLC de MetaTrader 5, los persiste en PostgreSQL y evalúa decisiones sistemáticas mediante señales guiadas por IA en capas (noticias básicas, snapshot técnico, planes de trading y overlays STL). La UI refleja esa filosofía con conmutadores de alineación, cierres argumentados, preferencias persistentes y un panel de ejecución rico en datos, permitiendo que el servidor ejecute flujos periódicos o manuales con seguridad mientras supervisas logs y evidencias.

La landing page estática (Quant by Lazying.art) vive en `docs/` y se publica via GitHub Pages (`trade.lazying.art` a través de `docs/CNAME`). El repositorio también incluye referencias para prompts de AI Trade Plan, notas de integración y documentación operativa.

### En un vistazo
| Área | Qué hace |
|---|---|
| Datos | Extrae OHLC de MT5 y hace upsert a PostgreSQL |
| Analítica | Ejecuta flujos de salud/noticias/técnico y STL |
| Toma de decisiones | Construye planes de trading por IA desde contexto en capas |
| Ejecución | Ejecuta/controla flujos de trading con guardias de seguridad |
| UI | Vistas desktop/móvil con flujos de gráficos sincronizados |

## 🧠 Filosofía central
- **Cadena de verdad**: las comprobaciones básicas de noticias (texto + scores) y los snapshots técnicos (contexto técnico pesado + STL) alimentan un único plan de trading por símbolo/timeframe. Las ejecuciones periódicas automáticas y las ejecuciones manuales comparten la misma tubería y los mismos logs de razonamiento.
- **Ejecución orientada a alineación**: los conmutadores Accept-Tech/Hold-Neutral, el switch de ignorar básicos y los wrappers de cierre parcial garantizan que la lógica técnica se siga de forma intencionada, que las posiciones opuestas se cierren antes de abrir nuevas entradas cuando haga falta y que se minimicen salidas innecesarias.
- **Datos inmutables**: cada ingesta escribe en Postgres con higiene de `ON CONFLICT`, mientras `/api/data` lee series saneadas para la UI. Las preferencias (`auto` settings, `close_fraction`, conmutadores hide-tech, auto-cálculo STL) persisten por `/api/preferences`.
- **Trading con seguridad primero**: `TRADING_ENABLED` y `safe_max` aplican permisos para modo manual/automático. `/api/close` y los runners periódicos registran motivos de cierre (neutral técnico, desalineación, etc.) para trazabilidad.

## ✨ Características
- Ingesta OHLC de MT5 a Postgres (`/api/fetch`, `/api/fetch_bulk`).
- UI de charts en `/` (desktop) y `/app` (móvil), con uso de Chart.js + Lightweight Charts en templates.
- Flujos de descomposición STL (`/api/stl`, `/api/stl/compute`, endpoints de poda/eliminación).
- Ingesta y análisis de noticias (`/api/news`, `/api/news/backfill_forex`, `/api/news/analyze`).
- Orquestación de flujo AI (`/api/health/run`, `/api/health/runs`, `/api/ai/trade_plan`).
- Ejecución manual de trades (`/api/trade`, `/api/trade/execute_plan`) protegida por `TRADING_ENABLED`.
- Operaciones de riesgo de posiciones (`/api/positions*`, `/api/close`, `/api/close_tickets`) con cierres permitidos bajo comportamiento de seguridad explícito.
- Stream de actualizaciones WebSocket en `/ws/updates` para hints en tiempo real y señales de refresco.
- Activos PWA/estáticos para dashboard instalable.

## 🗂️ Estructura del proyecto
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

## ✅ Requisitos previos
- Ubuntu/Linux o Windows con acceso a terminal.
- MetaTrader 5 instalado (`terminal64.exe`) y con sesión iniciada cuando se requiera.
- Python 3.10+ (Python 3.11 recomendado por mayor compatibilidad con las wheels de MetaTrader5).
- Instancia de PostgreSQL accesible desde el servidor de app.
- Claves de API opcionales para proveedores de noticias:
  - FMP
  - Alpha Vantage

## 🛠️ Instalación

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

## ⚙️ Configuración
Copia `.env.example` a `.env` y ajusta los valores.

### Variables principales
| Variable | Propósito |
|---|---|
| `DATABASE_URL` | DSN preferido de PostgreSQL |
| `DATABASE_MT_URL` | DSN alterno si no existe `DATABASE_URL` |
| `DATABASE_QT_URL` | DSN de respaldo secundario |
| `MT5_PATH` | Ruta a `terminal64.exe` (Wine o nativo) |
| `MT5_LOGIN` / `MT5_PASSWORD` / `MT5_SERVER` | Opcionales si la sesión del terminal MT5 ya está iniciada |
| `PORT` | Puerto del servidor (por defecto `8888`) |

### Variables opcionales
- `FMP_API_KEY`, `ALPHAVANTAGE_API_KEY` para enriquecimiento de noticias.
- `TRADING_ENABLED` (`0` por defecto, usa `1` para habilitar endpoints de envío de órdenes).
- `TRADING_VOLUME` (volumen manual por defecto).
- `AUTO_FETCH`, `AUTO_FETCH_SYMBOL`, `AUTO_FETCH_TF`, `AUTO_FETCH_COUNT`, `AUTO_FETCH_SEC`.
- `PIN_DEFAULTS_TO_XAU_H1=1` para forzar símbolo/timeframe por defecto al iniciar la UI.
- `LOG_LEVEL`, `LOG_BACKFILL`, además de preferencias de cuenta y polling vía `/api/preferences` y variables de entorno.

Notas:
- `MT5_PATH` debe apuntar a tu `terminal64.exe` dentro del prefijo Wine usado por tu instalación de MT5.
- Puedes omitir credenciales de MT5 cuando la sesión del terminal ya esté iniciada; la app intentará reutilizar esa sesión.

## 🚀 Uso

### Iniciar servidor
```bash
python -m app.server
```

### Abrir UI
- UI desktop: `http://localhost:8888/`
- UI móvil: `http://localhost:8888/app`

### URLs clave
| Superficie | URL | Propósito |
|---|---|---|
| Desktop | `http://localhost:8888/` | Gráfico de velas y controles de flujo desktop |
| Móvil | `http://localhost:8888/app` | Layout táctil con controles compactos |
| Health API | `http://localhost:8888/api/health/freshness` | Comprobación rápida de datos + estado del servicio |

### Flujo típico
1. Obtiene barras desde MT5 y las persiste en Postgres.
2. Lee barras desde la BD para graficar.
3. Ejecuta análisis de salud/técnico/noticias.
4. Genera el plan de trading AI.
5. Ejecuta o cierra posiciones bajo guardias de seguridad.

## 🔌 Endpoints de API (Práctico)
- `GET /api/fetch?symbol=XAUUSD&tf=H1&count=500[&mode=inc|full][&persist=1]`
  - Obtiene datos desde MT5 y hace upsert en BD.
  - Si `persist=1`, el servidor guarda por defecto `last_symbol/last_tf/last_count`; los fetch masivos en segundo plano deberían omitirlo para no sobreescribir elecciones de UI.
- `GET /api/fetch_bulk` — ingesta masiva/schedulada.
- `GET /api/data?symbol=XAUUSD&tf=H1&limit=500` — lee datos de chart desde BD.
- `GET /api/strategy/run?symbol=XAUUSD&tf=H1&fast=20&slow=50`
  - Ejecuta el cruce SMA(20/50) y devuelve payload de señal.
  - Nota clave: el envío de órdenes impulsado por estrategia desde este endpoint está deshabilitado actualmente en el código del servidor; la ejecución se controla a través de endpoints de trading.
- `POST /api/trade` — Buy/Sell manual desde UI, protegido por `TRADING_ENABLED`.
- `POST /api/trade/execute_plan` — ejecuta un plan generado, incluyendo pre-cierre y comprobaciones de distancia de stop.
- `POST /api/close` — cierra posiciones (permitido incluso con `TRADING_ENABLED=0` por seguridad):
  - Símbolo actual: body `symbol=...`; `side=long|short|both` opcional.
  - Todos los símbolos: `?scope=all` y `&side=...` opcional.
  - La respuesta incluye `closed_count` y resultados por ticket.
- `POST /api/close_tickets` — cierra un subconjunto solicitado por ticket.
- `GET /api/positions`, `GET /api/positions/all`.
- `GET /api/stl`, `POST /api/stl/compute`, `POST /api/stl/prune`, `POST /api/stl/prune_all`, `DELETE /api/stl/run/{id}`.
- `GET /api/news`, `POST /api/news/backfill_forex`, `POST /api/news/analyze`.
- `GET /api/health/freshness`, `GET /api/tech/freshness`, `GET|POST /api/health/run`, `GET /api/health/runs`.
- `POST /api/preferences` y recuperación de preferencias relacionada.
- `GET /api/ai/trade_plan`.
- `GET /api/accounts`, `GET /api/account/current`, `POST /api/account/login`.
- `GET /ws/updates`.

## 🧪 Ejemplos
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

## 🗄️ Base de datos y esquema
Ver `sql/schema.sql`.

Puntos clave:
- La PK compuesta `(symbol, timeframe, ts)` en `ohlc_bars` evita barras duplicadas.
- La ingesta usa `ON CONFLICT ... DO UPDATE`.
- Hay tablas extra para corridas STL/componentes, preferencias, artículos de noticias, health runs, series de cuentas, operaciones cerradas y vínculos signal/order-plan.

## 🛡️ Controles de trading y seguridad
- Guardia de entorno: `TRADING_ENABLED=0` por defecto desactiva el placement de órdenes desde endpoints manuales y de ejecución de plan.
- El estado `Auto` del header en la UI agenda chequeos de estrategia; no evita los gates de seguridad del trading.
- Las operaciones de cierre están permitidas de forma explícita incluso con trading deshabilitado.
- Safe-max y ponderación por símbolo/tipo se usan en flujos de ejecución para limitar exposición.

## 📈 Interruptor de auto-cálculo STL
- El auto-cálculo STL se controla por símbolo x timeframe mediante el switch `Auto STL` en el panel STL.
- Por defecto está APAGADO para reducir latencia de UI en contextos grandes/lentos.
- Con ON, STL faltante o desactualizado puede calcularse automáticamente; en OFF usa controles de recálculo manual.
- El estado persiste por clave en `/api/preferences` como `stl_auto_compute:SYMBOL:TF` y también en localStorage para arranques más rápidos.

## 🧷 Recordar la última selección
- El servidor persiste `last_symbol`, `last_tf`, `last_count` e inyecta defaults en templates.
- La UI también guarda `last_symbol`/`last_tf` en `localStorage`.
- `/?reset=1` ignora preferencias almacenadas para esa carga de página.
- `PIN_DEFAULTS_TO_XAU_H1=1` puede forzar defaults de arranque.

## 🤖 Contexto del plan de trading con IA
Al solicitar un plan de trading AI, el servidor garantiza que existan ejecuciones frescas de Basic Health y Tech Snapshot para el símbolo/timeframe actual (creándolas si faltan), luego construye el contexto del prompt a partir de:
- Bloque de salud básica,
- Bloque técnico de IA,
- Bloque de snapshot técnico en vivo.

## 🧰 Notas de desarrollo
- Dependencias de runtime principales: `tornado`, `asyncpg`, `MetaTrader5`, `numpy`, `python-dotenv`, `requests`, `httpx`, `statsmodels`, `openai`.
- Actualmente no existe una suite automatizada formal; los smoke tests y la validación manual de UI son el flujo activo.
- Smoke tests recomendados:
  - `python scripts/test_mixed_ai.py`
  - `python scripts/test_fmp.py`
  - `python scripts/test_fmp_endpoints.py`
- Comprobaciones manuales antes de release:
  - sincronización pan/zoom,
  - comportamiento de STL overlay/líneas de período,
  - controles de trading (incluyendo comportamiento de seguridad de cierre),
  - fallback del panel de noticias.

## 🧯 Solución de problemas
| Síntoma | Acción |
|---|---|
| Error de inicialización MT5 | Configura `MT5_PATH` al `terminal64.exe` exacto y ejecuta el terminal manualmente al menos una vez |
| Error de login MT5 | Asegúrate de que `MT5_SERVER` coincida exactamente con la cadena de servidor del terminal, u omite credenciales y reutiliza una sesión activa |
| Sin datos para el símbolo | Verifica naming del símbolo del broker y visibilidad en Market Watch (`XAUUSD`, `XAUUSD.a`, `GOLD`, etc.) |
| Problemas de conexión a Postgres | Verifica `DATABASE_URL`, luego ejecuta `psql "$DATABASE_URL" -c 'select 1;'` |
| Analítica UI lenta u obsoleta | Desactiva auto STL en pares/TF pesados y recalcúlalo manualmente |

## 🛣️ Hoja de ruta
- Expandir assets de runtime de `i18n/` más allá de docs multilingües basados en README.
- Añadir pruebas automatizadas formales (API + integración + UI smoke automation).
- Mejorar empaquetado de despliegue y perfiles de entorno reproducibles.
- Seguir refinando validación de planes AI y salvaguardas de ejecución.

## 🤝 Contribuir
- Mantén los cambios pequeños y acotados.
- Usa prefijos claros de commit donde aplique (por ejemplo: `UI: ...`, `Server: ...`, `References: ...`).
- Evita ruido de formato no relacionado.
- Incluye capturas/GIFs para cambios de UI cuando sea relevante.
- Ejecuta smoke tests y comprobaciones en navegador local antes de PR.

## 📚 Referencias
- `references/ai-trader-overview.md`
- `references/database_setup_postgres.md`
- `references/mt5_python_setup_ubuntu.md`
- `references/mt4_vs_mt5.md`
- `references/llm_trading_system.md`
- `references/release_deploy.md`
- `references/pnl_debugging.md`

## 📄 Licencia
No existe un archivo `LICENSE` en este repositorio a fecha 2026-02-28.

Se asume que los términos de licencia siguen sin definir explícitamente en el repositorio; mantén esta nota hasta que el mantenimiento añada un archivo de licencia explícito.


## ❤️ Support

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://camo.githubusercontent.com/24a4914f0b42c6f435f9e101621f1e52535b02c225764b2f6cc99416926004b7/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f446f6e6174652d4c617a79696e674172742d3045413545393f7374796c653d666f722d7468652d6261646765266c6f676f3d6b6f2d6669266c6f676f436f6c6f723d7768697465)](https://chat.lazying.art/donate) | [![PayPal](https://camo.githubusercontent.com/d0f57e8b016517a4b06961b24d0ca87d62fdba16e18bbdb6aba28e978dc0ea21/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f50617950616c2d526f6e677a686f754368656e2d3030343537433f7374796c653d666f722d7468652d6261646765266c6f676f3d70617970616c266c6f676f436f6c6f723d7768697465)](https://paypal.me/RongzhouChen) | [![Stripe](https://camo.githubusercontent.com/1152dfe04b6943afe3a8d2953676749603fb9f95e24088c92c97a01a897b4942/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f5374726970652d446f6e6174652d3633354246463f7374796c653d666f722d7468652d6261646765266c6f676f3d737472697065266c6f676f436f6c6f723d7768697465)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |
