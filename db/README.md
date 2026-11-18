# `db/` — Cơ sở dữ liệu

**Phạm vi:** sửa theo Issue chức năng được giao (`ADR-014`) — đọc skill `sqlalchemy-model` trước khi sửa, giữ kiến trúc `gui → api → db`. **Trạng thái:** ✅ 10 bảng + seed 120 đơn (PR #55, #69 thêm `refresh_tokens` theo ADR-013)

## Đặt gì ở đây

| File | Nội dung |
|---|---|
| `schema.sql` | DDL tạo các bảng — **nguồn chân lý** khớp với `docs/erd.md` |
| `seed.sql` | Dữ liệu mẫu: 3 roles, 5 users, 6 categories, **51 món**, 12 bàn, **120 đơn/30 ngày**, 119 hoá đơn. Phải **idempotent** |
| `verify_seed.sql` | Kiểm chứng sau khi nạp: đếm dòng, mã trùng, lệch tổng tiền, hoá đơn/dòng món mồ côi, số ngày có đơn, bảng `refresh_tokens` rỗng — in PASS/FAIL từng phép kiểm (23 phép) |
| `migrations/` | Alembic `versions/` — mỗi lần đổi cấu trúc là 1 file mới |

## KHÔNG đặt

- File `.sql` dump dữ liệu thật, backup (`.gitignore` đã chặn)
- SQL viết tay để chạy tạm rồi quên
- Logic Python (thuộc `api/`)

## Quy ước

Đọc skill `sqlalchemy-model`. Quy tắc cứng: tiền `DECIMAL(12,0)`, `utf8mb4`, `InnoDB`,
FK có `ON DELETE` đúng chủ đích, **không sửa migration đã merge**.

Kiểm tra:

```bash
make reset-db        # tạo DB sạch từ 0 rồi nạp schema + seed
docker exec -i cafetlu-mysql mysql -uroot -proot cafetlu < db/verify_seed.sql   # phải không có dòng FAIL
```

Nạp `seed.sql` lần 2 không được lỗi và không đổi số dòng (idempotent). Seed **không** hồi sinh món
đã xoá mềm (`deleted_at` không nằm trong `ON DUPLICATE KEY UPDATE`).
