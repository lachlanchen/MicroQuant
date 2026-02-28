[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# MetaTrader QT - 정량 트레이딩 스타터 (Micro Quant Philosophy)

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Backend](https://img.shields.io/badge/Backend-Tornado-2d7cbf)
![Database](https://img.shields.io/badge/Database-PostgreSQL-336791?logo=postgresql&logoColor=white)
![Broker](https://img.shields.io/badge/Broker%20Bridge-MetaTrader5-1f6feb)
![UI](https://img.shields.io/badge/UI-Lightweight%20Charts%20%2B%20Chart.js-0ea5e9)
![Status](https://img.shields.io/badge/README-Expanded-success)
![GitHub%20Stars](https://img.shields.io/github/stars/lachlanchen/MicroQuant?style=for-the-badge&logo=github&logoColor=white&labelColor=0f172a&color=0ea5e9)
![GitHub%20Issues](https://img.shields.io/github/issues/lachlanchen/MicroQuant?style=for-the-badge&logo=github&logoColor=white&labelColor=0f172a&color=ef4444)

## 🎯 프로젝트 스냅샷

| 초점 | 스택 |
|---|---|
| 런타임 | Tornado + asyncpg + WebSocket |
| 트레이딩 | MetaTrader5 + 계층형 AI/기술/뉴스 컨텍스트 |
| 저장소 | ON CONFLICT 기반 업서트 파이프라인이 적용된 PostgreSQL |
| 배포 | PWA 자산 + 브라우저 우선 데스크톱/모바일 UI |

## 목차
- [스크린샷](#-screenshot)
- [개요](#-overview)
- [핵심 철학](#-core-philosophy)
- [기능](#-features)
- [프로젝트 구조](#-project-structure)
- [사전 요구 사항](#-prerequisites)
- [설치](#-installation)
- [설정](#️-configuration)
- [사용법](#-usage)
- [API 엔드포인트](#-api-endpoints-practical)
- [예시](#-examples)
- [데이터베이스 및 스키마](#-database--schema)
- [거래 제어 및 안전성](#️-trading-controls--safety)
- [STL 자동 계산 토글](#-stl-auto-compute-toggle)
- [마지막 선택 기억하기](#-remembering-last-selection)
- [AI 트레이드 플랜 프롬프트 컨텍스트](#️-ai-trade-plan-prompt-context)
- [개발 노트](#-development-notes)
- [문제 해결](#-troubleshooting)
- [로드맵](#-roadmap)
- [기여](#-contributing)
- [참고 자료](#-references)
- [지원](#️-support)
- [라이선스](#-license)

## 📸 스크린샷
![Micro Quant UI](figures/demos/micro-quant-ui.png)

[![DATA Source](https://img.shields.io/badge/Data_Source-RoboForex-0060ff?style=for-the-badge&labelColor=0a4eb3)](https://my.roboforex.com/en/?a=efx)

## 🧭 개요
Micro Quant는 화려한 대시보드보다 반복 가능한 거래 로직 스택에 더 초점을 둡니다. MetaTrader 5에서 OHLC 데이터를 가져와 PostgreSQL에 영속 저장하고, 계층형 AI 기반 신호(기본 뉴스, 기술 스냅샷, 트레이드 플랜, STL 오버레이)를 통해 체계적인 매매 판단을 수행합니다. UI는 이 철학을 반영해 정렬 토글, 근거 기반 청산, 저장된 선호도, 데이터 중심 실행 패널을 제공하며, 사용자는 로그와 근거를 확인하면서 서버가 주기 실행 또는 모달 실행 플로우를 안정적으로 실행하도록 확인할 수 있습니다.

정적 랜딩 페이지(`Quant by Lazying.art`)는 `docs/` 하위에 있으며 GitHub Pages(`trade.lazying.art` via `docs/CNAME`)로 배포됩니다. 이 저장소에는 AI 트레이드 플랜 프롬프트, 통합 노트, 운영 문서가 함께 포함되어 있습니다.

### 한눈에 보기
| 영역 | 역할 |
|---|---|
| 데이터 | MT5 OHLC를 가져와 PostgreSQL에 업서트 |
| 분석 | health/news/tech 워크플로우와 STL 처리 실행 |
| 의사결정 | 계층화된 컨텍스트로 AI 트레이드 플랜 생성 |
| 실행 | 안전 가드 아래에서 거래 플로우 실행/제어 |
| UI | 동기화된 차트 워크플로우의 데스크톱/모바일 화면 |

## 🧠 핵심 철학
- **진실의 사슬(Chain of truth)**: 기본 뉴스 점검(텍스트 + 점수)과 기술 스냅샷(풍부한 기술적 컨텍스트 + STL) 결과를 바탕으로 심볼/타임프레임 당 하나의 AI 트레이드 플랜을 생성합니다. 주기적 자동 실행과 수동 모달 실행은 동일한 파이프라인과 같은 추론 로그를 공유합니다.
- **정렬 우선 실행**: Accept-Tech/Hold-Neutral 토글, ignore-basics 스위치, 부분 청산 래퍼로 기술 신호를 의도적으로 준수하고, 필요 시 반대 포지션을 새 진입 전에 먼저 청산하며, 불필요한 청산을 줄입니다.
- **불변 데이터**: 모든 데이터 수집은 `ON CONFLICT` 정합성을 유지하며 Postgres에 기록되고, UI는 `/api/data`에서 정제된 시계열을 읽습니다. 선호도(`auto` 설정, `close_fraction`, tech 숨김 토글, STL 자동 계산)는 `/api/preferences`로 영속화됩니다.
- **안전 우선 트레이딩**: `TRADING_ENABLED`와 `safe_max`가 수동/자동 권한 제어를 담당합니다. `/api/close` 및 주기 실행기는 추적성 확보를 위해 청산 사유(tech 중립, 정렬 불일치 등)를 로그에 남깁니다.

## ✨ 기능
- MT5 OHLC를 Postgres로 수집 (`/api/fetch`, `/api/fetch_bulk`).
- 템플릿에서 Chart.js + Lightweight Charts를 사용하는 차트 UI: `/`(데스크톱), `/app`(모바일).
- STL 분해 워크플로우 (`/api/stl`, `/api/stl/compute`, prune/delete 엔드포인트).
- 뉴스 수집/분석 (`/api/news`, `/api/news/backfill_forex`, `/api/news/analyze`).
- AI 워크플로 orchestration (`/api/health/run`, `/api/health/runs`, `/api/ai/trade_plan`).
- 수동 거래 실행 (`/api/trade`, `/api/trade/execute_plan`)은 `TRADING_ENABLED`로 제어됩니다.
- 포지션 리스크 작업 (`/api/positions*`, `/api/close`, `/api/close_tickets`)은 명시된 안전 동작 하에서만 청산이 허용됩니다.
- 실시간 힌트와 갱신 신호를 위한 WebSocket 스트림 `/ws/updates`.
- 설치형 대시보드 사용을 위한 PWA 정적 자산.

## 🗂️ 프로젝트 구조
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

## ✅ 사전 요구 사항
- Ubuntu/Linux 또는 터미널 접근 가능한 Windows.
- MetaTrader 5 설치됨(`terminal64.exe`) 및 필요 시 로그인.
- Python 3.10+ (MetaTrader5 휠 호환성 측면에서 Python 3.11 권장).
- 앱 서버에서 접근 가능한 PostgreSQL 인스턴스.
- 뉴스 제공자용 선택적 API 키:
  - FMP
  - Alpha Vantage

## 🛠️ 설치

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

도움말 스크립트:
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

## ⚙️ 설정
`.env.example`을 `.env`로 복사한 후 값들을 조정합니다.

### 핵심 환경 변수
| 변수 | 용도 |
|---|---|
| `DATABASE_URL` | 우선 사용 PostgreSQL DSN |
| `DATABASE_MT_URL` | `DATABASE_URL`이 비어 있을 때 대체 DSN |
| `DATABASE_QT_URL` | 두 번째 대체 DSN |
| `MT5_PATH` | `terminal64.exe` 경로 (Wine 또는 네이티브) |
| `MT5_LOGIN` / `MT5_PASSWORD` / `MT5_SERVER` | MT5 터미널 세션이 이미 로그인되어 있으면 생략 가능 |
| `PORT` | 서버 포트 (기본값 `8888`) |

### 선택적 변수
- `FMP_API_KEY`, `ALPHAVANTAGE_API_KEY` (뉴스 보강용).
- `TRADING_ENABLED` (`0` 기본값, `1`로 설정해 주문 전송 엔드포인트 허용).
- `TRADING_VOLUME` (기본 수동 거래량).
- `AUTO_FETCH`, `AUTO_FETCH_SYMBOL`, `AUTO_FETCH_TF`, `AUTO_FETCH_COUNT`, `AUTO_FETCH_SEC`.
- `PIN_DEFAULTS_TO_XAU_H1=1`: UI 시작 시 기본 심볼/타임프레임 강제.
- `LOG_LEVEL`, `LOG_BACKFILL`, 그리고 `/api/preferences`와 환경 변수로 제어되는 계정/폴링 관련 선호도.

참고:
- `MT5_PATH`는 MT5 설치 스크립트에서 사용하는 Wine prefix의 `terminal64.exe` 경로를 정확히 지정해야 합니다.
- 터미널 세션이 이미 로그인되어 있으면 MT5 계정 정보를 생략할 수 있으며 앱이 해당 세션을 재사용합니다.

## 🚀 사용법

### 서버 시작
```bash
python -m app.server
```

### UI 열기
- 데스크톱 UI: `http://localhost:8888/`
- 모바일 UI: `http://localhost:8888/app`

### 주요 URL
| Surface | URL | 용도 |
|---|---|---|
| Desktop | `http://localhost:8888/` | 캔들차트와 데스크톱 워크플로 제어 |
| Mobile | `http://localhost:8888/app` | 터치 우선 레이아웃과 컴팩트한 제어 |
| API Health | `http://localhost:8888/api/health/freshness` | 데이터 + 서비스 준비 상태 빠른 점검 |

### 일반 워크플로
1. MT5에서 바를 가져와 Postgres에 저장.
2. DB에서 바를 읽어 차트로 표시.
3. health/tech/news 분석 실행.
4. AI 트레이드 플랜 생성.
5. 안전 가드에서 주문 실행 또는 포지션 청산.

## 🔌 API 엔드포인트 (실전)
- `GET /api/fetch?symbol=XAUUSD&tf=H1&count=500[&mode=inc|full][&persist=1]`
  - MT5에서 가져와 DB로 업서트.
  - `persist=1`이면 서버가 `last_symbol/last_tf/last_count` 기본값을 저장합니다. bulk/자동 수집에서는 UI 선택값을 덮어쓰지 않도록 생략하세요.
- `GET /api/fetch_bulk` — 대량/예약 수집.
- `GET /api/data?symbol=XAUUSD&tf=H1&limit=500` — DB에서 차트 데이터 조회.
- `GET /api/strategy/run?symbol=XAUUSD&tf=H1&fast=20&slow=50`
  - SMA(20/50) 크로스오버를 실행하고 신호 페이로드를 반환.
  - 중요 구현 노트: 현재 서버 코드에서는 이 엔드포인트로 전략 기반 주문 배치가 비활성화되어 있으며, 주문 실행은 trade 엔드포인트에서 처리합니다.
- `POST /api/trade` — UI에서 수동 Buy/Sell 실행 (`TRADING_ENABLED` 제어).
- `POST /api/trade/execute_plan` — 생성된 플랜 실행. 사전 청산 및 stop-distance 검사 포함.
- `POST /api/close` — 포지션 일괄 청산 (`TRADING_ENABLED=0`에서도 가능, 안전 목적):
  - 현재 심볼: form body `symbol=...`; optional `side=long|short|both`.
  - 모든 심볼: `?scope=all` 및 선택적으로 `&side=...`.
  - 응답에는 `closed_count` 및 티켓별 결과가 포함됩니다.
- `POST /api/close_tickets` — 특정 티켓 묶음을 선택해 청산.
- `GET /api/positions`, `GET /api/positions/all`.
- `GET /api/stl`, `POST /api/stl/compute`, `POST /api/stl/prune`, `POST /api/stl/prune_all`, `DELETE /api/stl/run/{id}`.
- `GET /api/news`, `POST /api/news/backfill_forex`, `POST /api/news/analyze`.
- `GET /api/health/freshness`, `GET /api/tech/freshness`, `GET|POST /api/health/run`, `GET /api/health/runs`.
- `POST /api/preferences`와 관련 선호도 조회.
- `GET /api/ai/trade_plan`.
- `GET /api/accounts`, `GET /api/account/current`, `POST /api/account/login`.
- `GET /ws/updates`.

## 🧪 예시
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

## 🗄️ 데이터베이스 및 스키마
`sql/schema.sql`을 참조하세요.

요점:
- `ohlc_bars`의 복합 PK `(symbol, timeframe, ts)`가 중복 바 생성을 방지합니다.
- 수집은 `ON CONFLICT ... DO UPDATE`로 처리됩니다.
- STL 실행/컴포넌트, 선호도, 뉴스 기사, health runs, 계정 시리즈, 청산 거래, 시그널/주문 플랜 연결을 지원하는 추가 테이블이 존재합니다.

## 🛡️ 거래 제어 및 안전성
- 기본값이 `TRADING_ENABLED=0`인 환경 가드가 수동/플랜 실행 엔드포인트의 주문 실행을 비활성화합니다.
- UI 헤더의 `Auto` 동작은 전략 체크를 스케줄링할 뿐 거래 안전 게이트를 우회하지 않습니다.
- 거래 비활성 상태에서도 청산은 의도적으로 허용됩니다.
- Safe-max와 심볼/유형 가중치가 실행 흐름에서 노출을 제한하는 데 사용됩니다.

## 📈 STL 자동 계산 토글
- STL 자동 계산은 STL 패널의 `Auto STL` 스위치로 심볼 × 타임프레임 단위로 제어됩니다.
- 기본값은 OFF이며, 큰 데이터셋/느린 컨텍스트에서 UI 지연을 줄이기 위해 설정되어 있습니다.
- ON 상태에서는 누락되거나 오래된 STL을 자동 계산하고, OFF 상태에서는 수동 재계산 컨트롤을 사용합니다.
- 상태는 `/api/preferences`의 `stl_auto_compute:SYMBOL:TF` 키 및 빠른 시작을 위한 local storage에 저장됩니다.

## 🧷 마지막 선택 기억하기
- 서버는 `last_symbol`, `last_tf`, `last_count`를 저장해 템플릿 기본값으로 주입합니다.
- UI도 `localStorage`에 `last_symbol`/`last_tf`를 저장합니다.
- `/?reset=1`은 해당 페이지 로드 시 저장된 선호도를 무시합니다.
- `PIN_DEFAULTS_TO_XAU_H1=1`로 시작 기본값을 강제할 수 있습니다.

## 🤖 AI 트레이드 플랜 프롬프트 컨텍스트
AI 트레이드 플랜을 요청할 때, 서버는 현재 심볼/타임프레임에 대해 최신 Basic Health와 Tech Snapshot 실행이 존재하는지 확인하고(없으면 생성), 다음 항목으로 프롬프트 컨텍스트를 구성합니다.
- Basic health 블록,
- Tech AI 블록,
- 라이브 기술 스냅샷 블록.

## 🧰 개발 노트
- 주요 런타임 의존성: `tornado`, `asyncpg`, `MetaTrader5`, `numpy`, `python-dotenv`, `requests`, `httpx`, `statsmodels`, `openai`.
- 현재 공식 자동화 테스트 스위트는 구성되어 있지 않으며, smoke test와 수동 UI 검증이 주요 워크플로입니다.
- 권장 smoke test:
  - `python scripts/test_mixed_ai.py`
  - `python scripts/test_fmp.py`
  - `python scripts/test_fmp_endpoints.py`
- 릴리스 전 수동 점검:
  - pan/zoom 동기화,
  - STL 오버레이/period-line 동작,
  - 거래 제어(청산 안전 동작 포함),
  - 뉴스 패널 fallback 동작.

## 🧯 문제 해결
| 증상 | 조치 |
|---|---|
| MT5 initialize failed | `MT5_PATH`를 정확한 `terminal64.exe`로 설정한 뒤 터미널을 최소 한 번 수동 실행 |
| MT5 login failed | `MT5_SERVER` 값이 터미널 서버 문자열과 정확히 일치하는지 확인하거나, 자격 증명을 생략하고 활성 세션 재사용 |
| No data for symbol | 브로커 심볼 명명 규칙과 Market Watch 노출 설정을 확인 (`XAUUSD`, `XAUUSD.a`, `GOLD` 등) |
| Postgres connection issues | `DATABASE_URL` 확인 후 `psql "$DATABASE_URL" -c 'select 1;'` |
| Slow or stale UI analytics | 무거운 페어/TF에서 auto STL을 끄고 수동 재계산 |

## 🛣️ 로드맵
- README 기반 다국어 문서 외에도 `i18n/` 런타임 자산 확장.
- 공식 자동화 테스트 추가(API + 통합 + UI smoke 자동화).
- 배포 패키징과 재현 가능한 환경 프로파일 개선.
- AI 플랜 검증 및 실행 안전장치 개선.

## 🤝 기여
- 변경은 작고 범위를 명확하게 유지하세요.
- 가능하면 커밋 접두어를 명확히 사용하세요(예: `UI: ...`, `Server: ...`, `References: ...`).
- 관련 없는 포맷 변경은 피하세요.
- UI 변경 시 관련 스크린샷/GIF 첨부를 권장합니다.
- PR 전 smoke test와 로컬 브라우저 검증을 실행하세요.

## 📚 참고 자료
- `references/ai-trader-overview.md`
- `references/database_setup_postgres.md`
- `references/mt5_python_setup_ubuntu.md`
- `references/mt4_vs_mt5.md`
- `references/llm_trading_system.md`
- `references/release_deploy.md`
- `references/pnl_debugging.md`

## 📄 라이선스
이 저장소에는 현재(2026-02-28 기준) `LICENSE` 파일이 없습니다.

라이선스가 본 저장소에 명시되지 않았으므로 유지보수자가 명시적인 라이선스 파일을 추가할 때까지 이 안내를 유지합니다.


## ❤️ Support

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://camo.githubusercontent.com/24a4914f0b42c6f435f9e101621f1e52535b02c225764b2f6cc99416926004b7/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f446f6e6174652d4c617a79696e674172742d3045413545393f7374796c653d666f722d7468652d6261646765266c6f676f3d6b6f2d6669266c6f676f436f6c6f723d7768697465)](https://chat.lazying.art/donate) | [![PayPal](https://camo.githubusercontent.com/d0f57e8b016517a4b06961b24d0ca87d62fdba16e18bbdb6aba28e978dc0ea21/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f50617950616c2d526f6e677a686f754368656e2d3030343537433f7374796c653d666f722d7468652d6261646765266c6f676f3d70617970616c266c6f676f436f6c6f723d7768697465)](https://paypal.me/RongzhouChen) | [![Stripe](https://camo.githubusercontent.com/1152dfe04b6943afe3a8d2953676749603fb9f95e24088c92c97a01a897b4942/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f5374726970652d446f6e6174652d3633354246463f7374796c653d666f722d7468652d6261646765266c6f676f3d737472697065266c6f676f436f6c6f723d7768697465)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |
