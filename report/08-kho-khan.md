# Chương 8: Khó khăn, Lỗi đã giải quyết & Bài học kinh nghiệm

> **Người phụ trách:** Cả nhóm A, B, C, D (mỗi vai 2–3 vấn đề thật; D (@Haianh4705) biên tập)
> **Cổng gắn kết & Hạn hoàn thành:** G2–G4 (tích luỹ theo mỗi cổng) → G5 (chốt trước hạn nộp 5 ngày)
> **Độ dài dự kiến:** 2–4 trang

## Mục lục dự kiến

- `8.1` Mở đầu
- `8.2` Sự cố kỹ thuật về môi trường, CI/CD & đóng gói
- `8.3` Vấn đề tích hợp dữ liệu, API & giao diện
- `8.4` Kinh nghiệm phối hợp nhóm & kiểm soát chất lượng AI
- `8.5` Tổng kết

## Nội dung dự kiến

- Sự cố hạ tầng đã ghi nhận trong `CHANGELOG.md`: Docker CLI ngoài PATH trên macOS, `MSYS_NO_PATHCONV` khi truyền cờ Inno Setup ở Git Bash, apt treo trên runner (`#52`), thiếu `libEGL.so.1` khi chạy Qt headless.
- Lỗi tích hợp dữ liệu & API: 3 mã đơn trùng trong seed (`#55`), header `User-Agent > 255` gây lỗi 500 khi đăng nhập (`#71`), lệch body khi GUI gọi `/auth/logout` (`#74`).
- Lỗi giao diện thực tế: nút bị ẩn trên dialog xác nhận ở Windows (`#44`), màn Dashboard dùng mock khi chờ endpoint `/reports/*` (`#70`).
- Kinh nghiệm dùng hợp đồng `docs/api-contract.md`, kiểm thử trực tiếp trên schema MySQL thật và vận hành nhật ký `docs/log/<vai>.md` để tránh "hộp đen" AI.

## Danh sách ảnh cần chụp & minh chứng

- **Đã có:** báo cáo bước kiểm tra Windows tại `docs/screenshots/installer/ci-run-report.md` và lịch sử fix trong `CHANGELOG.md`.
- **Minh chứng kèm theo:** dẫn mã Issue/PR (`#42`, `#44`, `#52`, `#55`, `#71`, `#74`) và đoạn cấu hình/code minh hoạ `≤ 30` dòng (không bắt buộc chụp ảnh UI riêng).
