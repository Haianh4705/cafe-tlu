# Nhật ký — C (Giao diện / UX)

> Quy tắc + mẫu: [`README.md`](README.md). Cập nhật trong PR đã làm việc, không dồn.
> **Người giữ file:** C — @MeoCamGuitar. Người khác không sửa hộ.

**Vùng:** `gui/`, `assets/` · **Bắt đầu:** G1

## 1. Tôi phụ trách gì

- Khung GUI + theme TLU + `BaseView` (#23), `api_client` + i18n (#24), màn Đăng nhập (#25)
- Màn Danh sách món (#30), màn Order tại bàn + thanh toán + in hoá đơn (#49 = PR #44)
- 4 trạng thái màn hình (loading / rỗng / lỗi / có dữ liệu), ảnh chụp vào `docs/screenshots/<module>/`
- Ghi `docs/test-cases.md` các ca vùng GUI — **chỉ đánh `PASS` khi chạy end-to-end với API + MySQL thật**

## 2. Việc đã làm

| Ngày | Issue | PR / commit | File chính | Làm gì (1 câu) | Vì sao cách đó (1 câu) |
|---|---|---|---|---|---|
| 11-08 | #23, #24, #25 | #40 / `97756b1` | `gui/main.py`, `gui/theme.py`, `gui/views/base.py`, `gui/api_client.py`, `gui/views/login_view.py` | dựng khung app, bảng màu TLU, `BaseView` 4 trạng thái, `ApiClient` bọc 23 endpoint và màn Đăng nhập | gom toàn bộ HTTP về `ApiClient` và token về `theme.py` để các màn hình sau dùng chung, không lặp |
| 11-09 | #30 | #41 / `e462185` | `gui/views/product_list_view.py`, `gui/widgets/product_dialog.py`, `tests/test_gui_products.py` | xây dựng màn Quản lý thực đơn: tìm kiếm `Ctrl+F`, lọc danh mục, phân trang và dialog CRUD + xác nhận xoá | tải qua `ApiWorker` trên `QThread` và đọc envelope `data`/`meta` để không treo UI khi gọi backend |
| 11-11 | #49 | #44 | `gui/views/order_view.py`, `gui/widgets/order_cart.py`, `gui/widgets/checkout_dialog.py`, `gui/widgets/receipt_dialog.py`, `tests/test_gui_order.py` | xây dựng màn Order 3 cột, hộp thoại thanh toán, xem trước/in hoá đơn K80 và bọc cờ `APP_ENV=demo` khi chưa có API | chỉ kích hoạt `MOCK_*` khi bật `APP_ENV=demo` để môi trường thật không nuốt lỗi API mà vẫn hiện `STATE_ERROR` + Thử lại |

## 3. AI đã làm gì

| Ngày | Công cụ | AI làm gì | Tôi sửa / kiểm chứng gì |
|---|---|---|---|
| 11-08 → 11-09 | AI agent trong repo | soạn nháp khung `theme.py`, `BaseView`, `ApiClient`, `LoginView`, `ProductListView`, `OrderView`, `CheckoutDialog`, `ReceiptDialog` và bộ unit test PySide6 | chạy thử trên máy Windows, tự đối chiếu 4 trạng thái + phân trang `meta` của #41, chụp ảnh gửi reviewer |
| 11-11 | Antigravity AI agent | hỗ trợ rebase lên `develop` (`ceb0f56`), bọc cờ `APP_ENV=demo`, sửa test lọc món & trả `TC-ORD-01..03` về `⬜` theo review #44 | chạy thử app thực tế trên Windows phát hiện **2 lỗi nút tàng hình** (nút "Xác nhận thanh toán" trong `CheckoutDialog` và mất nút ở `QMessageBox` huỷ đơn) → yêu cầu sửa thành nút Navy/Đỏ rõ nét + `ConfirmCancelOrderDialog`, và chạy `ruff`/`black`/`pytest` kiểm chứng |

## 4. Câu hỏi thầy hay hỏi (vùng C)

> Lấy từ [`defense.md`](../defense.md) mục C.

| # | Câu hỏi | Trả lời ngắn (2–4 câu) | Chỉ vào |
|---|---|---|---|
| 1 | Vì sao PySide6, không Tkinter? | | `docs/decisions.md` ADR-003 |
| 2 | Gọi API mất 2 giây thì UI thế nào? Sao không treo? | | worker/QThread trong `gui/` |
| 3 | Màn hình có 4 trạng thái — kể tên và vì sao cần? | | skill `pyside6-screen` mục 4 |
| 4 | Palette lấy ở đâu? Vì sao navy? | | `gui/theme.py` + ADR-007 |
| 5 | `api_client` để làm gì? Sao không gọi `requests` rải rác? | | `gui/api_client.py` |
| 6 | API trả 500 thì GUI hiển thị gì? | | nhánh `error.code` |
| 7 | Tiếng Việt: font gì, vì sao không dùng font mặc định? | | `gui/theme.py`, `assets/fonts/` |
| 8 | Signal/slot là gì? Ví dụ trong bài? | | kết nối worker → view |
| 9 | Resize 1280 vs full HD xử lý sao? | | layout/`QSizePolicy` |

## 5. Chưa làm / chưa hiểu

- [x] PR #44 (màn Order): đã sửa review lần 3 — trả `TC-ORD-01..03` về `⬜`, bọc mock sau `APP_ENV=demo` + `# shortcut:`, sửa bug mất nút khi huỷ đơn / thanh toán trên Windows, bổ sung assert lọc món & test trạng thái lỗi
- [ ] Màn hình Login (#25), Thực đơn (#30) và Order (#49) chưa nối API + MySQL thật vì A/B chưa xong backend (`#17`–`#22`, `#29`), nên chưa có ca e2e nào được tính `PASS`
- [ ] Chưa chạy kiểm tra `Setup.exe` (Release `v0.1.0`, #26) và `make doctor` đầy đủ trên máy Windows (điều kiện cổng G1)
- [ ] _(ghi những chỗ mình còn cần ôn kỹ trước buổi hỏi chéo — xem mục 4 và `docs/defense.md`)_

## 6. Nhật ký theo cổng

| Cổng | Ngày | Đã xong gì | Còn thiếu gì |
|---|---|---|---|
| G1 | 11-11 | khung GUI, `theme.py`, `BaseView`, `ApiClient`, `i18n.py`, màn Đăng nhập (#40) | nối API `#22` của A; xác nhận `make doctor` + test cài `Setup.exe` trên Windows (#26) |
| G2 | 11-11 | giao diện Quản lý thực đơn CRUD + phân trang + tìm kiếm (#41) | nối API `#29` của A; chạy lại e2e và điền `TC-AUTH`, `TC-PRD`, `TC-SRC` |
| G3 | 11-11 | giao diện Order tại bàn + thanh toán + in bill K80 (PR #44 / `#49`) | nối API `orders`/`checkout` của A; màn Dashboard (4 KPI + 2 biểu đồ) và màn Báo cáo |
