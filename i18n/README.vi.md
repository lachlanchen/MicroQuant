[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# MetaTrader QT - Bộ khởi động giao dịch định lượng (Triết lý Micro Quant)

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Backend](https://img.shields.io/badge/Backend-Tornado-2d7cbf)
![Database](https://img.shields.io/badge/Database-PostgreSQL-336791?logo=postgresql&logoColor=white)
![Broker](https://img.shields.io/badge/Broker%20Bridge-MetaTrader5-1f6feb)
![UI](https://img.shields.io/badge/UI-Lightweight%20Charts%20%2B%20Chart.js-0ea5e9)
![Status](https://img.shields.io/badge/README-Expanded-success)
![GitHub%20Stars](https://img.shields.io/github/stars/lachlanchen/MicroQuant?style=for-the-badge&logo=github&logoColor=white&labelColor=0f172a&color=0ea5e9)
![GitHub%20Issues](https://img.shields.io/github/issues/lachlanchen/MicroQuant?style=for-the-badge&logo=github&logoColor=white&labelColor=0f172a&color=ef4444)

## 🎯 Tổng quan dự án

| Trọng tâm | Ngăn xếp |
|---|---|
| Runtime | Tornado + asyncpg + WebSocket |
| Trading | MetaTrader5 + ngữ cảnh AI/kỹ thuật/tin tức theo lớp |
| Lưu trữ | PostgreSQL với pipeline upsert có tính xác định |
| Triển khai | Tài nguyên PWA + UI desktop/mobile ưu tiên trình duyệt |

## Mục lục
- [📸 Screenshot](#-screenshot)
- [Tổng quan](#-overview)
- [Triết lý cốt lõi](#-core-philosophy)
- [Tính năng](#-features)
- [Cấu trúc dự án](#-project-structure)
- [Điều kiện tiên quyết](#-prerequisites)
- [Cài đặt](#-installation)
- [Cấu hình](#️-configuration)
- [Cách sử dụng](#-usage)
- [Endpoint API](#-api-endpoints-practical)
- [Ví dụ](#-examples)
- [Cơ sở dữ liệu & Schema](#-database--schema)
- [Kiểm soát giao dịch & An toàn](#️-trading-controls--safety)
- [Bật/tắt tính toán STL tự động](#-stl-auto-compute-toggle)
- [Nhớ lựa chọn gần nhất](#-remembering-last-selection)
- [Ngữ cảnh gợi ý kế hoạch giao dịch AI](#️-ai-trade-plan-prompt-context)
- [Ghi chú phát triển](#-development-notes)
- [Xử lý sự cố](#-troubleshooting)
- [Lộ trình](#-roadmap)
- [Đóng góp](#-contributing)
- [Tài liệu tham chiếu](#-references)
- [Hỗ trợ](#️-support)
- [Giấy phép](#-license)

## 📸 Screenshot
![Micro Quant UI](figures/demos/micro-quant-ui.png)

[![DATA Source](https://img.shields.io/badge/Data_Source-RoboForex-0060ff?style=for-the-badge&labelColor=0a4eb3)](https://my.roboforex.com/en/?a=efx)

Thông tin về tiếp thị liên kết: Nút RoboForex phía trên chứa mã đối tác của tôi (`efx`), vì vậy tôi có thể nhận hoa hồng từ hoạt động giao dịch của người được giới thiệu. Việc sử dụng là hoàn toàn tùy chọn và không ảnh hưởng đến cách MicroQuant hoạt động. Giao dịch đòn bẩy có nguy cơ thua lỗ cao; dự án này là phần mềm thử nghiệm, không phải lời khuyên đầu tư hay cam kết lợi nhuận. Xem [chương trình đối tác hiện hành](https://roboforex.com/partner-program/) và [công bố rủi ro](https://roboforex.com/about/company/documents/).

## 🧭 Tổng quan
Micro Quant không tập trung vào giao diện hào nhoáng, mà là một chuỗi logic giao dịch có thể lặp lại: nó lấy dữ liệu OHLC từ MetaTrader 5, lưu trữ vào PostgreSQL, và đánh giá quyết định có hệ thống thông qua các tín hiệu AI theo nhiều lớp (Basic news, Tech snapshot, kế hoạch giao dịch, và overlay STL). UI thể hiện đúng triết lý này với các công tắc căn chỉnh, đóng lệnh có giải thích, tùy chọn lưu preference, và bảng thực thi phong phú dữ liệu để server có thể chạy luồng giao dịch theo chu kỳ hoặc theo modal an toàn khi bạn theo dõi log và bằng chứng.

Trang landing tĩnh (Quant by Lazying.art) nằm trong `docs/` và được xuất bản qua GitHub Pages (`quant.lazying.art` qua `docs/CNAME`). Repository cũng gồm tài liệu tham chiếu cho prompt AI Trade Plan, ghi chú tích hợp, và tài liệu vận hành.

### Nhìn nhanh
| Khu vực | Chức năng |
|---|---|
| Data | Lấy OHLC MT5 và upsert vào PostgreSQL |
| Analytics | Chạy quy trình health/news/tech và STL |
| Decisioning | Xây kế hoạch giao dịch AI từ ngữ cảnh theo lớp |
| Execution | Thực thi/điều khiển luồng giao dịch dưới lớp bảo vệ an toàn |
| UI | Giao diện desktop/mobile với quy trình chart đồng bộ |

## 🧠 Triết lý cốt lõi
- **Chuỗi chân lý**: Kiểm tra tin tức cơ bản (text + scores) và snapshot kỹ thuật (ngữ cảnh kỹ thuật + STL) tạo ra một kế hoạch giao dịch AI duy nhất cho mỗi symbol/timeframe. Các lần chạy tự động chu kỳ và chạy thủ công theo modal dùng chung một pipeline và nhật ký reasoning.
- **Thực thi ưu tiên theo alignment**: Các công tắc Accept-Tech/Hold-Neutral, ignore-basics, và partial-close đảm bảo Tech được tuân thủ có chủ đích, đóng vị thế ngược trước khi mở lệnh mới khi cần, đồng thời giảm các lần thoát không cần thiết.
- **Dữ liệu bất biến**: Mỗi lần fetch đều ghi vào Postgres với quy tắc `ON CONFLICT`, trong khi `/api/data` đọc chuỗi dữ liệu đã sanitize cho UI. Các preference (`auto` settings, `close_fraction`, hide-tech toggles, STL auto-compute) được lưu bền bỉ qua `/api/preferences`.
- **Giao dịch an toàn trước tiên**: `TRADING_ENABLED` và `safe_max` điều phối quyền manual/auto. `/api/close` và runner định kỳ ghi lại lý do đóng lệnh (tech neutral, misalignment, v.v.) để dễ truy vết.

## ✨ Tính năng
- Thu nạp OHLC MT5 vào Postgres (`/api/fetch`, `/api/fetch_bulk`).
- UI Chart tại `/` (desktop) và `/app` (mobile), sử dụng Chart.js + Lightweight Charts trong template.
- Workflow phân rã STL (`/api/stl`, `/api/stl/compute`, các endpoint prune/delete).
- Thu thập và phân tích tin tức (`/api/news`, `/api/news/backfill_forex`, `/api/news/analyze`).
- Điều phối luồng AI (`/api/health/run`, `/api/health/runs`, `/api/ai/trade_plan`).
- Thực thi giao dịch thủ công (`/api/trade`, `/api/trade/execute_plan`) chịu gate bởi `TRADING_ENABLED`.
- Quản lý rủi ro vị thế (`/api/positions*`, `/api/close`, `/api/close_tickets`) với phép đóng theo hành vi an toàn rõ ràng.
- Stream cập nhật WebSocket tại `/ws/updates` cho gợi ý realtime và tín hiệu làm mới.
- Tài nguyên PWA/static cho dashboard có thể cài đặt.

## 🗂️ Cấu trúc dự án
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

## ✅ Điều kiện tiên quyết
- Ubuntu/Linux hoặc Windows có quyền truy cập terminal.
- MetaTrader 5 đã cài (`terminal64.exe`) và đăng nhập khi cần.
- Python 3.10+ (khuyến nghị Python 3.11 để tương thích rộng hơn với MetaTrader5 wheels).
- Một instance PostgreSQL có thể truy cập từ app server.
- Tùy chọn API key cho nhà cung cấp tin tức:
  - FMP
  - Alpha Vantage

## 🛠️ Cài đặt

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

## ⚙️ Cấu hình
Copy `.env.example` sang `.env` và chỉnh sửa các giá trị.

### Biến cốt lõi
| Biến | Mục đích |
|---|---|
| `DATABASE_URL` | DSN PostgreSQL ưu tiên |
| `DATABASE_MT_URL` | DSN dự phòng khi `DATABASE_URL` chưa set |
| `DATABASE_QT_URL` | DSN dự phòng phụ |
| `MT5_PATH` | Đường dẫn tới `terminal64.exe` (Wine hoặc native) |
| `MT5_LOGIN` / `MT5_PASSWORD` / `MT5_SERVER` | Tùy chọn nếu phiên MT5 đã đăng nhập sẵn |
| `PORT` | Cổng server (mặc định `8888`) |

### Biến tùy chọn
- `FMP_API_KEY`, `ALPHAVANTAGE_API_KEY` cho việc enrich tin tức.
- `TRADING_ENABLED` (`0` mặc định, set `1` để cho phép endpoint đặt lệnh).
- `TRADING_VOLUME` (khối lượng mặc định khi giao dịch thủ công).
- `AUTO_FETCH`, `AUTO_FETCH_SYMBOL`, `AUTO_FETCH_TF`, `AUTO_FETCH_COUNT`, `AUTO_FETCH_SEC`.
- `PIN_DEFAULTS_TO_XAU_H1=1` để ép UI mặc định về symbol/timeframe mặc định.
- `LOG_LEVEL`, `LOG_BACKFILL`, cộng với các preference liên quan account/poll qua `/api/preferences` và biến môi trường.

Lưu ý:
- `MT5_PATH` nên trỏ đúng tới `terminal64.exe` trong prefix Wine mà script cài MT5 của bạn dùng.
- Có thể bỏ thông tin đăng nhập MT5 nếu phiên terminal đang đăng nhập sẵn; app sẽ thử tái sử dụng lại phiên đó.

## 🚀 Cách sử dụng

### Khởi động server
```bash
python -m app.server
```

### Mở UI
- Desktop UI: `http://localhost:8888/`
- Mobile UI: `http://localhost:8888/app`

### URL chính
| Nơi dùng | URL | Mục đích |
|---|---|---|
| Desktop | `http://localhost:8888/` | Biểu đồ nến và workflow desktop |
| Mobile | `http://localhost:8888/app` | Layout tối ưu cử chỉ với điều khiển gọn |
| API Health | `http://localhost:8888/api/health/freshness` | Kiểm tra nhanh readiness dữ liệu + dịch vụ |

### Quy trình thường dùng
1. Fetch bar từ MT5 và lưu vào Postgres.
2. Đọc bar từ DB cho biểu đồ.
3. Chạy phân tích health/tech/news.
4. Sinh AI trade plan.
5. Thực thi hoặc đóng vị thế theo cơ chế an toàn.

## 🔌 API Endpoints (Practical)
- `GET /api/fetch?symbol=XAUUSD&tf=H1&count=500[&mode=inc|full][&persist=1]`
  - Fetch từ MT5 và upsert vào DB.
  - Nếu `persist=1`, server lưu mặc định `last_symbol/last_tf/last_count`; bulk/background fetch nên bỏ option này để tránh ghi đè lựa chọn UI.
- `GET /api/fetch_bulk` — nạp theo lô/lịch trình.
- `GET /api/data?symbol=XAUUSD&tf=H1&limit=500` — đọc chart data từ DB.
- `GET /api/strategy/run?symbol=XAUUSD&tf=H1&fast=20&slow=50`
  - Chạy cross SMA(20/50) và trả về payload tín hiệu.
  - Ghi chú quan trọng: thực thi lệnh theo strategy endpoint hiện đã bị tắt trong server; execute lệnh được xử lý qua trade endpoints.
- `POST /api/trade` — manual Buy/Sell từ UI, được gate bởi `TRADING_ENABLED`.
- `POST /api/trade/execute_plan` — thực thi kế hoạch đã sinh ra, có pre-close và kiểm tra stop-distance.
- `POST /api/close` — flatten positions (được phép kể cả khi `TRADING_ENABLED=0` vì an toàn):
  - Current symbol: form body `symbol=...`; optional `side=long|short|both`.
  - Tất cả symbol: `?scope=all` và `&side=...` (tuỳ chọn).
  - Response gồm `closed_count` và kết quả từng ticket.
- `POST /api/close_tickets` — đóng một phần theo danh sách ticket yêu cầu.
- `GET /api/positions`, `GET /api/positions/all`.
- `GET /api/stl`, `POST /api/stl/compute`, `POST /api/stl/prune`, `POST /api/stl/prune_all`, `DELETE /api/stl/run/{id}`.
- `GET /api/news`, `POST /api/news/backfill_forex`, `POST /api/news/analyze`.
- `GET /api/health/freshness`, `GET /api/tech/freshness`, `GET|POST /api/health/run`, `GET /api/health/runs`.
- `POST /api/preferences` và API lấy preference liên quan.
- `GET /api/ai/trade_plan`.
- `GET /api/accounts`, `GET /api/account/current`, `POST /api/account/login`.
- `GET /ws/updates`.

## 🧪 Ví dụ
```bash
# Fetch 500 H1 bars cho XAUUSD
curl "http://localhost:8888/api/fetch?symbol=XAUUSD&tf=H1&count=500"

# Read 200 bars từ DB
curl "http://localhost:8888/api/data?symbol=XAUUSD&tf=H1&limit=200"

# Run tính toán tín hiệu SMA
curl "http://localhost:8888/api/strategy/run?symbol=XAUUSD&tf=H1&fast=20&slow=50"

# Close vị thế long hiện tại của symbol
curl -X POST "http://localhost:8888/api/close" -d "symbol=XAUUSD&side=long"

# Close toàn bộ vị thế short trên mọi symbol
curl -X POST "http://localhost:8888/api/close?scope=all&side=short"
```

## 🗄️ Database & Schema
Xem `sql/schema.sql`.

Điểm nhấn:
- Composite PK `(symbol, timeframe, ts)` trong `ohlc_bars` giúp ngăn bar trùng lặp.
- Ingestion dùng `ON CONFLICT ... DO UPDATE`.
- Các bảng phụ hỗ trợ STL runs/components, preferences, news articles, health runs, account series, closed deals, và liên kết signal/order-plan.

## 🛡️ Kiểm soát giao dịch & An toàn
- Guard môi trường: `TRADING_ENABLED=0` mặc định vô hiệu hóa việc đặt lệnh từ các endpoint manual/plan execution.
- Header `Auto` trong UI lập lịch kiểm tra strategy; nó không đi qua (bypass) safety gate trading.
- Close operations được cho phép có chủ đích ngay cả khi trading tắt.
- safe-max và trọng số symbol/kind được dùng trong execution để giới hạn mức phơi nhiễm.

## 📈 Bật/tắt tính toán STL tự động
- Tính toán STL tự động được kiểm soát theo từng cặp x khung thời gian qua switch `Auto STL` trong panel STL.
- Mặc định là OFF để giảm độ trễ UI khi bối cảnh lớn/chậm.
- Khi ON, STL thiếu/cũ có thể tự động tính mới; nếu OFF thì dùng các nút recalc thủ công.
- State được giữ qua `/api/preferences` với key kiểu `stl_auto_compute:SYMBOL:TF` và cả localStorage để khởi động nhanh.

## 🧷 Nhớ lựa chọn gần nhất
- Server lưu `last_symbol`, `last_tf`, `last_count` rồi inject vào template mặc định.
- UI cũng lưu `last_symbol`/`last_tf` trong `localStorage`.
- `/?reset=1` sẽ bỏ qua preference đã lưu cho lần tải trang đó.
- `PIN_DEFAULTS_TO_XAU_H1=1` có thể ép mặc định khởi động.

## 🤖 Ngữ cảnh gợi ý kế hoạch giao dịch AI
Khi yêu cầu tạo AI trade plan, server đảm bảo có run Basic Health và Tech Snapshot mới cho symbol/timeframe hiện tại (sẽ tạo mới nếu thiếu), rồi build prompt context từ:
- Khối health cơ bản,
- Khối Tech AI,
- Khối live technical snapshot.

## 🧰 Ghi chú phát triển
- Các dependency runtime chính: `tornado`, `asyncpg`, `MetaTrader5`, `numpy`, `python-dotenv`, `requests`, `httpx`, `statsmodels`, `openai`.
- Hiện chưa có bộ test tự động chính thức; smoke tests và kiểm tra thủ công UI là quy trình hoạt động.
- Smoke tests khuyến nghị:
  - `python scripts/test_mixed_ai.py`
  - `python scripts/test_fmp.py`
  - `python scripts/test_fmp_endpoints.py`
- Kiểm tra thủ công trước khi phát hành:
  - pan/zoom sync,
  - hành vi STL overlay/period-line,
  - trading controls (kể cả close safety behavior),
  - news panel fallback behavior.

## 🧯 Xử lý sự cố
| Triệu chứng | Hành động |
|---|---|
| MT5 initialize failed | Đặt `MT5_PATH` đúng tới `terminal64.exe` rồi khởi chạy terminal thủ công ít nhất một lần |
| MT5 login failed | Đảm bảo `MT5_SERVER` khớp chính xác với chuỗi server của terminal, hoặc bỏ credential và tái dùng session active |
| Không có dữ liệu cho symbol | Kiểm tra tên symbol của broker và khả năng hiển thị trong Market Watch (`XAUUSD`, `XAUUSD.a`, `GOLD`, ...`) |
| Lỗi kết nối Postgres | Kiểm tra `DATABASE_URL`, sau đó chạy `psql "$DATABASE_URL" -c 'select 1;'` |
| Analytics UI chậm hoặc treo dữ liệu | Tắt auto STL với cặp/TF nặng rồi tính lại thủ công |

## 🛣️ Lộ trình
- Mở rộng tài nguyên runtime của `i18n/` ngoài tài liệu README đa ngôn ngữ.
- Thêm bộ test tự động chính thức (API + integration + UI smoke automation).
- Cải thiện đóng gói triển khai và profile môi trường tái tạo được.
- Tiếp tục tinh chỉnh kiểm chứng kế hoạch AI và rào chắn execution.

## 🤝 Đóng góp
- Giữ patch nhỏ và giới hạn phạm vi.
- Dùng tiền tố commit rõ ràng khi có thể (ví dụ: `UI: ...`, `Server: ...`, `References: ...`).
- Tránh chỉnh sửa định dạng không liên quan.
- Đính kèm ảnh chụp/GIF cho thay đổi UI khi có liên quan.
- Chạy smoke test và kiểm tra trình duyệt local trước khi mở PR.

## 📚 Tài liệu tham khảo
- `references/ai-trader-overview.md`
- `references/database_setup_postgres.md`
- `references/mt5_python_setup_ubuntu.md`
- `references/mt4_vs_mt5.md`
- `references/llm_trading_system.md`
- `references/release_deploy.md`
- `references/pnl_debugging.md`

## ❤️ Support

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://camo.githubusercontent.com/24a4914f0b42c6f435f9e101621f1e52535b02c225764b2f6cc99416926004b7/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f446f6e6174652d4c617a79696e674172742d3045413545393f7374796c653d666f722d7468652d6261646765266c6f676f3d6b6f2d6669266c6f676f436f6c6f723d7768697465)](https://chat.lazying.art/donate) | [![PayPal](https://camo.githubusercontent.com/d0f57e8b016517a4b06961b24d0ca87d62fdba16e18bbdb6aba28e978dc0ea21/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f50617950616c2d526f6e677a686f754368656e2d3030343537433f7374796c653d666f722d7468652d6261646765266c6f676f3d70617970616c266c6f676f436f6c6f723d7768697465)](https://paypal.me/RongzhouChen) | [![Stripe](https://camo.githubusercontent.com/1152dfe04b6943afe3a8d2953676749603fb9f95e24088c92c97a01a897b4942/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f5374726970652d446f6e6174652d3633354246463f7374796c653d666f722d7468652d6261646765266c6f676f3d737472697065266c6f676f436f6c6f723d7768697465)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

## 📄 License
Không có tệp `LICENSE` trong repository tính đến ngày 2026-02-28.

Giả định: điều khoản cấp phép hiện tại trong repo chưa được ghi rõ; giữ nguyên ghi chú này cho đến khi maintainer thêm file giấy phép chính thức.
