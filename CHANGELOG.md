# Changelog

Mọi thay đổi đáng chú ý của dự án được ghi ở đây.
Định dạng theo [Keep a Changelog](https://keepachangelog.com/vi/1.1.0/),
phiên bản theo [Semantic Versioning](https://semver.org/lang/vi/).

> Quy tắc: mỗi PR đổi hành vi thêm **1 dòng** vào mục `Unreleased` (WORKFLOW.md mục 13.5).

## [Unreleased]

### Changed
- `docs/plan.md` chuyển từ **kế hoạch 8 tuần** sang **lộ trình theo cổng G1–G6**: bỏ mốc tuần/ngày,
  mỗi cổng mở khi đủ điều kiện; cập nhật theo `README.md`, `WORKFLOW.md` (16.3), `docs/workflow.md`,
  `docs/setup-github.md` (milestone `G1`–`G6`), skill `next-task` và bảng điều khiển #33/#34

### Added — giao diện (GUI)
- Màn hình Quản lý thực đơn (`ProductListView`): bảng danh sách món, bộ lọc danh mục động, tìm kiếm nhanh `Ctrl+F`, phân trang, cùng bộ hộp thoại CRUD thêm/sửa/xoá món ăn chuẩn nhận diện TLU (#41, Closes #30)
- Khung giao diện desktop PySide6: theme nhận diện TLU (palette navy `#000066` + swoosh đỏ `#F32409`), BaseView 4 trạng thái bắt buộc, ApiClient bọc 23 endpoint, màn hình Đăng nhập (`LoginView`) phân quyền vai trò (`admin`/`staff`/`barista`), nhúng font Manrope và tài liệu ảnh chụp (#40, Closes #23, #24, #25)

### Added — hạ tầng & công cụ
- Bộ cài Windows: `installer/cafetlu.spec` (PyInstaller onedir, nhúng `assets/`), `cafetlu.iss`
  (Inno Setup, cài per-user, shortcut + uninstall), `app.ico` 7 kích thước, `scripts/build_installer.sh`
  và `scripts/make_icon.py`; version lấy duy nhất từ `shared/version.py` (#26)
- `Release` workflow: build bằng script chung, tải được artifact `CafeTLU-Setup` cả khi chạy tay
  (`workflow_dispatch`), không chỉ khi push tag
- Nhãn "Phiên bản" ở sidebar GUI đọc từ `shared/version.py` (hết hard-code `1.0`)
- `make doctor` kiểm thêm MySQL container (cổng 3307) + `infra/Dockerfile`; thêm `infra/Dockerfile`
  (Python 3.12-slim, user không phải root, healthcheck `/health`) (#27)
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
