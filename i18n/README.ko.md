[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


<p align="center">
  <img src="https://raw.githubusercontent.com/lachlanchen/lachlanchen/main/logos/banner.png" alt="LazyingArt banner" />
</p>

# MetaTrader QT - 정량 트레이딩 스타터 (Micro Quant 철학)

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Backend](https://img.shields.io/badge/Backend-Tornado-2d7cbf)
![Database](https://img.shields.io/badge/Database-PostgreSQL-336791?logo=postgresql&logoColor=white)
![Broker](https://img.shields.io/badge/Broker%20Bridge-MetaTrader5-1f6feb)
![UI](https://img.shields.io/badge/UI-Lightweight%20Charts%20%2B%20Chart.js-0ea5e9)
![Status](https://img.shields.io/badge/README-Expanded-success)

## 📸 스크린샷
![Micro Quant UI](figures/demos/micro-quant-ui.png)

<p align="center">
  <a href="https://my.roboforex.com/en/?a=efx" target="_blank" rel="noopener noreferrer">
    <button style="padding: 0.65rem 1.25rem; font-weight: 600; border-radius: 999px; border: none; color: white; background: #0060ff; cursor: pointer;">
      DATA Source
    </button>
  </a>
</p>

## 🧭 개요
Micro Quant는 화려한 대시보드보다 반복 가능한 트레이딩 로직 스택에 초점을 둡니다. MetaTrader 5에서 OHLC 데이터를 가져와 Postgres에 저장하고, 계층형 AI 신호(Basic news, Tech snapshot, trade plans, STL overlays)를 통해 체계적인 의사결정을 평가합니다. UI도 이 철학을 반영해 정렬 토글, 근거 기반 청산, 환경설정 영속화, 데이터가 풍부한 실행 패널을 제공하며, 사용자가 로그와 근거를 확인하는 동안 서버가 주기 실행 또는 모달 실행 트레이드 플로우를 안전하게 운용할 수 있도록 설계되었습니다.

정적 랜딩 페이지(Quant by Lazying.art)는 `docs/` 아래에 있으며 GitHub Pages(`docs/CNAME`을 통한 `trade.lazying.art`)로 배포됩니다. 저장소에는 AI Trade Plan 프롬프트, 통합 노트, 운영 문서도 포함되어 있습니다.

### 한눈에 보기
| 영역 | 설명 |
|---|---|
| Data | MT5 OHLC를 가져와 PostgreSQL에 upsert |
| Analytics | health/news/tech 및 STL 워크플로 실행 |
| Decisioning | 계층형 컨텍스트로 AI 거래 계획 생성 |
| Execution | 안전 가드 뒤에서 거래 플로우 실행/제어 |
| UI | 동기화된 차트 워크플로를 갖춘 데스크톱/모바일 뷰 |

## 🧠 핵심 철학
- **진실의 체인(Chain of truth)**: Basic news 점검(텍스트 + 점수)과 Tech snapshot(심화 기술 컨텍스트 + STL)이 심볼/타임프레임별 단일 AI 거래 계획으로 연결됩니다. 주기적 자동 실행과 수동 모달 실행은 동일한 파이프라인과 추론 로그를 공유합니다.
- **정렬 우선 실행(Alignment-first execution)**: Accept-Tech/Hold-Neutral 토글, ignore-basics 스위치, partial-close 래퍼를 통해 Tech 신호를 의도적으로 따르고, 필요 시 신규 진입 전에 반대 포지션을 청산하며, 불필요한 종료를 최소화합니다.
- **불변 데이터(Immutable data)**: 모든 fetch는 `ON CONFLICT` 위생 규칙과 함께 Postgres에 기록되며, `/api/data`는 UI용 정제 시계열을 읽습니다. 환경설정(auto volume, `close_fraction`, hide-tech 토글, STL auto-compute)은 `/api/preferences`를 통해 유지됩니다.
- **안전 우선 트레이딩(Safety-first trading)**: `TRADING_ENABLED`와 `safe_max`가 수동/자동 실행 권한을 제어합니다. `/api/close` 및 주기 실행기는 청산 사유(tech neutral, misalignment 등)를 로그로 남겨 추적 가능성을 제공합니다.

## ✨ 기능
- MT5 OHLC를 Postgres로 적재 (`/api/fetch`, `/api/fetch_bulk`).
- `/`(데스크톱) + `/app`(모바일) 차트 UI, 템플릿에서 Chart.js + Lightweight Charts 사용.
- STL 분해 워크플로 (`/api/stl`, `/api/stl/compute`, prune/delete 엔드포인트).
- 뉴스 수집 및 분석 (`/api/news`, `/api/news/backfill_forex`, `/api/news/analyze`).
- AI 워크플로 오케스트레이션 (`/api/health/run`, `/api/health/runs`, `/api/ai/trade_plan`).
- 수동 거래 실행 (`/api/trade`, `/api/trade/execute_plan`), `TRADING_ENABLED`로 보호.
- 포지션 리스크 작업 (`/api/positions*`, `/api/close`, `/api/close_tickets`), 안전을 위해 청산 작업은 허용.
- `/ws/updates` WebSocket 업데이트 스트림.

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
├── i18n/                        # Present (currently empty)
├── .github/FUNDING.yml          # Sponsor/support metadata
└── README.md + README.*.md      # Canonical + multilingual docs
```

## ✅ 사전 요구사항
- Ubuntu/Linux 또는 Windows.
- MT5가 설치되어 접근 가능해야 함 (`terminal64.exe`), 터미널 실행 및 로그인 상태 필요.
- Python 3.10+ (MetaTrader5 호환성 기준 3.11 권장).
- PostgreSQL 인스턴스.

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

도우미 스크립트:
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

## ⚙️ 구성
`.env.example`을 `.env`로 복사한 뒤 값을 조정하세요.

### 핵심 변수
| 변수 | 용도 |
|---|---|
| `DATABASE_URL` | 기본 PostgreSQL DSN |
| `DATABASE_MT_URL` | `DATABASE_URL` 미설정 시 대체 DSN |
| `DATABASE_QT_URL` | 2차 대체 DSN |
| `MT5_PATH` | `terminal64.exe` 경로(Wine 또는 네이티브) |
| `MT5_LOGIN` / `MT5_PASSWORD` / `MT5_SERVER` | MT5 터미널 세션이 이미 로그인되어 있으면 선택 사항 |
| `PORT` | 서버 포트 (기본 `8888`) |

### 선택 변수
- 뉴스 강화용 `FMP_API_KEY`, `ALPHAVANTAGE_API_KEY`.
- `TRADING_ENABLED` (기본 `0`, 주문 엔드포인트 허용 시 `1`).
- `TRADING_VOLUME` (기본 수동 볼륨).
- `AUTO_FETCH`, `AUTO_FETCH_SYMBOL`, `AUTO_FETCH_TF`, `AUTO_FETCH_COUNT`, `AUTO_FETCH_SEC`.
- UI 시작 기본 심볼/타임프레임 강제: `PIN_DEFAULTS_TO_XAU_H1=1`.
- `LOG_LEVEL`, `LOG_BACKFILL`, 그리고 `/api/preferences` 및 환경변수 기반 계정/폴링 관련 설정.

참고:
- `MT5_PATH`는 MT5 설치 스크립트가 사용하는 Wine prefix 아래 `terminal64.exe`를 가리켜야 합니다.
- 터미널 세션이 이미 로그인되어 있다면 MT5 자격증명은 생략 가능하며, 앱은 해당 세션 재사용을 시도합니다.

## 🚀 사용법

### 서버 시작
```bash
python -m app.server
```

### UI 열기
- 데스크톱 UI: `http://localhost:8888/`
- 모바일 UI: `http://localhost:8888/app`

### 일반 워크플로
1. MT5에서 바 데이터를 가져와 Postgres에 저장.
2. 차트 렌더링을 위해 DB에서 바 데이터를 조회.
3. health/tech/news 분석 실행.
4. AI 거래 계획 생성.
5. 안전 가드 하에서 포지션 실행 또는 청산.

## 🔌 API 엔드포인트 (실무 중심)
- `GET /api/fetch?symbol=XAUUSD&tf=H1&count=500[&mode=inc|full][&persist=1]`
  - MT5에서 가져와 DB에 upsert.
  - `persist=1`이면 서버가 `last_symbol/last_tf/last_count` 기본값을 저장합니다. bulk/background fetch에서는 UI 선택값 덮어쓰기를 피하기 위해 이 값을 생략해야 합니다.
- `GET /api/fetch_bulk` — 대량/스케줄 적재.
- `GET /api/data?symbol=XAUUSD&tf=H1&limit=500` — DB에서 차트 데이터 조회.
- `GET /api/strategy/run?symbol=XAUUSD&tf=H1&fast=20&slow=50`
  - SMA(20/50) 크로스오버를 실행하고 신호 payload 반환.
  - 중요 구현 메모: 이 엔드포인트의 전략 기반 주문 실행은 현재 서버 코드에서 비활성화되어 있으며, 주문 실행은 trade 엔드포인트를 통해 처리됩니다.
- `POST /api/trade` — UI에서 수동 Buy/Sell, `TRADING_ENABLED` 게이트 적용.
- `POST /api/trade/execute_plan` — 생성된 계획을 실행하며 pre-close 및 stop-distance 검사를 포함.
- `POST /api/close` — 포지션 일괄 청산 (`TRADING_ENABLED=0`이어도 안전을 위해 허용):
  - 현재 심볼: form body `symbol=...`; 선택적으로 `side=long|short|both`.
  - 전체 심볼: `?scope=all` 및 선택적으로 `&side=...`.
  - 응답에는 `closed_count`와 티켓별 결과 포함.
- `POST /api/close_tickets` — 티켓 기준으로 요청된 일부 포지션 청산.
- `GET /api/positions`, `GET /api/positions/all`.
- `GET /api/stl`, `POST /api/stl/compute`, `POST /api/stl/prune`, `POST /api/stl/prune_all`, `DELETE /api/stl/run/{id}`.
- `GET /api/news`, `POST /api/news/backfill_forex`, `POST /api/news/analyze`.
- `GET /api/health/freshness`, `GET /api/tech/freshness`, `GET|POST /api/health/run`, `GET /api/health/runs`.
- `POST /api/preferences` 및 관련 설정 조회.
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
`sql/schema.sql`을 참고하세요.

핵심 요약:
- `ohlc_bars`의 복합 PK `(symbol, timeframe, ts)`로 중복 바를 방지.
- 적재는 `ON CONFLICT ... DO UPDATE`를 사용.
- 추가 테이블은 STL 실행/컴포넌트, preferences, news articles, health runs, account series, closed deals, signal/order-plan 연결을 지원.

## 🛡️ 트레이딩 제어 및 안전장치
- 환경 가드: 기본값 `TRADING_ENABLED=0`으로 수동/계획 실행 엔드포인트의 주문 배치를 비활성화.
- UI의 `Auto` 헤더 동작은 전략 점검을 스케줄링할 뿐, 트레이딩 안전 게이트를 우회하지 않음.
- 트레이딩이 비활성화되어 있어도 청산 작업은 의도적으로 허용.
- 실행 플로우에서 safe-max 및 심볼/종류 가중치를 사용해 노출을 제한.

## 📈 STL 자동 계산 토글
- STL 자동 계산은 STL 패널의 `Auto STL` 스위치로 심볼 x 타임프레임 단위 제어.
- 대규모/저속 컨텍스트에서 UI 지연을 줄이기 위해 기본값은 OFF.
- ON이면 누락/오래된 STL을 자동 계산할 수 있고, 아니면 수동 재계산 컨트롤 사용.
- 상태는 `/api/preferences`의 `stl_auto_compute:SYMBOL:TF` 키 및 빠른 시작을 위한 로컬 스토리지에 저장.

## 🧷 마지막 선택값 기억
- 서버는 `last_symbol`, `last_tf`, `last_count`를 저장하고 템플릿에 기본값으로 주입.
- UI도 `localStorage`에 `last_symbol`/`last_tf` 저장.
- `/?reset=1`은 해당 페이지 로드에서 저장된 선호값을 무시.
- `PIN_DEFAULTS_TO_XAU_H1=1`으로 시작 기본값 강제 가능.

## 🤖 AI 거래 계획 프롬프트 컨텍스트
AI 거래 계획 요청 시 서버는 현재 심볼/타임프레임에 대해 최신 Basic Health 및 Tech Snapshot 실행 결과가 존재하는지 확인하고(없으면 생성), 이후 다음 블록으로 프롬프트 컨텍스트를 구성합니다:
- Basic health 블록,
- Tech AI 블록,
- Live technical snapshot 블록.

## 🧰 개발 노트
- 주요 런타임 의존성: `tornado`, `asyncpg`, `MetaTrader5`, `numpy`, `python-dotenv`, `requests`, `httpx`, `statsmodels`, `openai`.
- 현재 공식 자동 테스트 스위트는 구성되어 있지 않으며, 스모크 테스트와 수동 UI 검증이 활성 워크플로입니다.
- 권장 스모크 테스트:
  - `python scripts/test_mixed_ai.py`
  - `python scripts/test_fmp.py`
  - `python scripts/test_fmp_endpoints.py`
- 푸시 전 수동 점검 항목:
  - pan/zoom sync,
  - STL overlay/period line 동작,
  - trading controls (청산 안전 동작 포함),
  - news panel fallback 동작.

## 🧯 문제 해결
| 증상 | 조치 |
|---|---|
| MT5 initialize failed | `MT5_PATH`를 정확한 `terminal64.exe`로 설정하고, 터미널을 최소 1회 수동 실행 |
| MT5 login failed | `MT5_SERVER` 문자열이 터미널 서버 문자열과 정확히 일치하는지 확인하거나, 자격증명을 생략하고 활성 세션 재사용 |
| No data for symbol | 브로커 심볼 명명 및 Market Watch 노출 상태 확인 (`XAUUSD`, `XAUUSD.a`, `GOLD` 등) |
| Postgres connection issues | `DATABASE_URL` 확인 후 `psql "$DATABASE_URL" -c 'select 1;'` 실행 |
| Slow or stale UI analytics | 무거운 페어/타임프레임에서는 auto STL을 끄고 수동 재계산 |

## 🛣️ 로드맵
- README 기반 다국어 문서 외에도 `i18n/` 런타임 자산 확장.
- 공식 자동 테스트(API + 통합 + UI 스모크 자동화) 추가.
- 배포 패키징 및 재현 가능한 환경 프로필 개선.
- AI 계획 검증 및 실행 안전장치 지속 고도화.

## 🤝 기여
- 패치는 작고 범위를 명확하게 유지.
- 가능한 경우 명확한 커밋 접두사 사용 (예: `UI: ...`, `Server: ...`, `References: ...`).
- 무관한 포맷 변경은 지양.
- UI 변경 시 관련 스크린샷/GIF 포함.
- PR 전 스모크 테스트와 로컬 브라우저 점검 수행.

## ❤️ 지원 / 스폰서
스폰서 및 지원 링크는 `.github/FUNDING.yml`에 설정되어 있습니다:
- GitHub Sponsors: https://github.com/sponsors/lachlanchen
- Lazying.art: https://lazying.art
- Chat: https://chat.lazying.art
- OnlyIdeas: https://onlyideas.art

## 📚 참고 자료
- `references/ai-trader-overview.md`
- `references/database_setup_postgres.md`
- `references/mt5_python_setup_ubuntu.md`
- `references/mt4_vs_mt5.md`
- `references/llm_trading_system.md`
- `references/release_deploy.md`
- `references/pnl_debugging.md`

## 📄 라이선스
2026-02-28 기준 이 저장소에는 `LICENSE` 파일이 없습니다.

가정: 현재 저장소 내 라이선스 조건은 명시되지 않았으므로, 유지보수자가 명시적 라이선스 파일을 추가할 때까지 이 안내를 유지합니다.
