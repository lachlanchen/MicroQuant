# MicroQuant by Lazying.art — Tổng quan

MicroQuant by Lazying.art là một nguyên mẫu Micro Quant dựa trên Tornado + Postgres. Nó lấy dữ liệu thị trường (ví dụ vàng) từ MetaTrader 5, lưu vào PostgreSQL và dùng giao diện Chart.js để trình bày bộ công cụ AI Trade Plan.

Thư mục `docs/` chứa trang đích MicroQuant (`quant.lazying.art`), còn `references/` lưu các ghi chú hướng dẫn, cấu hình DB và tích hợp MT5 + Python.

Sau khi thiết lập `.env` và cơ sở dữ liệu, chạy `python -m app.server` để xem giao diện này tại máy.
