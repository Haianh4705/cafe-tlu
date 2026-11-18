# Chương 7: Kết quả đạt được & Đánh giá hệ thống

> **Người phụ trách:** D (@Haianh4705) tổng hợp cùng A, B, C
> **Cổng gắn kết & Hạn hoàn thành:** G3 (luồng MVP) → G4/G5 (chốt kết quả chạy máy sạch trước hạn nộp 3 ngày)
> **Độ dài dự kiến:** 3–4 trang

## Mục lục dự kiến

- `7.1` Mở đầu
- `7.2` Đối chiếu mức độ hoàn thành 6 yêu cầu đề bài
- `7.3` Minh chứng kịch bản vận hành End-to-End
- `7.4` Số liệu kiểm thử, độ phủ & kiểm chứng trên máy sạch
- `7.5` Tổng kết

## Nội dung dự kiến

- Bảng đối chiếu 6 tiêu chí bắt buộc của Đề tài 5 (CRUD, Login, thống kê, tìm kiếm, bộ cài `.exe`, phân quyền) kèm điểm mở rộng mốc 8–9.
- Kịch bản chạy liên hoàn với dữ liệu thật: đăng nhập theo vai trò → CRUD món → mở bàn gọi món → thanh toán in hoá đơn → xem Dashboard & xuất báo cáo.
- Thống kê kết quả thật: số test `pytest` pass, coverage `api/services`, tỷ lệ đạt của 24 ca trong `docs/test-cases.md` và đối chiếu khớp số SQL – GUI – Excel/PDF.
- Biên bản chạy thử bộ cài và demo trên máy người khác ngoài máy phát triển ở cổng G5/G6.

## Danh sách ảnh cần chụp & minh chứng

- **Tham chiếu chéo (đã có, không copy trùng):** bộ ảnh tại `docs/screenshots/gui/`, `docs/screenshots/product/`, `docs/screenshots/order/`, `docs/screenshots/dashboard/` và `docs/screenshots/installer/`.
- **Cần chụp (G3/G5):** `docs/screenshots/reports/export-excel-pdf-<YYYYMMDD>-01.png` — file Excel/PDF xuất ra hiển thị đúng tiếng Việt và khớp số liệu với màn hình.
