# Chương 4: Thiết kế Kiến trúc Backend & REST API

> **Người phụ trách:** A (@bao20062005dh-creator) — Backend / API Lead
> **Cổng gắn kết & Hạn hoàn thành:** G2 (Auth + CRUD #1–#12) → G3 (đủ 23 endpoint) → G4/G5 (chốt bảo mật trước hạn nộp 5 ngày)
> **Độ dài dự kiến:** 3–5 trang

## Mục lục dự kiến

- `4.1` Mở đầu
- `4.2` Kiến trúc Client–Server & Phân tầng Backend
- `4.3` Hợp đồng REST API & Chuẩn hoá Envelope
- `4.4` Xác thực JWT, Refresh Token Rotation & Phân quyền RBAC
- `4.5` Quản lý Transaction, Xử lý lỗi & Tổng kết

## Nội dung dự kiến

- Luồng phụ thuộc một chiều `gui/ → api/routers/ → api/services/ → api/models/ → MySQL` (ADR-006, `WORKFLOW.md` mục 4), router mỏng không chứa SQL.
- Tổng hợp bảng 23 endpoint trong `docs/api-contract.md`, định dạng envelope `data`/`meta`/`error` và ngoại lệ phẳng `/health` (ADR-011).
- Cơ chế băm mật khẩu bcrypt cost 12 (`api/core/security.py`), JWT 30 phút, lưu SHA-256 của refresh token trong bảng `refresh_tokens` để thu hồi khi logout/rotate (ADR-013).
- Kiểm quyền trên server bằng `Depends(require_role(...))`, bọc transaction khi thanh toán (`checkout`) và chống SQL injection qua SQLAlchemy ORM.

## Danh sách ảnh cần chụp & minh chứng

- **Cần chụp (G2/G3):** `docs/screenshots/api/swagger-endpoints-<YYYYMMDD>-01.png` — trang Swagger `/docs` liệt kê đầy đủ endpoint đã triển khai.
- **Cần chụp (G2/G3):** `docs/screenshots/api/rbac-403-staff-<YYYYMMDD>-01.png` — minh chứng `staff` gọi endpoint admin bị server chặn `403 FORBIDDEN`.
