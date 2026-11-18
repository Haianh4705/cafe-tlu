# Chương 9: Hướng phát triển & Kết luận

> **Người phụ trách:** A (@bao20062005dh-creator) + D (@Haianh4705)
> **Cổng gắn kết & Hạn hoàn thành:** G3/G4 (rà các điểm `# shortcut:`) → G5 (chốt trước hạn nộp 5 ngày)
> **Độ dài dự kiến:** 2–3 trang

## Mục lục dự kiến

- `9.1` Mở đầu
- `9.2` Các giới hạn chủ động ở phiên bản hiện tại (`shortcut:`)
- `9.3` Hướng mở rộng nghiệp vụ quán café
- `9.4` Hướng nâng cấp kiến trúc & vận hành
- `9.5` Kết luận chung

## Nội dung dự kiến

- Tổng hợp danh sách nợ kỹ thuật đánh dấu `# shortcut:` trong mã nguồn và mục 5 của `docs/log/A.md`..`D.md` (tách `requirements-api.txt` giảm kích thước image, ký số `.exe`, rate limit đăng nhập, gộp bàn khác khu vực).
- Mở rộng tính năng khách tự gọi món qua mã QR tại bàn tái sử dụng nguyên backend REST API hiện có (định hướng ADR-006).
- Bổ sung quản lý định mức tồn kho nguyên liệu (trừ kho khi pha chế) và quy trình mở/chốt ca thu ngân theo ngày.
- Nâng cấp thông báo thời gian thực qua WebSocket cho màn hình Barista khi có đơn mới thay cho tải lại thủ công.

## Danh sách ảnh cần chụp & minh chứng

- **Sơ đồ tại chỗ:** vẽ sơ đồ kiến trúc mở rộng (Desktop + QR Web Client + WebSocket) bằng Mermaid ngay trong chương, tham chiếu `docs/screenshots/` nếu có bản thử nghiệm giao diện.
