# ERD & từ điển dữ liệu

> **Trạng thái:** 🟡 KHUNG — B điền và chốt trước cổng **G2** (cuối tuần 2).
> Quy ước đặt tên, kiểu dữ liệu, ràng buộc: xem `WORKFLOW.md` **mục 8**.
> DDL thật nằm ở `db/schema.sql` — file này là bản thiết kế, `schema.sql` là bản thi hành;
> **hai file phải luôn khớp nhau**.

## 1. Sơ đồ

```mermaid
erDiagram
    roles ||--o{ users : "phân quyền"
    users ||--o{ orders : "tạo"
    categories ||--o{ products : "chứa"
    tables ||--o{ orders : "phục vụ"
    orders ||--|{ order_items : "gồm"
    products ||--o{ order_items : "được bán trong"
    orders ||--|| invoices : "thanh toán"
    users ||--o{ audit_logs : "thao tác"

    users {
        bigint id PK
        varchar username UK
        varchar password_hash
        varchar full_name
        bigint role_id FK
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    roles { bigint id PK
            varchar name UK
            varchar description }
    categories { bigint id PK
                 varchar name UK
                 int sort_order
                 boolean is_deleted }
    products { bigint id PK
               varchar name UK
               bigint category_id FK
               decimal price
               varchar unit
               varchar image_url
               boolean is_available
               boolean is_deleted }
    tables { bigint id PK
             varchar name UK
             varchar zone
             varchar status }
    orders { bigint id PK
             bigint table_id FK
             bigint user_id FK
             varchar status
             decimal total_amount
             datetime created_at }
    order_items { bigint id PK
                  bigint order_id FK
                  bigint product_id FK
                  int quantity
                  decimal unit_price
                  varchar note
                  varchar status }
    invoices { bigint id PK
               bigint order_id FK
               decimal subtotal
               decimal discount
               decimal total
               varchar payment_method
               datetime paid_at }
    audit_logs { bigint id PK
                 bigint user_id FK
                 varchar action
                 varchar entity
                 bigint entity_id
                 json old_value
                 json new_value
                 datetime created_at }
```

> Nếu công cụ bạn dùng không hiển thị Mermaid, xuất ảnh từ dbdiagram.io rồi lưu
> `docs/screenshots/db/erd-<YYYYMMDD>.png` và nhúng vào đây.

## 2. Từ điển dữ liệu

> Điền cho từng bảng. Ví dụ mẫu:

### `products` — món ăn / đồ uống

| Cột | Kiểu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | BIGINT UNSIGNED | PK, AUTO_INCREMENT | |
| `name` | VARCHAR(150) | NOT NULL, UNIQUE | Tên món, duy nhất để tránh trùng |
| `category_id` | BIGINT UNSIGNED | NOT NULL, FK → `categories.id` | |
| `price` | DECIMAL(12,0) | NOT NULL, CHECK > 0 | VNĐ, **không phần lẻ** |
| `unit` | VARCHAR(20) | DEFAULT 'ly' | ly / cốc / phần |
| `image_url` | VARCHAR(255) | NULL | Đường dẫn tương đối tới `assets/` |
| `is_available` | BOOLEAN | DEFAULT 1 | Còn bán hay tạm hết |
| `is_deleted` | BOOLEAN | DEFAULT 0 | Xoá mềm |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | |
| `updated_at` | DATETIME | ON UPDATE CURRENT_TIMESTAMP | |

### `<bảng tiếp theo>`

| Cột | Kiểu | Ràng buộc | Mô tả |
|---|---|---|---|
| | | | |

## 3. Enum & trạng thái

| Enum | Giá trị | Ghi chú |
|---|---|---|
| `orders.status` | `open` · `paid` · `cancelled` | |
| `order_items.status` | `pending` · `preparing` · `served` · `cancelled` | Trạng thái pha chế |
| `tables.status` | `free` · `occupied` · `reserved` | |
| `invoices.payment_method` | `cash` · `transfer` · `momo` | |
| `roles.name` | `admin` · `staff` · `barista` | |

## 4. Câu hỏi nghiệp vụ cần chốt

- [ ] Một hoá đơn có gộp nhiều bàn được không? (ảnh hưởng `orders.table_id`)
- [ ] Xoá mềm món thì hoá đơn cũ hiển thị thế nào? (giữ `unit_price` tại thời điểm bán)
- [ ] Có quản lý tồn nguyên liệu ở mốc 8 không? (nếu có: thêm `ingredients`, `recipes`)
- [ ] Ca làm việc (`shifts`) có cần cho báo cáo theo nhân viên không?
