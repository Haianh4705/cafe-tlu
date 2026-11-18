# Đặc tả API (hợp đồng)

> **Nguồn chân lý** về hợp đồng giữa GUI (C) và Backend (A). B viết phần số liệu báo cáo.
> Định dạng request/response, mã lỗi, quy ước URL: xem `WORKFLOW.md` **mục 9** (không lặp lại ở đây).
>
> **Trạng thái:** ✅ Đã chốt v1 (2026-11-04) — 23 endpoint dưới đây là **hợp đồng** giữa
> GUI (C) và Backend (A). Bổ sung endpoint mới thì được (thêm dòng + PR riêng); **đổi hoặc
> bỏ endpoint đã đánh dấu ✅ thì phải báo nhóm trước**.

## 1. Thông tin chung

| Mục | Giá trị |
|---|---|
| Base URL (dev) | `http://127.0.0.1:8000/api/v1` |
| Base URL (deploy) | *điền ở G4* |
| Xác thực | `Authorization: Bearer <access_token>` |
| Định dạng | JSON, `charset=utf-8` |
| Swagger | `http://127.0.0.1:8000/docs` (tự sinh) |
| Phân trang | `?page=1&page_size=20` (mặc định 20, tối đa 100) |
| Sắp xếp | `?sort=-created_at` (dấu `-` = giảm dần) |

## 2. Bảng endpoint

> Cột "Quyền" dùng tên role: `admin` · `staff` · `barista`.

| # | Method | Path | Quyền | Mô tả | Trạng thái |
|---|---|---|---|---|---|
| 1 | GET | `/health` | public | Kiểm tra sống + version | ✅ |
| 2 | POST | `/auth/login` | public | Trả access + refresh token | ✅ |
| 3 | POST | `/auth/refresh` | public | Làm mới access token | ✅ |
| 4 | POST | `/auth/logout` | đã đăng nhập | Thu hồi token | ✅ |
| 5 | GET | `/auth/me` | đã đăng nhập | Thông tin người dùng hiện tại | ✅ |
| 6 | GET | `/categories` | staff+ | Danh sách danh mục | ✅ |
| 7 | POST | `/categories` | admin | Tạo danh mục | ✅ |
| 8 | GET | `/products` | staff+ | Danh sách + tìm kiếm + lọc | ✅ |
| 9 | GET | `/products/{id}` | staff+ | Chi tiết món | ✅ |
| 10 | POST | `/products` | admin | Tạo món | ✅ |
| 11 | PATCH | `/products/{id}` | admin | Sửa món | ✅ |
| 12 | DELETE | `/products/{id}` | admin | Xoá mềm món | ✅ |
| 13 | GET | `/tables` | staff+ | Danh sách bàn + trạng thái + `open_order_id` | ✅ |
| 14 | POST | `/orders` | staff+ | Tạo đơn (order tại bàn) | ✅ |
| 15 | GET | `/orders/{id}` | staff+ | Chi tiết đơn | ✅ |
| 16 | POST | `/orders/{id}/items` | staff+ | Thêm món vào đơn | ✅ |
| 17 | PATCH | `/orders/{id}/items/{item_id}` | staff+ | Sửa số lượng / ghi chú | ✅ |
| 18 | DELETE | `/orders/{id}/items/{item_id}` | staff+ | Bỏ món khỏi đơn | ✅ |
| 19 | POST | `/orders/{id}/checkout` | staff+ | Thanh toán + tạo hoá đơn (transaction) | ✅ |
| 20 | GET | `/reports/revenue` | admin | Doanh thu theo ngày/tháng | ⬜ |
| 21 | GET | `/reports/top-products` | admin | Top món bán chạy | ⬜ |
| 22 | GET | `/reports/export` | admin | Xuất Excel/PDF | ⬜ |
| 23 | GET | `/audit-logs` | admin | Lịch sử thao tác | ⬜ |
| 24 | GET | `/public/menu` | public | Danh mục, bàn và thực đơn cho Kiosk khách hàng | ✅ |
| 25 | POST | `/public/orders` | public | Tạo đơn gọi món từ Kiosk khách hàng (trả kèm `qr_payload`) | ✅ |

