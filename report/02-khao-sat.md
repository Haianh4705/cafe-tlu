# Chương 2: Khảo sát nghiệp vụ & Đặc tả yêu cầu

> **Người phụ trách:** C (@MeoCamGuitar) chủ trì, B (@trungdunxg) phối hợp
> **Cổng gắn kết & Hạn hoàn thành:** G3 (hoàn thiện sau khi chốt luồng Order/Thanh toán) → G5 (chốt trước hạn nộp 5 ngày)
> **Độ dài dự kiến:** 2–3 trang

## Mục lục dự kiến

- `2.1` Mở đầu
- `2.2` Khảo sát quy trình vận hành quán café tại TLU
- `2.3` Hạn chế của quản lý thủ công & bài toán đặt ra
- `2.4` Đặc tả yêu cầu chức năng & phi chức năng
- `2.5` Tổng kết

## Nội dung dự kiến

- Mô tả đặc thù phục vụ theo khung giờ giữa các ca học và sơ đồ 3 khu vực bàn (Tầng 1, Tầng 2, Ban công — 12 bàn trong `db/seed.sql`).
- Phân tích quy trình phối hợp 3 vai trò tại quán: Quản lý (`admin`), Thu ngân/Phục vụ (`staff`), Pha chế (`barista`).
- Bảng yêu cầu chức năng (đăng nhập, quản lý thực đơn, gọi món tại bàn, thanh toán in hoá đơn, báo cáo doanh thu/top món, audit log) khớp `docs/api-contract.md`.
- Yêu cầu phi chức năng: giao diện bất đồng bộ không treo, tiền tệ `DECIMAL(12,0)` không sai số, cài đặt chạy được trên máy Windows sạch.

## Danh sách ảnh cần chụp & minh chứng

- **Đã có:** `docs/screenshots/order/order-pos-view-20261108-01.png` — minh hoạ luồng chọn bàn và gọi món tại quầy.
- **Sơ đồ tại chỗ:** vẽ lưu đồ quy trình gọi món – pha chế – thanh toán bằng Mermaid trực tiếp trong chương (không lưu file ảnh trùng).
