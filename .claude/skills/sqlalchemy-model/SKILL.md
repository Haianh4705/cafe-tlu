---
name: sqlalchemy-model
description: Thêm hoặc sửa bảng/cột trong CSDL MySQL của CafeTLU. Dùng khi được giao việc kiểu "thêm bảng", "thêm cột", "đổi kiểu dữ liệu", "viết migration", "cập nhật seed", hoặc khi schema.sql và ORM bị lệch nhau.
---

# Model + migration + schema.sql

## Nguyên tắc vàng: 4 nơi phải khớp nhau

Một thay đổi cấu trúc **luôn** chạm 4 file — thiếu một là hỏng:

| File | Vai trò |
|---|---|
| `docs/erd.md` | Bản thiết kế + từ điển dữ liệu (**chốt trước**) |
| `db/schema.sql` | DDL chạy được trên DB mới |
| `api/models/*.py` | ORM dùng bởi ứng dụng |
| `db/migrations/versions/*.py` | Nâng cấp DB đang có dữ liệu |

## Cấm

- **Sửa migration đã merge.** Cần đổi → tạo migration **mới**.
- `DROP TABLE` / `TRUNCATE` / `DELETE` không `WHERE` trên dữ liệu thật.
- Dùng `FLOAT`/`DOUBLE` cho tiền → phải `DECIMAL(12,0)`.
- Đổi tên/xoá cột đang dùng trong cùng một bước → thêm cột mới, migrate dữ liệu, xoá ở phiên bản sau.
- Viết `seed.sql` không idempotent.

## Quy ước (đã chốt trong docs/erd.md mục 2)

| Mục | Giá trị |
|---|---|
| Engine / charset | `InnoDB` · `utf8mb4` · `utf8mb4_unicode_ci` |
| PK | `id BIGINT UNSIGNED AUTO_INCREMENT` |
| FK | `<bảng_số_ít>_id`, `ON DELETE RESTRICT` (trừ `order_items` là CASCADE) |
| Tiền | `DECIMAL(12,0)` |
| Boolean | `is_available`, `is_deleted` — `TINYINT(1)` |
| Thời gian | `created_at`, `updated_at DATETIME DEFAULT CURRENT_TIMESTAMP` |
| Index | `idx_<bảng>_<cột>` · Unique `uq_<bảng>_<cột>` |

## Khuôn mẫu

```python
# api/models/product.py
class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    price: Mapped[Decimal] = mapped_column(Numeric(12, 0), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), default="ly", nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
```

```sql
-- db/schema.sql (phần tương ứng)
CREATE TABLE products (
  id           BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  name         VARCHAR(150)    NOT NULL,
  category_id  BIGINT UNSIGNED NOT NULL,
  price        DECIMAL(12,0)   NOT NULL,
  unit         VARCHAR(20)     NOT NULL DEFAULT 'ly',
  is_available TINYINT(1)      NOT NULL DEFAULT 1,
  is_deleted   TINYINT(1)      NOT NULL DEFAULT 0,
  created_at   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_products_name (name),
  KEY idx_products_category_id (category_id),
  CONSTRAINT fk_products_categories FOREIGN KEY (category_id)
    REFERENCES categories (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

## Quy trình

1. Sửa `docs/erd.md` trước (bảng + từ điển + bất biến nếu có).
2. Sửa `db/schema.sql`.
3. Sửa/thêm model.
4. `alembic revision -m "mô tả"` → điền `upgrade()`/`downgrade()`.
5. Cập nhật `db/seed.sql` nếu bảng mới cần dữ liệu mẫu.
6. `make reset-db` → phải tạo được DB sạch từ đầu.
7. Kiểm tra seed chạy **2 lần** liên tiếp không lỗi (idempotent).

## Checklist

- [ ] 4 nơi khớp nhau (erd / schema.sql / model / migration)
- [ ] Tiền là `DECIMAL(12,0)`; không có FLOAT
- [ ] Có index cho cột dùng để lọc/sắp xếp báo cáo
- [ ] FK có `ON DELETE` đúng chủ đích
- [ ] `make reset-db` chạy sạch từ 0
- [ ] `db/seed.sql` chạy lại lần 2 không lỗi
- [ ] Không sửa migration cũ