**Trạng thái:** ⬜ chưa làm · 🟡 đang làm · ✅ xong + có test

> Lỗi `422 VALIDATION_ERROR` chỉ trả `details.errors[{loc, msg, type}]`, không echo `input`/`ctx`
> để không lộ mật khẩu hoặc dữ liệu nhạy cảm trong phản hồi/log.

> `GET /tables` trả thêm `open_order_id` (`null` nếu bàn trống) để GUI mở lại đơn đang phục vụ.
> `POST /orders/{id}/items` gộp số lượng nếu món đã có trong đơn; mọi thay đổi món đều tính lại
> `orders.total_amount` ở server trong cùng transaction.
> `POST /orders/{id}/checkout` nhận `payment_method` (`cash|qr|transfer|card`), `paid_amount`
> (mặc định bằng thực thu), `discount_amount`, `notes`; server tính lại tiền, tạo `invoices`,
> đóng đơn và trả bàn về `available` trong một transaction; kết quả trả `{order, invoice}`.

## 3. Mã lỗi

> Khai báo hằng số trong `shared/error_codes.py`. **Không đổi mã đã phát hành.**

| `error.code` | HTTP | Khi nào | `message` gợi ý |
|---|---|---|---|
| `VALIDATION_ERROR` | 422 | Dữ liệu đầu vào sai | "Dữ liệu không hợp lệ" |
| `UNAUTHENTICATED` | 401 | Thiếu/sai token | "Vui lòng đăng nhập lại" |
| `FORBIDDEN` | 403 | Không đủ quyền | "Bạn không có quyền thực hiện thao tác này" |
| `NOT_FOUND` | 404 | Không tìm thấy | "Không tìm thấy dữ liệu" |
| `PRODUCT_NAME_DUPLICATED` | 409 | Trùng tên món | "Tên món đã tồn tại" |
| `ORDER_ALREADY_PAID` | 409 | Sửa đơn đã thanh toán | "Đơn đã thanh toán, không thể sửa" |
| `INSUFFICIENT_STOCK` | 409 | Hết nguyên liệu | "Không đủ nguyên liệu để pha món này" |

## 4. Ví dụ đầy đủ

### 4.1 `POST /auth/login`

```json
// Request
{ "username": "thungan01", "password": "••••••" }

// 200 OK
{
  "data": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "bearer",
    "user": { "id": 3, "username": "thungan01", "full_name": "Trần Thị B", "role": "staff" }
  },
  "meta": null
}
```

### 4.2 `GET /products?search=trà&category_id=2&page=1`

```json
{
  "data": [
    { "id": 12, "name": "Trà đào cam sả", "category": "Trà trái cây", "price": 35000,
      "unit": "ly", "is_available": true, "image_url": "/assets/products/tra-dao.jpg" }
  ],
  "meta": { "page": 1, "page_size": 20, "total": 7, "total_pages": 1 }
}
```

### 4.3 Lỗi

```json
{
  "error": {
    "code": "PRODUCT_NAME_DUPLICATED",
    "message": "Tên món đã tồn tại",
    "details": { "field": "name", "value": "Trà đào cam sả" }
  }
}
```

### 4.4 `POST /public/orders` (Kiosk khách hàng)

```json
// Request
{
  "table_id": 3,
  "notes": "Ít ngọt",
  "items": [
    { "product_id": 4, "quantity": 2, "notes": "50% đường, Ít đá" }
  ]
}

// 201 Created
{
  "data": {
    "id": 121,
    "order_code": "ORD-20261118-001",
    "table_id": 3,
    "table_number": "Bàn 03",
    "status": "pending",
    "total_amount": 70000,
    "notes": "[Kiosk] Ít ngọt",
    "qr_payload": "CAFETLU|VIETQR|ORD-20261118-001|70000",
    "created_at": "2026-11-18T13:50:00",
    "items": [
      {
        "id": 251,
        "product_id": 4,
        "product_name": "Trà đào cam sả",
        "unit": "ly",
        "quantity": 2,
        "unit_price": 35000,
        "subtotal": 70000,
        "notes": "50% đường, Ít đá"
      }
    ]
  },
  "meta": null
}
```
