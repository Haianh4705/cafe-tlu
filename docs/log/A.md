# Nhật ký — A (Backend / API)

> Quy tắc + mẫu: [`README.md`](README.md). Cập nhật trong PR đã làm việc, không dồn.
> **Người giữ file:** A — @bao20062005dh-creator. Người khác không sửa hộ.

**Vùng:** `api/`, `shared/` · **Bắt đầu:** G1

## 1. Tôi phụ trách gì

- Khung FastAPI + `/health` (#19), config + kết nối MySQL (#20), models SQLAlchemy theo ERD của B (#21)
- Auth JWT + phân quyền `admin`/`staff` (#22)
- CRUD `products` + `categories` (#29), sau đó orders/hoá đơn (G3)
- `docs/api-contract.md` — hợp đồng API, cập nhật mỗi khi đổi endpoint

## 2. Việc đã làm

| Ngày | Issue | PR / commit | File chính | Làm gì (1 câu) | Vì sao cách đó (1 câu) |
|---|---|---|---|---|---|
| | | | | | |

## 3. AI đã làm gì

| Ngày | Công cụ | AI làm gì | Tôi sửa / kiểm chứng gì |
|---|---|---|---|
| | | | |

## 4. Câu hỏi thầy hay hỏi (vùng A)

> Lấy từ [`defense.md`](../defense.md) mục A. Điền dần, câu nào chưa trả lời được thì để trống —
> đó chính là việc cần học.

| # | Câu hỏi | Trả lời ngắn (2–4 câu) | Chỉ vào |
|---|---|---|---|
| 1 | JWT là gì? Token chứa gì? Hết hạn thì sao? | | `api/core/security.py` |
| 2 | Phân quyền kiểm ở đâu? Sửa request có qua mặt được không? | | `require_role` + test 403 |
| 3 | Vì sao router không viết SQL? | | `api/routers/` vs `api/services/` |
| 4 | Tạo đơn lỗi giữa chừng thì dữ liệu ra sao? | | transaction trong service |
| 5 | `Depends(get_db)` hoạt động thế nào? | | `api/core/db.py` |
| 6 | Vì sao bọc `data`/`meta`/`error`? | | `WORKFLOW.md` mục 9.3 |
| 7 | 401 khác 403 ở đâu? | | `shared/error_codes.py` |
| 8 | Chống SQL injection bằng gì? | | ORM / bind param |

## 5. Chưa làm / chưa hiểu

- [ ] `api/` chưa có code — `/health` chưa tồn tại nên `HEALTHCHECK` trong `infra/Dockerfile` sẽ báo
      unhealthy cho tới khi #19 xong (D đã biết, không cần báo lại)
- [ ] _(ghi những chỗ mình chưa giải thích được — dùng làm danh sách ôn)_

## 6. Nhật ký theo cổng

| Cổng | Ngày | Đã xong gì | Còn thiếu gì |
|---|---|---|---|
| G1 | | | |
| G2 | | | |
| G3 | | | |
