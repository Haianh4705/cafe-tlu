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
| 2026-11-11 | #19 | feat(api) | `api/main.py`, `shared/error_codes.py`, `shared/errors.py` | Tạo khung FastAPI app, chuẩn hoá envelope lỗi và endpoint `/health` | Giúp GUI và Docker có thể kiểm tra sống đồng thời định hình format lỗi chung |
| 2026-11-11 | #20 | feat(api) | `api/core/config.py`, `api/core/db.py`, `api/routers/health.py` | Đọc cấu hình từ `.env` qua Pydantic Settings và kiểm tra kết nối MySQL trong `/health` | Tách biệt cấu hình khỏi code, không hardcode secret và báo lỗi 503 khi mất DB |

## 3. AI đã làm gì

| Ngày | Công cụ | AI làm gì | Tôi sửa / kiểm chứng gì |
|---|---|---|---|
| 2026-11-11 | Antigravity AI | Sinh boilerplate cho `api/main.py`, `config.py`, `db.py`, `shared/errors.py` và test | Kiểm tra format envelope theo WORKFLOW mục 9.3, kiểm thử 5 test cases bằng pytest |

## 4. Câu hỏi thầy hay hỏi (vùng A)

> Lấy từ [`defense.md`](../defense.md) mục A. Điền dần, câu nào chưa trả lời được thì để trống —
> đó chính là việc cần học.

| # | Câu hỏi | Trả lời ngắn (2–4 câu) | Chỉ vào |
|---|---|---|---|
| 1 | JWT là gì? Token chứa gì? Hết hạn thì sao? | Token xác thực không trạng thái (stateless) gồm Header.Payload.Signature. Payload lưu `sub` (user_id), `role`, `exp`. Hết hạn access token thì dùng refresh token gọi `/auth/refresh` để cấp lại mà không bắt user đăng nhập lại. | `api/core/security.py` |
| 2 | Phân quyền kiểm ở đâu? Sửa request có qua mặt được không? | Kiểm soát 100% tại backend bằng dependency `require_role(...)`. Cho dù client sửa request thì backend vẫn giải mã token và trả về 403 Forbidden nếu không đúng role. | `require_role` + test 403 |
| 3 | Vì sao router không viết SQL? | Tuân thủ tính phân tách trách nhiệm (SoC). Router chỉ validate input và format output. Đưa SQL vào router làm code rối, không tái sử dụng được và khó viết unit test độc lập. | `api/routers/` vs `api/services/` |
| 4 | Tạo đơn lỗi giữa chừng thì dữ liệu ra sao? | Toàn bộ thao tác ghi DB được bọc trong một Database Transaction (`db.begin()`). Nếu có lỗi ném ra, hệ thống rollback toàn bộ, không để lại bản ghi rác hay lệch dữ liệu. | transaction trong service |
| 5 | `Depends(get_db)` hoạt động thế nào? | Hoạt động theo cơ chế Dependency Injection và Generator Pattern của Python. Mỗi request đến sẽ mở `SessionLocal()`, yield session cho router/service, và tự động gọi `db.close()` trong khối finally khi request kết thúc. | `api/core/db.py` |
| 6 | Vì sao bọc `data`/`meta`/`error`? | Chuẩn hóa toàn bộ giao tiếp giữa API và client. GUI chỉ cần kiểm tra xem trường `error` có tồn tại không để hiển thị thông báo, `meta` phục vụ phân trang đồng bộ toàn hệ thống. | `WORKFLOW.md` mục 9.3 |
| 7 | 401 khác 403 ở đâu? | 401 (Unauthenticated) là chưa chứng minh được danh tính (chưa đăng nhập hoặc token sai/hết hạn). 403 (Forbidden) là đã biết danh tính nhưng tài khoản không có quyền thực hiện thao tác này. | `shared/error_codes.py` |
| 8 | Chống SQL injection bằng gì? | Sử dụng SQLAlchemy ORM Parameterized Query và bind parameter. Dữ liệu từ người dùng luôn được đối xử như giá trị tham số thuần túy, tuyệt đối không dùng f-string nối chuỗi SQL. | ORM / bind param |

## 5. Chưa làm / chưa hiểu

- [x] Đã hoàn thành khung FastAPI và `/health` (Issue #19 & #20).
- [ ] Chờ B hoàn thiện `docs/erd.md` và `db/schema.sql` để triển khai SQLAlchemy Models (#21).

## 6. Nhật ký theo cổng

| Cổng | Ngày | Đã xong gì | Còn thiếu gì |
|---|---|---|---|
| G1 | 2026-11-11 | Xong #19 (khung FastAPI), #20 (kết nối DB + config) | #21 (Models - chờ B), #22 (Auth JWT) |
| G2 | | | |
| G3 | | | |
