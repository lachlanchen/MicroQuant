[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


<p align="center">
  <img src="https://raw.githubusercontent.com/lachlanchen/lachlanchen/main/logos/banner.png" alt="LazyingArt banner" />
</p>

# MetaTrader QT - Bộ khởi đầu giao dịch định lượng (Triết lý Micro Quant)

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Backend](https://img.shields.io/badge/Backend-Tornado-2d7cbf)
![Database](https://img.shields.io/badge/Database-PostgreSQL-336791?logo=postgresql&logoColor=white)
![Broker](https://img.shields.io/badge/Broker%20Bridge-MetaTrader5-1f6feb)
![UI](https://img.shields.io/badge/UI-Lightweight%20Charts%20%2B%20Chart.js-0ea5e9)
![Status](https://img.shields.io/badge/README-Expanded-success)

## 📸 Ảnh chụp màn hình
![Micro Quant UI](figures/demos/micro-quant-ui.png)

<p align="center">
  <a href="https://my.roboforex.com/en/?a=efx" target="_blank" rel="noopener noreferrer">
    <button style="padding: 0.65rem 1.25rem; font-weight: 600; border-radius: 999px; border: none; color: white; background: #0060ff; cursor: pointer;">
      DATA Source
    </button>
  </a>
</p>

## 🧭 Tổng quan
Micro Quant tập trung ít hơn vào dashboard hào nhoáng và nhiều hơn vào một ngăn xếp logic giao dịch có thể lặp lại: hệ thống lấy dữ liệu OHLC từ MetaTrader 5, lưu vào Postgres, và đánh giá quyết định có hệ thống thông qua các tín hiệu theo lớp có AI hướng dẫn (Tin tức cơ bản, ảnh chụp kỹ thuật, kế hoạch giao dịch và lớp phủ STL). UI phản ánh triết lý đó bằng các nút bật/tắt căn chỉnh, đóng lệnh có lý do, lưu tuỳ chọn bền vững và khung thực thi giàu dữ liệu để server có thể chạy luồng giao dịch định kỳ hoặc theo modal một cách an toàn trong khi bạn vẫn kiểm tra log và bằng chứng.

Trang tĩnh (Quant by Lazying.art) nằm trong `docs/` và được xuất bản qua GitHub Pages (`trade.lazying.art` thông qua `docs/CNAME`). Repo cũng bao gồm tài liệu tham chiếu cho prompt AI Trade Plan, ghi chú tích hợp và tài liệu vận hành.

### Tóm tắt nhanh
| Khu vực | Chức năng |
|---|---|
| Data | Lấy MT5 OHLC và upsert vào PostgreSQL |
| Analytics | Chạy các luồng health/news/tech và STL |
| Decisioning | Tạo AI trade plan từ ngữ cảnh theo lớp |
| Execution | Thực thi/điều khiển luồng giao dịch với hàng rào an toàn |
| UI | Giao diện desktop/mobile với quy trình biểu đồ đồng bộ |

## 🧠 Triết lý cốt lõi
- **Chain of truth**: Kiểm tra tin tức cơ bản (văn bản + điểm số) và Tech snapshot (ngữ cảnh kỹ thuật nặng + STL) cấp dữ liệu cho một AI trade plan duy nhất cho mỗi symbol/timeframe. Các lần chạy tự động định kỳ và chạy thủ công theo modal dùng chung một pipeline và log lập luận.
- **Alignment-first execution**: Các tuỳ chọn Accept-Tech/Hold-Neutral, công tắc ignore-basics và wrapper partial-close giúp Tech được tuân theo có chủ đích, vị thế ngược chiều được đóng trước khi mở lệnh mới khi cần, và hạn chế các lần thoát lệnh không cần thiết.
- **Immutable data**: Mỗi lần fetch đều ghi vào Postgres với vệ sinh `ON CONFLICT`, trong khi `/api/data` đọc chuỗi đã làm sạch cho UI. Tuỳ chọn người dùng (auto volumes, `close_fraction`, hide-tech toggles, STL auto-compute) được lưu qua `/api/preferences`.
- **Safety-first trading**: `TRADING_ENABLED` và `safe_max` áp dụng quyền thủ công/tự động. `/api/close` và các bộ chạy định kỳ có thể ghi lý do đóng lệnh (tech neutral, misalignment, v.v.) để truy vết.

## ✨ Tính năng
- Nạp MT5 OHLC vào Postgres (`/api/fetch`, `/api/fetch_bulk`).
- UI biểu đồ tại `/` (desktop) và `/app` (mobile), dùng Chart.js + Lightweight Charts trong templates.
- Luồng STL decomposition (`/api/stl`, `/api/stl/compute`, các endpoint prune/delete).
- Nạp và phân tích tin tức (`/api/news`, `/api/news/backfill_forex`, `/api/news/analyze`).
- Điều phối quy trình AI (`/api/health/run`, `/api/health/runs`, `/api/ai/trade_plan`).
- Thực thi giao dịch thủ công (`/api/trade`, `/api/trade/execute_plan`) có bảo vệ bởi `TRADING_ENABLED`.
- Tác vụ rủi ro vị thế (`/api/positions*`, `/api/close`, `/api/close_tickets`) với thao tác đóng lệnh luôn được cho phép để đảm bảo an toàn.
- Luồng cập nhật WebSocket tại `/ws/updates`.

## 🗂️ Cấu trúc dự án
```text
metatrader_qt/
├── app/
│   ├── server.py                # Ứng dụng Tornado, routes, orchestration
│   ├── db.py                    # Lớp truy cập asyncpg + khởi tạo schema
│   ├── mt5_client.py            # Cầu nối MetaTrader5 + thao tác lệnh/dữ liệu
│   ├── news_fetcher.py          # Tổng hợp/lọc FMP/AlphaVantage
│   └── strategy.py              # Helper SMA crossover
├── templates/
│   ├── index.html               # UI desktop chính
│   └── mobile.html              # UI hướng mobile
├── static/                      # Tài nguyên PWA (icons/manifest/service worker)
├── sql/
│   └── schema.sql               # Schema DB cốt lõi
├── scripts/
│   ├── test_mixed_ai.py         # Smoke test Mixed AI
│   ├── test_fmp.py              # Smoke test FMP
│   ├── test_fmp_endpoints.py    # Script dò endpoint FMP
│   ├── setup_windows.ps1        # Bootstrap môi trường Windows
│   ├── run_windows.ps1          # Helper chạy trên Windows
│   └── bootstrap_venv311.sh     # Helper Python 3.11 cho Linux/mac
├── docs/                        # Trang đích GitHub Pages
├── references/                  # Ghi chú vận hành/cài đặt
├── strategies/llm/              # Các file JSON prompt/config
├── llm_model/echomind/          # Wrapper nhà cung cấp LLM
├── i18n/                        # Hiện có (đang để trống)
├── .github/FUNDING.yml          # Metadata sponsor/support
└── README.md + README.*.md      # Tài liệu chuẩn + đa ngôn ngữ
```

## ✅ Điều kiện tiên quyết
- Ubuntu/Linux hoặc Windows.
- MT5 đã cài và truy cập được (`terminal64.exe`), terminal đang chạy/đăng nhập.
- Python 3.10+ (khuyến nghị 3.11 để tương thích MetaTrader5).
- Một instance PostgreSQL.

## 🛠️ Cài đặt

### Windows (PowerShell)
```powershell
# 1) Tạo venv bằng Python 3.11 (MetaTrader5 chưa có wheels cho 3.13)
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt

# 2) Cấu hình env
Copy-Item .env.example .env
# Sửa .env và đặt DATABASE_URL, MT5_PATH (ví dụ C:\Program Files\MetaTrader 5\terminal64.exe), và thông tin demo MT5 của bạn
# Nạp env cho phiên hiện tại
Get-Content .env | Where-Object { $_ -and $_ -notmatch '^#' } | ForEach-Object { $n,$v = $_ -split '=',2; [Environment]::SetEnvironmentVariable($n, $v, 'Process') }

# 3) Chạy ứng dụng
python -m app.server
# Mở http://localhost:8888
```

Script hỗ trợ:
```powershell
scripts\setup_windows.ps1
scripts\run_windows.ps1
```

### Linux/macOS (bash)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Tùy chọn: venv 3.11 cục bộ (nếu Python global/Conda của bạn là 3.13)
# Yêu cầu python3.11 trên hệ thống
# sudo apt install python3.11 python3.11-venv
bash scripts/bootstrap_venv311.sh
source .venv311/bin/activate

# DB (dùng user/password riêng của bạn nếu cần)
# createdb -h localhost -p 5432 -U lachlan metatrader_db

# Cấu hình env
cp .env.example .env
# sửa .env với đường dẫn MT5 và thông tin đăng nhập
set -a; source .env; set +a

# Chạy ứng dụng
python -m app.server
# Mở http://localhost:8888
```

## ⚙️ Cấu hình
Sao chép `.env.example` thành `.env` rồi điều chỉnh các giá trị.

### Biến cốt lõi
| Variable | Mục đích |
|---|---|
| `DATABASE_URL` | DSN PostgreSQL ưu tiên |
| `DATABASE_MT_URL` | DSN dự phòng nếu `DATABASE_URL` chưa đặt |
| `DATABASE_QT_URL` | DSN dự phòng thứ cấp |
| `MT5_PATH` | Đường dẫn tới `terminal64.exe` (Wine hoặc native) |
| `MT5_LOGIN` / `MT5_PASSWORD` / `MT5_SERVER` | Có thể bỏ qua nếu phiên terminal MT5 đã đăng nhập |
| `PORT` | Cổng server (mặc định `8888`) |

### Biến tuỳ chọn
- `FMP_API_KEY`, `ALPHAVANTAGE_API_KEY` cho mở rộng dữ liệu tin tức.
- `TRADING_ENABLED` (`0` mặc định, đặt `1` để cho phép endpoint đặt lệnh).
- `TRADING_VOLUME` (khối lượng mặc định cho lệnh thủ công).
- `AUTO_FETCH`, `AUTO_FETCH_SYMBOL`, `AUTO_FETCH_TF`, `AUTO_FETCH_COUNT`, `AUTO_FETCH_SEC`.
- `PIN_DEFAULTS_TO_XAU_H1=1` để buộc mặc định symbol/timeframe khi UI khởi động.
- `LOG_LEVEL`, `LOG_BACKFILL`, cùng các tuỳ chọn liên quan account/poll qua `/api/preferences` và environment.

Lưu ý:
- `MT5_PATH` nên trỏ tới `terminal64.exe` trong Wine prefix mà script cài MT5 của bạn đang dùng.
- Bạn có thể bỏ qua thông tin đăng nhập MT5 khi phiên terminal đã login; ứng dụng sẽ cố gắng tái sử dụng phiên đó.

## 🚀 Cách dùng

### Khởi chạy server
```bash
python -m app.server
```

### Mở UI
- UI desktop: `http://localhost:8888/`
- UI mobile: `http://localhost:8888/app`

### Quy trình thường dùng
1. Lấy bars từ MT5 và lưu vào Postgres.
2. Đọc bars từ DB để vẽ biểu đồ.
3. Chạy phân tích health/tech/news.
4. Tạo AI trade plan.
5. Thực thi hoặc đóng vị thế dưới các rào chắn an toàn.

## 🔌 API Endpoints (Thực tế)
- `GET /api/fetch?symbol=XAUUSD&tf=H1&count=500[&mode=inc|full][&persist=1]`
  - Lấy dữ liệu từ MT5 và upsert vào DB.
  - Nếu `persist=1`, server lưu mặc định `last_symbol/last_tf/last_count`; các lần fetch hàng loạt/nền nên bỏ tuỳ chọn này để không ghi đè lựa chọn UI.
- `GET /api/fetch_bulk` — nạp dữ liệu hàng loạt/theo lịch.
- `GET /api/data?symbol=XAUUSD&tf=H1&limit=500` — đọc dữ liệu biểu đồ từ DB.
- `GET /api/strategy/run?symbol=XAUUSD&tf=H1&fast=20&slow=50`
  - Chạy SMA(20/50) crossover và trả về payload tín hiệu.
  - Ghi chú triển khai quan trọng: đặt lệnh từ endpoint này theo chiến lược hiện đang bị vô hiệu trong mã server; thực thi lệnh được xử lý qua các trade endpoint.
- `POST /api/trade` — Buy/Sell thủ công từ UI, bị chặn bởi `TRADING_ENABLED`.
- `POST /api/trade/execute_plan` — thực thi plan đã tạo, gồm kiểm tra đóng trước và khoảng cách stop.
- `POST /api/close` — đóng phẳng vị thế (được cho phép ngay cả khi `TRADING_ENABLED=0` để đảm bảo an toàn):
  - Symbol hiện tại: form body `symbol=...`; tuỳ chọn `side=long|short|both`.
  - Tất cả symbol: `?scope=all` và tuỳ chọn `&side=...`.
  - Phản hồi gồm `closed_count` và kết quả theo từng ticket.
- `POST /api/close_tickets` — đóng tập con được chỉ định theo ticket.
- `GET /api/positions`, `GET /api/positions/all`.
- `GET /api/stl`, `POST /api/stl/compute`, `POST /api/stl/prune`, `POST /api/stl/prune_all`, `DELETE /api/stl/run/{id}`.
- `GET /api/news`, `POST /api/news/backfill_forex`, `POST /api/news/analyze`.
- `GET /api/health/freshness`, `GET /api/tech/freshness`, `GET|POST /api/health/run`, `GET /api/health/runs`.
- `POST /api/preferences` và các endpoint truy xuất tuỳ chọn liên quan.
- `GET /api/ai/trade_plan`.
- `GET /api/accounts`, `GET /api/account/current`, `POST /api/account/login`.
- `GET /ws/updates`.

## 🧪 Ví dụ
```bash
# Lấy 500 nến H1 cho XAUUSD
curl "http://localhost:8888/api/fetch?symbol=XAUUSD&tf=H1&count=500"

# Đọc 200 nến từ DB
curl "http://localhost:8888/api/data?symbol=XAUUSD&tf=H1&limit=200"

# Chạy tính toán tín hiệu SMA
curl "http://localhost:8888/api/strategy/run?symbol=XAUUSD&tf=H1&fast=20&slow=50"

# Đóng các vị thế long của symbol hiện tại
curl -X POST "http://localhost:8888/api/close" -d "symbol=XAUUSD&side=long"

# Đóng tất cả vị thế short trên mọi symbol
curl -X POST "http://localhost:8888/api/close?scope=all&side=short"
```

## 🗄️ Cơ sở dữ liệu & Schema
Xem `sql/schema.sql`.

Điểm nổi bật:
- Composite PK `(symbol, timeframe, ts)` trong `ohlc_bars` ngăn trùng lặp nến.
- Luồng nạp dữ liệu dùng `ON CONFLICT ... DO UPDATE`.
- Các bảng bổ sung hỗ trợ STL runs/components, preferences, bài viết tin tức, health runs, chuỗi account, closed deals và liên kết signal/order-plan.

## 🛡️ Kiểm soát giao dịch & an toàn
- Hàng rào môi trường: `TRADING_ENABLED=0` mặc định vô hiệu hoá đặt lệnh từ endpoint thủ công/thực thi kế hoạch.
- Hành vi tiêu đề `Auto` trong UI sẽ lên lịch kiểm tra chiến lược; nó không bỏ qua các cổng an toàn giao dịch.
- Thao tác đóng vị thế được chủ đích cho phép ngay cả khi giao dịch đang tắt.
- Safe-max và trọng số theo symbol/kind được dùng trong luồng thực thi để giới hạn mức phơi nhiễm.

## 📈 Nút bật/tắt STL Auto-Compute
- STL auto-compute được kiểm soát theo từng cặp symbol x timeframe qua công tắc `Auto STL` trong panel STL.
- Mặc định là OFF để giảm lag UI trong bối cảnh dữ liệu lớn/chậm.
- Khi ON, STL thiếu/cũ có thể được tính lại tự động; nếu OFF thì dùng điều khiển tính lại thủ công.
- Trạng thái được lưu qua khoá `/api/preferences` như `stl_auto_compute:SYMBOL:TF` và cả local storage để khởi động nhanh hơn.

## 🧷 Ghi nhớ lựa chọn gần nhất
- Server lưu `last_symbol`, `last_tf`, `last_count` và chèn mặc định vào templates.
- UI cũng lưu `last_symbol`/`last_tf` trong `localStorage`.
- `/?reset=1` sẽ bỏ qua tuỳ chọn đã lưu cho lần tải trang đó.
- `PIN_DEFAULTS_TO_XAU_H1=1` có thể ép mặc định khi khởi động.

## 🤖 Ngữ cảnh prompt AI Trade Plan
Khi yêu cầu AI trade plan, server đảm bảo đã có bản chạy Basic Health và Tech Snapshot mới cho symbol/timeframe hiện tại (nếu thiếu sẽ tự tạo), rồi xây dựng ngữ cảnh prompt từ:
- Khối basic health,
- Khối Tech AI,
- Khối live technical snapshot.

## 🧰 Ghi chú phát triển
- Phụ thuộc runtime chính: `tornado`, `asyncpg`, `MetaTrader5`, `numpy`, `python-dotenv`, `requests`, `httpx`, `statsmodels`, `openai`.
- Hiện chưa có bộ kiểm thử tự động chính thức; quy trình hiện tại là smoke test và xác thực UI thủ công.
- Smoke test khuyến nghị:
  - `python scripts/test_mixed_ai.py`
  - `python scripts/test_fmp.py`
  - `python scripts/test_fmp_endpoints.py`
- Kiểm tra thủ công nên chạy trước khi push:
  - đồng bộ pan/zoom,
  - hành vi STL overlay/period line,
  - kiểm soát giao dịch (bao gồm hành vi đóng lệnh an toàn),
  - hành vi fallback của bảng tin tức.

## 🧯 Khắc phục sự cố
| Triệu chứng | Hành động |
|---|---|
| MT5 initialize failed | Đặt `MT5_PATH` đúng `terminal64.exe`, sau đó chạy terminal thủ công ít nhất một lần |
| MT5 login failed | Đảm bảo `MT5_SERVER` khớp chính xác chuỗi server trong terminal, hoặc bỏ credentials và tái sử dụng phiên đang hoạt động |
| No data for symbol | Xác minh quy ước đặt tên symbol của broker và khả năng hiển thị trong Market Watch (`XAUUSD`, `XAUUSD.a`, `GOLD`, v.v.) |
| Postgres connection issues | Xác minh `DATABASE_URL`, sau đó chạy `psql "$DATABASE_URL" -c 'select 1;'` |
| Slow or stale UI analytics | Tắt auto STL ở cặp/TF nặng và tính lại thủ công |

## 🛣️ Lộ trình
- Mở rộng tài nguyên runtime trong `i18n/` vượt ra ngoài bộ tài liệu README đa ngôn ngữ.
- Thêm kiểm thử tự động chính thức (API + integration + tự động hoá UI smoke).
- Cải thiện đóng gói triển khai và hồ sơ môi trường có thể tái lập.
- Tiếp tục tinh chỉnh kiểm định AI plan và hàng rào an toàn thực thi.

## 🤝 Đóng góp
- Giữ patch nhỏ và có phạm vi rõ ràng.
- Dùng tiền tố commit rõ ràng khi phù hợp (ví dụ: `UI: ...`, `Server: ...`, `References: ...`).
- Tránh thay đổi định dạng không liên quan.
- Kèm ảnh chụp/GIF cho thay đổi UI khi phù hợp.
- Chạy smoke test và kiểm tra trình duyệt cục bộ trước khi tạo PR.

## ❤️ Hỗ trợ / Tài trợ
Các liên kết tài trợ và hỗ trợ được cấu hình trong `.github/FUNDING.yml`:
- GitHub Sponsors: https://github.com/sponsors/lachlanchen
- Lazying.art: https://lazying.art
- Chat: https://chat.lazying.art
- OnlyIdeas: https://onlyideas.art

## 📚 Tài liệu tham khảo
- `references/ai-trader-overview.md`
- `references/database_setup_postgres.md`
- `references/mt5_python_setup_ubuntu.md`
- `references/mt4_vs_mt5.md`
- `references/llm_trading_system.md`
- `references/release_deploy.md`
- `references/pnl_debugging.md`

## 📄 Giấy phép
Không có tệp `LICENSE` trong repository này tính đến ngày 2026-02-28.

Giả định: điều khoản cấp phép hiện chưa được chỉ định trong repo; giữ ghi chú này cho đến khi maintainer thêm tệp giấy phép rõ ràng.
