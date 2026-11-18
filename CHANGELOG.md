# Changelog

Mọi thay đổi đáng chú ý của dự án được ghi ở đây.
Định dạng theo [Keep a Changelog](https://keepachangelog.com/vi/1.1.0/),
phiên bản theo [Semantic Versioning](https://semver.org/lang/vi/).

> Quy tắc: mỗi PR đổi hành vi thêm **1 dòng** vào mục `Unreleased` (WORKFLOW.md mục 13.5).

## [Unreleased]

### Changed — Quy trình nhóm
- Chuyển quy trình sang gán thành viên theo chức năng (`ADR-014`), bỏ bắt buộc approve trên GitHub (`required_approving_review_count = 0`) và bật `enforce_admins: true` để mọi chức năng đi qua Issue & PR (#90)

### Fixed — CI
- Buộc CI fail khi mất kết nối MySQL test (không skip ngầm) và bổ sung smoke test nạp `db/schema.sql`, `db/seed.sql` (2 lần idempotent), `db/verify_seed.sql` 23/23 PASS (#85)
- Cập nhật thư viện: `fastapi` 0.162.5 (sửa dọn dependency khi cancel), `pymysql` 1.2.4, `ruff` 0.17.5 — thay PR dependabot #57 bị conflict sau khi #45 được squash (#57)
- `Test` job không còn treo vô hạn khi `apt-get` gặp mirror chậm: `timeout-minutes` cho job
  (lint 10', test 15', release 45') + `Acquire::Retries/Timeout/ForceIPv4` và `timeout` cho apt (#52)

### Added — backend (API)
- Khung FastAPI Backend (`api/main.py`): Khởi tạo FastAPI app, cấu hình CORS, xử lý ngoại lệ chung bọc envelope `error` (`AppError` và `RequestValidationError`), tự sinh Swagger tại `/docs` (#19)
- Cấu hình & kết nối MySQL (`api/core/config.py`, `api/core/db.py`): Đọc cấu hình từ `.env` bằng `pydantic-settings`, dependency `get_db` cấp Session SQLAlchemy, endpoint `/health` kiểm tra sống và trạng thái kết nối MySQL, trả phẳng `status`/`version`/`database` theo ADR-011 (#20)
- Định nghĩa mã lỗi và exception dùng chung: `shared/error_codes.py` (hằng số `ErrorCode`) và `shared/errors.py` (`AppError`) (#19)
- Models SQLAlchemy cho 9 bảng theo ERD v1 (`api/models/`): khoá ngoại `ON DELETE`, index, CHECK, cột sinh `active_name`/`open_table_id`; test metadata + compile DDL MySQL (`tests/test_models.py`) (#21)
- CRUD thực đơn theo `docs/api-contract.md` #6-#12 (`api/routers/categories.py`, `api/routers/products.py`, `api/services/`): danh sách + tìm kiếm + lọc danh mục + phân trang, tạo/sửa món (admin), xoá mềm bằng `deleted_at`, chặn trùng tên `409 PRODUCT_NAME_DUPLICATED` (#29)
- Schema request/response cho thực đơn (`api/schemas/category.py`, `api/schemas/product.py`): `ProductOut` trả `category` + `category_id` cho GUI, `ProductUpdate` cho PATCH từng phần (#29)
- 13 test CRUD thực đơn trên MySQL test (`tests/test_products.py`): envelope + phân trang, search/lọc, 403 cho `staff`, 422, trùng tên, 404, xoá mềm và cho phép tạo lại tên cũ (#29)

### Added — xác thực (Auth)
- Bảng thứ 10 `refresh_tokens` (`token_hash` SHA-256 UNIQUE, `expires_at`, `revoked_at`, `replaced_by_id`, 2 `CHECK`) để logout/rotate **thu hồi được** token; chỉ lưu hash, seed không tạo token (ADR-013, #22)
- Model `RefreshToken` + quan hệ `User.refresh_tokens`, test metadata/DDL cập nhật đủ 10 bảng (`api/models/refresh_token.py`, `tests/test_models.py`) (#22)
- `api/core/security.py`: băm mật khẩu bcrypt cost 12, access token JWT 30 phút, dependency `get_current_user` (Bearer) và `require_role(...)` kiểm quyền ở server (#22)
- 4 endpoint `/auth/login`, `/auth/refresh`, `/auth/logout`, `/auth/me`: login phát cặp token, refresh xoay vòng token cũ (`revoked_at` + `replaced_by_id`), logout thu hồi token; response bọc envelope `data`/`meta` (#22)
- Test auth: 5 unit (bcrypt 12, JWT hết hạn, `require_role` 403) + 9 test DB (login sai trả cùng thông điệp, audit `LOGIN_FAILED`, refresh rotation, logout → 401, `staff` bị 403), fixture tự skip nếu không có MySQL `*_test` (`tests/test_auth.py`, `tests/conftest.py`) (#22)

### Added — cơ sở dữ liệu & báo cáo (Data & Reports)
- Thiết kế ERD 9 bảng chuẩn hóa 3NF, từ điển dữ liệu, bất biến nghiệp vụ và snapshot đơn giá (`docs/erd.md`, #17)
- DDL Schema MySQL 8.0/InnoDB/utf8mb4 đầy đủ ràng buộc khóa ngoại, chỉ mục và xóa mềm (`db/schema.sql`, #17)
- Dữ liệu mẫu idempotent (`db/seed.sql`) với 3 vai trò, 5 tài khoản bcrypt (mật khẩu `123456`), 6 danh mục, 51 món ăn uống, 12 bàn phục vụ (#18) và 120 đơn hàng mẫu trải dài 30 ngày
- Script sinh tự động 120 đơn hàng & hoá đơn mẫu có kiểm soát tính nhất quán (`scripts/seed_data.py`, #28)
- Module dịch vụ thống kê doanh thu theo ngày, top món bán chạy, theo danh mục và xuất file Excel/PDF chuẩn nhận diện TLU (`api/services/reports.py`, #31)
- Bộ unit test kiểm thử hàm thống kê và xuất file báo cáo (`tests/test_reports.py`)
- Bật tự động nạp `schema.sql` và `seed.sql` trong `docker-compose.yml` khi khởi tạo container MySQL
- Nhật ký cá nhân và ngân hàng phản biện của B (`docs/log/B.md`)
- Chương 3 Báo cáo BTL về Phân tích & Thiết kế CSDL đạt chuẩn 3NF (`report/03-phan-tich.md`)

### Changed — cơ sở dữ liệu (ràng buộc ở tầng DB)

- `products` xoá mềm bằng `deleted_at` + cột ảo `active_name` UNIQUE: xoá "Trà đào" rồi tạo lại món
  cùng tên được, nhưng không thể có hai món đang bán cùng tên (`db/schema.sql`)
- `orders.open_table_id` (cột ảo) + UNIQUE: mỗi bàn chỉ được **một đơn đang mở**
- 9 `CHECK` thay cho quy ước bằng lời: `subtotal = quantity × unit_price`, `final = subtotal − discount`,
  `change = paid − final`, `paid ≥ final`, trạng thái đơn/dòng món/bàn, phương thức thanh toán
- Index ghép cho báo cáo: `orders(status, created_at)`, `order_items(order_id, status)`,
  `invoices(paid_at, order_id)`, `audit_logs(entity_type, entity_id)`; `audit_logs.details` đổi sang `JSON`
- Sửa **3 mã trùng** (`ORD-20261110-001` ×2, `ORD-20261111-002` ×2, `INV-20261110-001` ×2) từng làm
  `ON DUPLICATE KEY UPDATE` ghi đè 2 đơn và 1 hoá đơn → seed giờ đủ **120 đơn / 119 hoá đơn, 0 trùng**
- Thêm `db/verify_seed.sql`: 21 phép kiểm PASS/FAIL (đếm dòng, mã trùng, lệch tổng tiền, mồ côi, 30 ngày)

### Added — quy trình
- **Nhật ký cá nhân bắt buộc:** `docs/log/A.md` … `D.md` — mỗi người ghi việc đã làm, AI đã hỗ trợ
  gì, câu hỏi thầy hay hỏi, phần còn chưa hiểu; cập nhật trong mỗi PR, rà trước mỗi cổng
  (`docs/log/README.md`, `WORKFLOW.md` 6.2 + 12.5 + 15.7, `AGENTS.md` điều 11)
- `docs/defense-D.md`: bản ôn bảo vệ phần D (Docker, CI, đóng gói, QA) kèm đáp án mẫu và giới hạn
  phải thừa nhận

### Changed
- `docs/plan.md` chuyển từ **kế hoạch 8 tuần** sang **lộ trình theo cổng G1–G6**: bỏ mốc tuần/ngày,
  mỗi cổng mở khi đủ điều kiện; cập nhật theo `README.md`, `WORKFLOW.md` (16.3), `docs/workflow.md`,
  `docs/setup-github.md` (milestone `G1`–`G6`), skill `next-task` và bảng điều khiển #33/#34

### Added — giao diện (GUI)
- Màn hình Tổng quan (`DashboardView`): 4 thẻ KPI (doanh thu hôm nay, số đơn hôm nay, doanh thu 30 ngày, món bán chạy nhất) và 2 biểu đồ QtCharts (doanh thu theo ngày, top 5 món bán chạy); dựng bằng dữ liệu `MOCK_*` khi `APP_ENV=demo`, chờ endpoint `GET /reports/revenue` và `GET /reports/top-products`
- Màn hình Bán hàng & Gọi món tại bàn (`OrderView`): giao diện POS 3 cột khoa học (sơ đồ bàn `TableCardWidget`, thực đơn món phân loại danh mục và tìm kiếm nhanh `Ctrl+F`/`F1`, giỏ hàng `OrderCartWidget` tính toán thành tiền tức thời, hộp thoại thanh toán `CheckoutDialog` tính tiền thối lại và hộp thoại in/xuất phiếu thanh toán K80 `ReceiptDialog` chuẩn nhận diện TLU)
- Màn hình Quản lý thực đơn (`ProductListView`): bảng danh sách món, bộ lọc danh mục động, tìm kiếm nhanh `Ctrl+F`, phân trang, cùng bộ hộp thoại CRUD thêm/sửa/xoá món ăn chuẩn nhận diện TLU (#41, Closes #30)
- Khung giao diện desktop PySide6: theme nhận diện TLU (palette navy `#000066` + swoosh đỏ `#F32409`), BaseView 4 trạng thái bắt buộc, ApiClient bọc 23 endpoint, màn hình Đăng nhập (`LoginView`) phân quyền vai trò (`admin`/`staff`/`barista`), nhúng font Manrope và tài liệu ảnh chụp (#40, Closes #23, #24, #25)

### Added — hạ tầng & công cụ
- Job `verify-installer`: cài bộ cài `.exe` vừa build lên runner `windows-latest` (máy Windows sạch),
  chạy app, chụp ảnh cửa sổ bằng `PrintWindow`, gỡ cài và kiểm thư mục đã sạch; báo cáo 11 bước
  đưa vào Summary + artifact 30 ngày (`scripts/verify_installer.ps1`, #26)
- Bộ cài Windows: `installer/cafetlu.spec` (PyInstaller onedir, nhúng `assets/`), `cafetlu.iss`
  (Inno Setup, cài per-user, shortcut + uninstall), `app.ico` 7 kích thước, `scripts/build_installer.sh`
  và `scripts/make_icon.py`; version lấy duy nhất từ `shared/version.py` (#26)
- `Release` workflow: build bằng script chung, tải được artifact `CafeTLU-Setup` cả khi chạy tay
  (`workflow_dispatch`), không chỉ khi push tag
- Nhãn "Phiên bản" ở sidebar GUI đọc từ `shared/version.py` (hết hard-code `1.0`)
- `make doctor` kiểm thêm MySQL **healthy** + cổng 3307 mở + `infra/Dockerfile`; thêm `infra/Dockerfile`
  (Python 3.12-slim, user không phải root, healthcheck `/health`) và khung `infra/docker-compose.prod.yml` (#27)
- `make next` + `scripts/next_task.sh`: in việc tiếp theo của mỗi người từ Issue được gán,
  sắp theo milestone rồi số Issue (thứ tự phụ thuộc), kèm skill phải đọc
- Skill `next-task`: dạy AI agent trả lời "tôi cần làm gì?" theo đúng khuôn, không tự bịa việc
- `Makefile` (17 lệnh, tự dò `python3.12` và Docker CLI), `docker-compose.yml` (MySQL 8.0, cổng 3307,
  Adminer ở profile `tools`), `requirements*.txt` pin phiên bản, `pyproject.toml` (ruff/black/pytest/coverage)
- `pre-commit` 11 hook: chặn secret, file lớn, `.env`, commit lên `main`/`develop`; format ruff/black
- CI 2 job (`Lint & format`, `Test` với MySQL service + Qt headless) và pipeline đóng gói
  Windows trên `windows-latest` (tự bật khi có `installer/*.iss`)
- Khung 10 thư mục code (`api/`, `gui/`, `db/`, `shared/`, `tests/`, `scripts/`, `infra/`,
  `installer/`, `assets/`, `report/`) — mỗi thư mục có README nêu owner, đặt gì, **không** đặt gì

### Added — quy trình & tài liệu
- Khung báo cáo BTL đủ 10 chương trong `report/` (`00-bia.md` → `09-huong-phat-trien.md`): mục lục dự kiến, phân công theo vai A/B/C/D, gắn cổng G2–G5 và danh sách ảnh khớp `docs/screenshots/` (#32)
- `docs/plan.md` — lộ trình theo cổng: mục tiêu + điều kiện ra cổng, thứ tự giao việc theo "sóng",
  thứ tự cắt scope khi trễ, việc điều phối của D
- `WORKFLOW.md` — quy chuẩn làm việc cho người và AI (nguồn chân lý)
- `AGENTS.md` — điểm vào cho AI agent + bảng định tuyến "sắp làm gì → đọc skill nào"
- `CONTRIBUTING.md`, `docs/standup.md`, `docs/setup-github.md`
- `docs/erd.md` — **khung** thiết kế dữ liệu: quy ước bắt buộc, khung để điền, 6 câu hỏi tự kiểm,
  deliverable. **B tự thiết kế** (nhóm cố ý không có bản ERD viết sẵn)
- `docs/api-contract.md` — **chốt v1**: 23 endpoint, envelope `data/meta/error`, 7 mã lỗi
- `docs/workflow.md` — sơ đồ bàn giao giữa 4 vai trò, "xong việc gì → đến ai", SLA review
- `docs/defense.md` — ngân hàng 48 câu hỏi bảo vệ theo vùng + 6 câu bẫy + hỏi chéo thứ 6
- `docs/decisions.md` — 8 ADR (stack, Docker 3307, build trên CI, palette TLU, tối giản…)
- `docs/test-cases.md` — 24 ca kiểm thử khung, sẵn PASS/FAIL
- `CHANGELOG.md`, `README.md`, template Issue/PR, `CODEOWNERS`, Dependabot

### Added — skill & quy ước
- **9 skill trong `.claude/skills/`**: `minimal-change`, `fastapi-endpoint`, `sqlalchemy-model`,
  `pyside6-screen`, `ui-design` (nhận diện TLU + chống "AI slop"), `pytest-db`, `win-installer`,
  `report-export`, `security`
- Quy ước comment `shortcut: <giới hạn>, <khi nào nâng cấp>` để gom nợ kỹ thuật (WORKFLOW 7.1)
- Cơ chế "hiểu bài": mục **"Giải thích được" 3 câu** bắt buộc trong template PR (WORKFLOW 6.3)

### Changed
- **Bỏ bản ERD viết sẵn**: `docs/erd.md` chuyển thành khung, B (Data & Reports) tự thiết kế trước khi
  viết `db/schema.sql` — để hiểu và bảo vệ được trước GV (đề bài: copy = 0 điểm). Mọi tài liệu
  liên quan (WORKFLOW, AGENTS, plan, workflow, defense, skills, db/README) đã cập nhật theo.
- **Chốt phân vai**: A = @bao20062005dh-creator (backend) · B = @trungdunxg (data/reports) ·
  C = @MeoCamGuitar (GUI) · D = @Haianh4705 (infra/QA/docs) — 16 issue đã gán assignee, chia theo
  sóng phụ thuộc; `CODEOWNERS` điền tên thật (ADR-009)
- Repo chuyển sang **public** → bật được branch protection cho `main`/`develop`
  (1 approval, CI bắt buộc, linear history, squash-only, không force-push)
- Dependabot: không tự bump major, gom minor+patch 1 PR/tuần, giới hạn 2 PR
- Actions nâng lên `checkout@v7`, `setup-python@v7`, `action-gh-release@v3` (hết cảnh báo Node 20)
- `ui-design` viết lại theo token CSS thật của `thanglong.edu.vn` + logo chính thức
- Checklist review gom về **một nguồn duy nhất** (WORKFLOW 18.3); template Issue/PR trỏ về `.github/`

### Fixed
- Cấu hình Alembic (`alembic.ini`, `db/migrations/`) kèm 2 revision `0001`/`0002` nâng cấp volume MySQL cũ trước `#69` thêm bảng `refresh_tokens` mà không mất dữ liệu (#78)
- `/auth/logout` nhận body **tuỳ chọn**: client không gửi `refresh_token` (như `gui/api_client`) sẽ thu hồi **mọi phiên** của user thay vì trả 422 (#22)
- `make install` chạy pip nhầm vào Python hệ thống (PEP 668) — nay dùng đúng python của `.venv`
- `make up`/`down`/`logs`/`tools` không tìm thấy Docker CLI và credential helper khi
  `~/.docker/bin` chưa trong PATH (macOS) — Makefile tự dò, dùng đường dẫn tuyệt đối
  (GNU make 3.81 fast-path không áp dụng PATH đã export cho lệnh "trơn")
- CI job `Test` lỗi `INTERNALERROR` vì thiếu `libEGL.so.1` — thêm bước cài thư viện Qt +
  `QT_QPA_PLATFORM=offscreen`
- Đồng bộ phiên bản ruff giữa `requirements-dev.txt` và pre-commit hook (0.17.3)
- CI job `Test` báo `ModuleNotFoundError: No module named 'gui'` khi chạy `pytest` trực tiếp —
  thêm `pythonpath = ["."]` vào cấu hình pytest để root repo luôn nằm trên `sys.path` (#42)

## [0.1.0] — 2026-11-04

### Added
- Khởi tạo repository.
- Thiết lập môi trường phát triển dùng chung: Python 3.12, Docker cho MySQL,
  pre-commit, ruff + black, pytest.
- Thiết lập quy trình GitHub: bảo vệ nhánh `main`/`develop`, yêu cầu review, CI bắt buộc.
