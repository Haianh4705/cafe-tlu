# Nhật ký — C (Giao diện / UX)

> Quy tắc + mẫu: [`README.md`](README.md). Cập nhật trong PR đã làm việc, không dồn.
> **Người giữ file:** C — @MeoCamGuitar. Người khác không sửa hộ.

**Vùng:** `gui/`, `assets/` · **Bắt đầu:** G1

## 1. Tôi phụ trách gì

- Khung GUI + theme TLU + `BaseView` (#23), `api_client` + i18n (#24), màn Đăng nhập (#25)
- Màn Danh sách món (#30), màn Order tại bàn + thanh toán + in hoá đơn (#49 = PR #44)
- Màn Tổng quan/Dashboard 4 KPI + 2 biểu đồ (G3 sóng 2, mục 9 — Issue chưa gán số)
- 4 trạng thái màn hình (loading / rỗng / lỗi / có dữ liệu), ảnh chụp vào `docs/screenshots/<module>/`
- Ghi `docs/test-cases.md` các ca vùng GUI — **chỉ đánh `PASS` khi chạy end-to-end với API + MySQL thật**

## 2. Việc đã làm

| Ngày | Issue | PR / commit | File chính | Làm gì (1 câu) | Vì sao cách đó (1 câu) |
|---|---|---|---|---|---|
| 11-08 | #23, #24, #25 | #40 / `97756b1` | `gui/main.py`, `gui/theme.py`, `gui/views/base.py`, `gui/api_client.py`, `gui/views/login_view.py` | dựng khung app, bảng màu TLU, `BaseView` 4 trạng thái, `ApiClient` bọc 23 endpoint và màn Đăng nhập | gom toàn bộ HTTP về `ApiClient` và token về `theme.py` để các màn hình sau dùng chung, không lặp |
| 11-09 | #30 | #41 / `e462185` | `gui/views/product_list_view.py`, `gui/widgets/product_dialog.py`, `tests/test_gui_products.py` | xây dựng màn Quản lý thực đơn: tìm kiếm `Ctrl+F`, lọc danh mục, phân trang và dialog CRUD + xác nhận xoá | tải qua `ApiWorker` trên `QThread` và đọc envelope `data`/`meta` để không treo UI khi gọi backend |
| 11-11 | #49 | #44 | `gui/views/order_view.py`, `gui/widgets/order_cart.py`, `gui/widgets/checkout_dialog.py`, `gui/widgets/receipt_dialog.py`, `tests/test_gui_order.py` | xây dựng màn Order 3 cột, hộp thoại thanh toán, xem trước/in hoá đơn K80 và bọc cờ `APP_ENV=demo` khi chưa có API | chỉ kích hoạt `MOCK_*` khi bật `APP_ENV=demo` để môi trường thật không nuốt lỗi API mà vẫn hiện `STATE_ERROR` + Thử lại |
| 11-17 | G3 mục 9 (chưa gán số) | #70 | `gui/views/dashboard_view.py`, `gui/main.py`, `gui/i18n.py`, `tests/test_gui_dashboard.py` | dựng Dashboard 4 thẻ KPI + 2 biểu đồ doanh thu 30 ngày và top 5 món bằng QtCharts (dùng mock `APP_ENV=demo`, chờ API `/reports/revenue` + `/reports/top-products`), thay placeholder trong `main.py` | dùng QtCharts có sẵn trong PySide6 (không thêm dependency ngoài) và gom mock sau `APP_ENV=demo` như OrderView để chờ API báo cáo từ A |
| 11-18 | #25 | `2a7b46c` / PR #114 (draft) | `gui/views/login_view.py`, `tests/test_gui_login.py`, `docs/test-cases.md`, `docs/screenshots/gui/` | xác minh phiên qua `/auth/me`; E2E admin/staff, ba lần sai mật khẩu, lỗi cùng thông điệp và mở lại form; lưu ảnh GUI | dùng danh tính trả về từ `/auth/me`; menu staff chỉ còn Tổng quan, Order, Bàn; `make check` trước đó đạt 84 test |
| 11-19 | #79 | PR #120 / `6e86238` | `gui/api_client.py`, `gui/main.py`, `tests/test_gui_login.py` | đồng bộ nhánh với develop/#124 và kiểm lại logout, hết hạn phiên, điều hướng về login, đăng nhập lại; 117 test local và CI xanh | giữ request refresh token đã có trong `ApiClient.logout()`; chạy request trong worker và chỉ phân biệt máy chủ chưa xác nhận với logout thành công trên form |
| 11-18 | #79 | PR #79 | `gui/api_client.py`, `gui/main.py`, `gui/i18n.py`, `tests/test_gui_login.py` | sửa nút Đăng xuất gửi refresh token, giải phóng phiên cục bộ cả khi lỗi mạng và đưa về form đăng nhập khi phiên hết hạn | xử lý xoá token trong finally và kết nối worker để luôn điều hướng về login form; thêm callback on_unauthenticated |
| 11-19 | #81 | PR #125 | `gui/views/dashboard_view.py`, `gui/main.py`, `gui/i18n.py`, `tests/test_gui_dashboard.py`, `docs/screenshots/dashboard/` | Dashboard không gọi endpoint chưa đăng ký; admin chủ động chọn Demo, staff chuyển nhanh sang Bán hàng; lưu ảnh admin/staff ở 1280×720 | giữ màn đầu sau login và reset Demo khi phiên thay đổi |
| 11-19 | #82 | PR #128 | `tests/test_gui_products.py` | đồng bộ develop `e3fafb8`; bổ sung test Xoá bộ lọc khi kết quả rỗng và tự lùi trang khi xoá món cuối trên trang cuối | `DB_NAME=cafe_tlu_test make lint` sạch; `DB_NAME=cafe_tlu_test make test` đạt 123 passed; logic #113 đã có nên chỉ thêm test |

## 3. AI đã làm gì

| Ngày | Công cụ | AI làm gì | Tôi sửa / kiểm chứng gì |
|---|---|---|---|
| 11-08 → 11-09 | AI agent trong repo | soạn nháp khung `theme.py`, `BaseView`, `ApiClient`, `LoginView`, `ProductListView`, `OrderView`, `CheckoutDialog`, `ReceiptDialog` và bộ unit test PySide6 | chạy thử trên máy Windows, tự đối chiếu 4 trạng thái + phân trang `meta` của #41, chụp ảnh gửi reviewer |
| 11-11 | Antigravity AI agent | hỗ trợ rebase lên `develop` (`ceb0f56`), bọc cờ `APP_ENV=demo`, sửa test lọc món & trả `TC-ORD-01..03` về `⬜` theo review #44 | chạy thử app thực tế trên Windows phát hiện **2 lỗi nút tàng hình** (nút "Xác nhận thanh toán" trong `CheckoutDialog` và mất nút ở `QMessageBox` huỷ đơn) → yêu cầu sửa thành nút Navy/Đỏ rõ nét + `ConfirmCancelOrderDialog`, và chạy `ruff`/`black`/`pytest` kiểm chứng |
| 11-17 | Command Code / Antigravity | viết nháp `DashboardView`, hàm chuẩn hoá response báo cáo (dùng mock khi `APP_ENV=demo`, chờ API `/reports/revenue` + `/reports/top-products`), 6 unit test PySide6 và 2 ảnh chụp giao diện | chạy `ruff`/`black`/`pytest` thật, tự xem ảnh 1280×720 và 1600×900, sửa selector `QFrame#...` và chuyển biểu đồ top món sang thanh ngang |
| 11-18 | Codex | thêm xác minh `/auth/me` và test GUI; cài `.venv`, bật MySQL/API/GUI; chạy GUI E2E cho admin/staff, ba lần sai mật khẩu, user không tồn tại và đóng/mở lại; lưu hai ảnh đăng nhập | `make check` với `cafe_tlu_test`: 84 passed; API `/me` trả đúng role; staff bị ẩn menu admin; lỗi đăng nhập inline đồng nhất; người dùng bật quyền CUA và chạy lại GUI; bỏ qua `make doctor` theo yêu cầu |
| 11-19 | Codex | rebase PR #120 lên `b23940c` (#124), rà luồng refresh/logout/session timeout và cập nhật minh chứng | `DB_NAME=cafe_tlu_test make lint && DB_NAME=cafe_tlu_test make test`: 117 passed; CI run 44358965729 xanh 2/2; giữ xác minh `/auth/me` từ #114 |
| 11-19 | Codex | kiểm tra logic #82 trên `origin/develop` và bổ sung hai ca GUI đang thiếu | baseline: `DB_NAME=cafe_tlu_test make lint && DB_NAME=cafe_tlu_test make test` xanh, 117 passed; 10 test `test_gui_products.py` xanh sau bổ sung |
| 11-18 | Antigravity AI agent | sửa cơ chế logout gửi refresh token, xử lý lỗi mạng không kẹt UI, thêm callback on_unauthenticated điều hướng khi 401, bổ sung 4 unit test PySide6 (#79) | chạy `ruff`/`black`/`pytest` đạt 68 passed, kiểm tra điều hướng thành công cả khi mất mạng và khi token hết hạn |
| 11-19 | Codex | đồng bộ PR #125 với `origin/develop`; bỏ lời gọi route báo cáo chưa đăng ký, thêm Demo theo lựa chọn admin và reset khi login/logout/hết phiên; giữ staff ở Dashboard với đường sang Order | `DB_NAME=cafe_tlu_test make lint && DB_NAME=cafe_tlu_test make test`: lint sạch, 121 passed; baseline trước sửa 116 passed; 21 test GUI mục tiêu xanh |
| 11-19 | Codex | đồng bộ PR #128 lên `develop` (`e3fafb8`), giải quyết xung đột nhật ký và giữ hai ca #82; dùng virtualenv của worktree #88 vì worktree #82 chưa có `.venv` | `DB_NAME=cafe_tlu_test make PY=<venv> lint` sạch; `DB_NAME=cafe_tlu_test make PY=<venv> test`: 123 passed, 14 warnings; không phát sinh lỗi `pytest-qt` |

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
- [x] Login (#25): API và GUI E2E admin/staff, menu theo role, ba lần sai mật khẩu, thông điệp chung cho user lạ, mở lại app về form đăng nhập; hai ảnh lưu trong `docs/screenshots/gui/`
- [ ] PR #114 đang ở dạng draft trên `feature/gui-login-meocam`; cần đẩy minh chứng mới để CI chạy lại, sau đó người dùng quyết định chuyển trạng thái PR/merge
- [ ] Chưa chạy kiểm tra `Setup.exe` (Release `v0.1.0`, #26) trên máy Windows; theo yêu cầu của người dùng, lượt này bỏ qua `make doctor` của C
- [ ] Dashboard chờ endpoint `GET /reports/revenue` và `GET /reports/top-products`; `docs/api-contract.md` **chưa có shape** response báo cáo nên GUI đang đọc `{total_revenue, total_orders, daily[]}` và `[{name, quantity}]` — cần A chốt
- [ ] _(ghi những chỗ mình còn cần ôn kỹ trước buổi hỏi chéo — xem mục 4 và `docs/defense.md`)_

## 6. Nhật ký theo cổng

| Cổng | Ngày | Đã xong gì | Còn thiếu gì |
|---|---|---|---|
| G1 | 11-18 | khung GUI, `theme.py`, `BaseView`, `ApiClient`; #25 xác minh API + GUI login, menu admin/staff, mở lại app và chụp hai ảnh; `make check` xanh | kiểm tra `Setup.exe` trên Windows (#26); lượt này bỏ qua `make doctor` của C theo yêu cầu |
| G2 | 11-11 | giao diện Quản lý thực đơn CRUD + phân trang + tìm kiếm (#41) | nối API `#29` của A; chạy lại e2e và điền `TC-AUTH`, `TC-PRD`, `TC-SRC` |
| G3 | 11-17 | giao diện Order tại bàn + thanh toán + in bill K80 (PR #44 / `#49`); màn Dashboard 4 KPI + 2 biểu đồ (mock, có unit test + ảnh chụp) | nối API `orders`/`checkout` và endpoint `GET /reports/...` của A; màn Báo cáo + lọc ngày; chốt shape response với A |
