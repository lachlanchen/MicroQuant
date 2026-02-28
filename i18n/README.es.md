[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


<p align="center">
  <img src="https://raw.githubusercontent.com/lachlanchen/lachlanchen/main/logos/banner.png" alt="LazyingArt banner" />
</p>

# MetaTrader QT - Starter de Trading Cuantitativo (Filosofía Micro Quant)

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Backend](https://img.shields.io/badge/Backend-Tornado-2d7cbf)
![Database](https://img.shields.io/badge/Database-PostgreSQL-336791?logo=postgresql&logoColor=white)
![Broker](https://img.shields.io/badge/Broker%20Bridge-MetaTrader5-1f6feb)
![UI](https://img.shields.io/badge/UI-Lightweight%20Charts%20%2B%20Chart.js-0ea5e9)
![Status](https://img.shields.io/badge/README-Expanded-success)

## 📸 Captura de pantalla
![Micro Quant UI](../figures/demos/micro-quant-ui.png)

<p align="center">
  <a href="https://my.roboforex.com/en/?a=efx" target="_blank" rel="noopener noreferrer">
    <button style="padding: 0.65rem 1.25rem; font-weight: 600; border-radius: 999px; border: none; color: white; background: #0060ff; cursor: pointer;">
      DATA Source
    </button>
  </a>
</p>

## 🧭 Resumen
Micro Quant se trata menos de paneles vistosos y más de una pila de lógica de trading repetible: extrae datos OHLC desde MetaTrader 5, los persiste en Postgres y evalúa decisiones sistemáticas mediante señales guiadas por IA en capas (noticias básicas, snapshot técnico, planes de trading y overlays STL). La UI refleja esa filosofía con toggles de alineación, cierres razonados, preferencias persistentes y un panel de ejecución rico en datos para que el servidor pueda ejecutar flujos de trading periódicos o modales mientras inspeccionas logs y evidencia.

La landing estática (Quant by Lazying.art) vive en `docs/` y se publica con GitHub Pages (`trade.lazying.art` vía `docs/CNAME`). El repositorio también incluye referencias para prompts de AI Trade Plan, notas de integración y documentación operativa.

### Vista rápida
| Área | Qué hace |
|---|---|
| Datos | Extrae OHLC de MT5 y hace upsert en PostgreSQL |
| Analítica | Ejecuta flujos de health/news/tech y STL |
| Toma de decisiones | Construye planes de trading con IA a partir de contexto en capas |
| Ejecución | Ejecuta/controla flujos de trading detrás de salvaguardas |
| UI | Vistas desktop/móvil con flujos de gráficos sincronizados |

## 🧠 Filosofía central
- **Cadena de verdad**: las validaciones básicas de noticias (texto + scores) y los snapshots de Tech (contexto técnico amplio + STL) alimentan un único plan de trading IA por símbolo/timeframe. Las ejecuciones automáticas periódicas y las ejecuciones manuales por modal comparten el mismo pipeline y logs de razonamiento.
- **Ejecución con prioridad en la alineación**: los toggles Accept-Tech/Hold-Neutral, el switch ignore-basics y los wrappers de partial-close garantizan que Tech se siga de forma intencional, que se cierren posiciones opuestas antes de nuevas entradas cuando sea necesario y que se minimicen salidas innecesarias.
- **Datos inmutables**: cada fetch escribe en Postgres con higiene `ON CONFLICT`, mientras que `/api/data` lee series saneadas para la UI. Las preferencias (volúmenes auto, `close_fraction`, toggles hide-tech, STL auto-compute) persisten mediante `/api/preferences`.
- **Trading con seguridad primero**: `TRADING_ENABLED` y `safe_max` aplican permisos para trading manual/automático. `/api/close` y los runners periódicos pueden registrar motivos de cierre (tech neutral, desalineación, etc.) para trazabilidad.

## ✨ Funcionalidades
- Ingesta OHLC de MT5 a Postgres (`/api/fetch`, `/api/fetch_bulk`).
- UI de gráficos en `/` (desktop) y `/app` (móvil), con uso de Chart.js + Lightweight Charts en templates.
- Flujos de descomposición STL (`/api/stl`, `/api/stl/compute`, endpoints prune/delete).
- Ingesta y análisis de noticias (`/api/news`, `/api/news/backfill_forex`, `/api/news/analyze`).
- Orquestación de workflows de IA (`/api/health/run`, `/api/health/runs`, `/api/ai/trade_plan`).
- Ejecución manual de operaciones (`/api/trade`, `/api/trade/execute_plan`) protegida por `TRADING_ENABLED`.
- Operaciones de riesgo sobre posiciones (`/api/positions*`, `/api/close`, `/api/close_tickets`) con cierres permitidos por seguridad.
- Stream de actualizaciones WebSocket en `/ws/updates`.

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
├── i18n/                        # Present (currently empty)
├── .github/FUNDING.yml          # Sponsor/support metadata
└── README.md + README.*.md      # Canonical + multilingual docs
```

## ✅ Requisitos previos
- Ubuntu/Linux o Windows.
- MT5 instalado y accesible (`terminal64.exe`), con el terminal abierto y con sesión iniciada.
- Python 3.10+ (3.11 recomendado para compatibilidad con MetaTrader5).
- Instancia de PostgreSQL.

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

Scripts auxiliares:
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

## ⚙️ Configuración
Copia `.env.example` a `.env` y ajusta los valores.

### Variables principales
| Variable | Purpose |
|---|---|
| `DATABASE_URL` | Preferred PostgreSQL DSN |
| `DATABASE_MT_URL` | Fallback DSN if `DATABASE_URL` unset |
| `DATABASE_QT_URL` | Secondary fallback DSN |
| `MT5_PATH` | Path to `terminal64.exe` (Wine or native) |
| `MT5_LOGIN` / `MT5_PASSWORD` / `MT5_SERVER` | Optional if MT5 terminal session is already logged in |
| `PORT` | Server port (default `8888`) |

### Variables opcionales
- `FMP_API_KEY`, `ALPHAVANTAGE_API_KEY` para enriquecer noticias.
- `TRADING_ENABLED` (por defecto `0`; usa `1` para habilitar endpoints de colocación de órdenes).
- `TRADING_VOLUME` (volumen manual por defecto).
- `AUTO_FETCH`, `AUTO_FETCH_SYMBOL`, `AUTO_FETCH_TF`, `AUTO_FETCH_COUNT`, `AUTO_FETCH_SEC`.
- `PIN_DEFAULTS_TO_XAU_H1=1` para forzar símbolo/timeframe de inicio en la UI.
- `LOG_LEVEL`, `LOG_BACKFILL`, más preferencias de cuenta/poll vía `/api/preferences` y entorno.

Notas:
- `MT5_PATH` debe apuntar a tu `terminal64.exe` dentro del Wine prefix usado por tu script de instalación de MT5.
- Puedes omitir credenciales de MT5 cuando la sesión del terminal ya está iniciada; la app intentará reutilizar esa sesión.

## 🚀 Uso

### Iniciar servidor
```bash
python -m app.server
```

### Abrir UI
- UI de escritorio: `http://localhost:8888/`
- UI móvil: `http://localhost:8888/app`

### Flujo común
1. Extraer velas desde MT5 y persistirlas en Postgres.
2. Leer velas desde DB para graficar.
3. Ejecutar análisis de health/tech/news.
4. Generar AI trade plan.
5. Ejecutar o cerrar posiciones bajo salvaguardas de seguridad.

## 🔌 Endpoints API (práctico)
- `GET /api/fetch?symbol=XAUUSD&tf=H1&count=500[&mode=inc|full][&persist=1]`
  - Extrae desde MT5 y hace upsert en DB.
  - Si `persist=1`, el servidor guarda los valores por defecto `last_symbol/last_tf/last_count`; en fetches bulk/background debe omitirse para no sobreescribir las elecciones de UI.
- `GET /api/fetch_bulk` — ingesta bulk/programada.
- `GET /api/data?symbol=XAUUSD&tf=H1&limit=500` — lee datos de gráfico desde DB.
- `GET /api/strategy/run?symbol=XAUUSD&tf=H1&fast=20&slow=50`
  - Ejecuta cruce SMA(20/50) y devuelve el payload de señal.
  - Nota importante de implementación: la colocación de órdenes desde este endpoint impulsado por estrategia está deshabilitada actualmente en el código del servidor; la ejecución de órdenes se maneja mediante endpoints de trade.
- `POST /api/trade` — Buy/Sell manual desde UI, protegido por `TRADING_ENABLED`.
- `POST /api/trade/execute_plan` — ejecuta un plan generado, incluye verificaciones de pre-close y stop-distance.
- `POST /api/close` — cierra posiciones (permitido incluso con `TRADING_ENABLED=0` por seguridad):
  - Símbolo actual: body de formulario `symbol=...`; opcional `side=long|short|both`.
  - Todos los símbolos: `?scope=all` y opcional `&side=...`.
  - La respuesta incluye `closed_count` y resultados por ticket.
- `POST /api/close_tickets` — cierra un subconjunto solicitado por ticket.
- `GET /api/positions`, `GET /api/positions/all`.
- `GET /api/stl`, `POST /api/stl/compute`, `POST /api/stl/prune`, `POST /api/stl/prune_all`, `DELETE /api/stl/run/{id}`.
- `GET /api/news`, `POST /api/news/backfill_forex`, `POST /api/news/analyze`.
- `GET /api/health/freshness`, `GET /api/tech/freshness`, `GET|POST /api/health/run`, `GET /api/health/runs`.
- `POST /api/preferences` y recuperación de preferencias relacionadas.
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
Consulta `sql/schema.sql`.

Puntos clave:
- La PK compuesta `(symbol, timeframe, ts)` en `ohlc_bars` evita barras duplicadas.
- La ingesta usa `ON CONFLICT ... DO UPDATE`.
- Tablas adicionales soportan ejecuciones/componentes STL, preferencias, artículos de noticias, ejecuciones de health, series de cuentas, deals cerrados y vinculación de señales con planes/órdenes.

## 🛡️ Controles de trading y seguridad
- Guardia por entorno: `TRADING_ENABLED=0` por defecto deshabilita la colocación de órdenes desde endpoints de ejecución manual/plan.
- El comportamiento del encabezado `Auto` en UI programa chequeos de estrategia; no omite las barreras de seguridad de trading.
- Las operaciones de cierre se permiten de forma intencional incluso cuando el trading está deshabilitado.
- En los flujos de ejecución se usan safe-max y ponderación por símbolo/tipo para limitar exposición.

## 📈 Toggle STL Auto-Compute
- El auto-cálculo STL se controla por símbolo x timeframe mediante el switch `Auto STL` en el panel STL.
- El valor por defecto es OFF para reducir lag de UI en contextos pesados/lentos.
- Cuando está ON, STL faltante/obsoleto puede calcularse automáticamente; si no, usa los controles de recálculo manual.
- El estado persiste vía claves de `/api/preferences` como `stl_auto_compute:SYMBOL:TF` y también en local storage para un arranque más rápido.

## 🧷 Recordar última selección
- El servidor persiste `last_symbol`, `last_tf`, `last_count` e inyecta valores por defecto en templates.
- La UI también guarda `last_symbol`/`last_tf` en `localStorage`.
- `/?reset=1` ignora preferencias guardadas para esa carga de página.
- `PIN_DEFAULTS_TO_XAU_H1=1` puede forzar valores de inicio.

## 🤖 Contexto del prompt AI Trade Plan
Al solicitar un AI trade plan, el servidor garantiza que existan ejecuciones recientes de Basic Health y Tech Snapshot para el símbolo/timeframe actual (creándolas si faltan), y luego arma el contexto del prompt desde:
- Basic health block,
- Tech AI block,
- Live technical snapshot block.

## 🧰 Notas de desarrollo
- Dependencias principales de runtime: `tornado`, `asyncpg`, `MetaTrader5`, `numpy`, `python-dotenv`, `requests`, `httpx`, `statsmodels`, `openai`.
- Actualmente no hay una suite formal de tests automatizados; el flujo activo se basa en smoke tests y validación manual de UI.
- Smoke tests recomendados:
  - `python scripts/test_mixed_ai.py`
  - `python scripts/test_fmp.py`
  - `python scripts/test_fmp_endpoints.py`
- Validaciones manuales antes de hacer push:
  - sincronización pan/zoom,
  - comportamiento de STL overlay/period lines,
  - controles de trading (incluyendo comportamiento de cierre por seguridad),
  - fallback del panel de noticias.

## 🧯 Solución de problemas
| Síntoma | Acción |
|---|---|
| MT5 initialize failed | Set `MT5_PATH` to exact `terminal64.exe`, then run terminal manually at least once |
| MT5 login failed | Ensure `MT5_SERVER` exactly matches terminal server string, or omit credentials and reuse an active session |
| No data for symbol | Verify broker symbol naming and Market Watch visibility (`XAUUSD`, `XAUUSD.a`, `GOLD`, etc.) |
| Postgres connection issues | Verify `DATABASE_URL`, then run `psql "$DATABASE_URL" -c 'select 1;'` |
| Slow or stale UI analytics | Disable auto STL on heavy pairs/TFs and recalc manually |

## 🛣️ Hoja de ruta
- Expandir assets de runtime `i18n/` más allá de documentación README multilingüe.
- Añadir tests automatizados formales (API + integración + automatización de smoke de UI).
- Mejorar packaging de despliegue y perfiles de entorno reproducibles.
- Seguir refinando la validación de planes IA y las salvaguardas de ejecución.

## 🤝 Contribuir
- Mantén los cambios pequeños y acotados.
- Usa prefijos de commit claros cuando aplique (por ejemplo: `UI: ...`, `Server: ...`, `References: ...`).
- Evita churn de formato no relacionado.
- Incluye capturas/GIFs para cambios de UI cuando sea relevante.
- Ejecuta smoke tests y comprobaciones locales en navegador antes de abrir PR.

## ❤️ Soporte / Sponsor
Los enlaces de sponsor y soporte están configurados en `.github/FUNDING.yml`:
- GitHub Sponsors: https://github.com/sponsors/lachlanchen
- Lazying.art: https://lazying.art
- Chat: https://chat.lazying.art
- OnlyIdeas: https://onlyideas.art

## 📚 Referencias
- `references/ai-trader-overview.md`
- `references/database_setup_postgres.md`
- `references/mt5_python_setup_ubuntu.md`
- `references/mt4_vs_mt5.md`
- `references/llm_trading_system.md`
- `references/release_deploy.md`
- `references/pnl_debugging.md`

## 📄 Licencia
No hay un archivo `LICENSE` en este repositorio a fecha de 2026-02-28.

Suposición: los términos de licencia actualmente no están especificados dentro del repositorio; conserva esta nota hasta que los maintainers agreguen un archivo de licencia explícito.
