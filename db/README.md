# `db/` — Cơ sở dữ liệu

**Owner:** B · **Bắt đầu:** cổng G1 (ngay) · **Trạng thái:** 🟡 khung trống, chờ code

## Đặt gì ở đây

| File | Nội dung |
|---|---|
| `schema.sql` | DDL tạo các bảng — **khớp 100%** với `docs/erd.md` (B tự thiết kế) |
| `seed.sql` | Dữ liệu mẫu: 3 roles, 5 users, 6 categories, **50 món**, 12 bàn, ~120 đơn/30 ngày. Phải **idempotent** |
| `migrations/` | Alembic `versions/` — mỗi lần đổi cấu trúc là 1 file mới |

## KHÔNG đặt

- File `.sql` dump dữ liệu thật, backup (`.gitignore` đã chặn)
- SQL viết tay để chạy tạm rồi quên
- Logic Python (thuộc `api/`)

## Quy ước

Đọc skill `sqlalchemy-model`. Quy tắc cứng: tiền `DECIMAL(12,0)`, `utf8mb4`, `InnoDB`,
FK có `ON DELETE` đúng chủ đích, **không sửa migration đã merge**.

Kiểm tra: `make reset-db` → phải tạo được DB sạch từ 0, chạy `seed.sql` 2 lần liên tiếp không lỗi.
