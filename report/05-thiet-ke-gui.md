# Chương 5: Thiết kế Giao diện Desktop (PySide6)

> **Người phụ trách:** C (@MeoCamGuitar) — GUI / UX Lead
> **Cổng gắn kết & Hạn hoàn thành:** G2 (Đăng nhập, Thực đơn) → G3 (Order, Dashboard, Báo cáo) → G5 (chốt ảnh dữ liệu thật trước hạn nộp 5 ngày)
> **Độ dài dự kiến:** 3–5 trang

## Mục lục dự kiến

- `5.1` Mở đầu
- `5.2` Nhận diện thương hiệu TLU (Palette, Font, Spacing)
- `5.3` Kiến trúc GUI bất đồng bộ (`BaseView` 4 trạng thái & `ApiWorker`)
- `5.4` Thiết kế chi tiết các màn hình nghiệp vụ
- `5.5` Tổng kết

## Nội dung dự kiến

- Áp dụng bảng màu TLU (navy `#000066`, đỏ cảnh báo `#F32409`, tint `#F1F5FF`) và font Manrope tập trung tại `gui/theme.py`, chuỗi Việt hoá ở `gui/i18n.py` (ADR-007).
- Gom toàn bộ gọi HTTP vào `gui/api_client.py` chạy trên `QThread`/`ApiWorker` để UI không treo; mỗi view kế thừa `BaseView` đủ 4 trạng thái `loading`/`empty`/`error`/`data`.
- Trình bày bố cục các màn: Đăng nhập, Quản lý thực đơn (`Ctrl+F`, phân trang), Order POS 3 cột + thanh toán + in phiếu K80, Dashboard `QtCharts` và Báo cáo lọc ngày.
- Kiểm tra phím tắt, validate đầu vào ở form, xác nhận thao tác huỷ/xoá và tương thích 3 độ phân giải (`1280×720`, `1600×900`, `1920×1080`).

## Danh sách ảnh cần chụp & minh chứng

- **Đã có (Đăng nhập & Khung):** `docs/screenshots/gui/login-screen-20261107-01.png`, `docs/screenshots/gui/main-window-20261107-01.png`.
- **Đã có (Thực đơn):** `docs/screenshots/product/product-list-20261107-01.png`, `docs/screenshots/product/product-dialog-20261107-01.png`.
- **Đã có (Order & Thanh toán):** `docs/screenshots/order/order-pos-view-20261108-01.png`, `docs/screenshots/order/order-checkout-dialog-20261108-01.png`, `docs/screenshots/order/order-receipt-dialog-20261109-01.png`, `docs/screenshots/order/order-cancel-dialog-20261111-01.png`.
- **Đã có (Dashboard):** `docs/screenshots/dashboard/dashboard-overview-20261117-01.png`, `docs/screenshots/dashboard/dashboard-overview-20261117-02.png` *(chụp lại dữ liệu thật sau khi nối API báo cáo ở G3)*.
- **Cần chụp (G3):** `docs/screenshots/reports/report-view-<YYYYMMDD>-01.png` — màn hình Báo cáo & bộ lọc khoảng ngày.
