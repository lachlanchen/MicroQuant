<p>
  <b>Ngôn ngữ:</b>
  <a href="README.en.md">English</a>
  · <a href="README.zh-Hant.md">中文（繁體）</a>
  · <a href="README.zh-Hans.md">中文 (简体)</a>
  · <a href="README.ja.md">日本語</a>
  · <a href="README.ko.md">한국어</a>
  · <a href="README.vi.md">Tiếng Việt</a>
  · <a href="README.ar.md">العربية</a>
  · <a href="README.fr.md">Français</a>
  · <a href="README.es.md">Español</a>
</p>

# MicroQuant by Lazying.art — Tổng quan

MicroQuant by Lazying.art là một nguyên mẫu Micro Quant dựa trên Tornado + Postgres. Nó lấy dữ liệu thị trường (ví dụ vàng) từ MetaTrader 5, lưu vào PostgreSQL và dùng giao diện Chart.js để trình bày bộ công cụ AI Trade Plan.

Thư mục `docs/` chứa trang đích MicroQuant (`quant.lazying.art`), còn `references/` lưu các ghi chú hướng dẫn, cấu hình DB và tích hợp MT5 + Python.

Sau khi thiết lập `.env` và cơ sở dữ liệu, chạy `python -m app.server` để xem giao diện này tại máy.
