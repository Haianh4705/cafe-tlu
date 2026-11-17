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
| 2026-11-17 | #21 | #65 (merged) | `api/models/` (9 bảng), `tests/test_models.py` | Viết SQLAlchemy models khớp ERD v1 và test metadata/DDL | Dùng chung `Base` ở `api/core/db.py`, test không cần MySQL nên CI chạy nhanh |
| 2026-11-17 | #22 | #71 (merged) | `api/core/security.py`, `api/routers/auth.py`, `api/services/auth.py`, `api/models/refresh_token.py`, `tests/test_auth.py`, `tests/conftest.py` | Làm login/refresh/logout/me: bcrypt 12, JWT 30 phút, refresh token lưu hash + rotation, `require_role` kiểm quyền | Lưu hash thay token thô và thu hồi được khi logout (ADR-013); envelope `data`/`meta` theo hợp đồng |
| 2026-11-17 | #22 (fix) | `fix/api-logout-optional-body` | `api/schemas/auth.py`, `api/services/auth.py`, `api/routers/auth.py`, `tests/test_auth.py` | Nới `/auth/logout` cho body tuỳ chọn; không gửi token thì thu hồi mọi phiên | GUI `api_client.logout()` gọi không body → giữ hành vi thu hồi thật thay vì bắt C sửa client |

## 3. AI đã làm gì

| Ngày | Công cụ | AI làm gì | Tôi sửa / kiểm chứng gì |
|---|---|---|---|
| 2026-11-11 | Antigravity AI | Sinh boilerplate cho `api/main.py`, `config.py`, `db.py`, `shared/errors.py` và test | Kiểm tra format envelope theo WORKFLOW mục 9.3, kiểm thử 5 test cases bằng pytest |
| 2026-11-17 | Command Code | Scaffold 9 model + `tests/test_models.py` từ `docs/erd.md` và `db/schema.sql` | Tự đối chiếu từng cột/FK/index với schema, chạy `configure_mappers()` và compile DDL MySQL, 39 test pass |
| 2026-11-17 | Command Code | Viết `security.py`, service/router auth, model `refresh_tokens` và 14 test auth theo DDL D chốt | Tự kiểm OpenAPI, chạy ruff/black/pytest; test DB skip ở máy local vì chưa có Docker, chờ CI xác nhận |

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

- [x] #19/#20 (PR #56) và #21 (PR #65) đã merge vào `develop`.
- [x] #22: login/refresh/logout/me + bcrypt cost 12 + `require_role`; 9 test DB tự skip ở máy local, CI sẽ chạy.
- [ ] Chưa kiểm `Base.metadata.create_all` / Alembic autogenerate trên MySQL thật — cần cài Docker Desktop (máy hiện chưa có).
- [ ] Rate limit `/auth/login` chưa làm: cần mã lỗi 429 mới + cập nhật contract bằng PR riêng (để G4).

## 6. Nhật ký theo cổng

| Cổng | Ngày | Đã xong gì | Còn thiếu gì |
|---|---|---|---|
| G1 | 2026-11-17 | #19/#20, #21 đã merge; #22 auth + phân quyền xong (chờ PR) | PR #22 chờ approve + CI; `make doctor` 4/4 máy (D); rate limit login để G4 |
| G2 | | | |
| G3 | | | |
