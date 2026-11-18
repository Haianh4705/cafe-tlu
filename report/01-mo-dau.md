# Chương 1: Mở đầu

> **Người phụ trách:** D (@Haianh4705), cả nhóm rà phần phân công
> **Cổng gắn kết & Hạn hoàn thành:** G2 (bản thảo khung) → G5 (chốt số liệu trước hạn nộp 5 ngày)
> **Độ dài dự kiến:** 2–3 trang

## Mục lục dự kiến

- `1.1` Mở đầu & Lý do chọn đề tài
- `1.2` Mục tiêu & Phạm vi hệ thống (6 yêu cầu đề bài + định hướng mốc 8–9)
- `1.3` Phân công nhiệm vụ & Quy trình làm việc nhóm
- `1.4` Bố cục báo cáo & Tổng kết

## Nội dung dự kiến

- Trình bày bối cảnh quản lý quán café sinh viên TLU và 6 yêu cầu cốt lõi của Đề tài 5: CRUD, Login, thống kê, tìm kiếm, bộ cài Windows, phân quyền.
- Giải thích lựa chọn kiến trúc tách lớp `PySide6 → FastAPI → MySQL 8` (ADR-003, ADR-006) thay cho kết nối DB trực tiếp.
- Mô tả phân công 4 vai A/B/C/D (ADR-009), hợp đồng API v1 (`docs/api-contract.md`) và lộ trình kiểm soát chất lượng theo 6 cổng G1–G6 (`docs/plan.md`).
- Nêu quy trình minh bạch khi dùng AI: nhật ký `docs/log/<vai>.md`, mục "Giải thích được" 3 câu trong PR và hỏi chéo thứ Sáu (`docs/defense.md`).

## Danh sách ảnh cần chụp & minh chứng

- **Đã có:** `docs/screenshots/gui/main-window-20261107-01.png` — ảnh tổng quan cửa sổ chính CafeTLU minh hoạ sản phẩm ở phần mở đầu.
- **Cần chụp (G5):** `docs/screenshots/infra/ci-pipeline-<YYYYMMDD>-01.png` — ảnh chụp tổng quan pipeline CI/CD hoặc bảng trạng thái hoàn thành cổng.
