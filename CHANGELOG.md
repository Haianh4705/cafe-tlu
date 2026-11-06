# Changelog

Mọi thay đổi đáng chú ý của dự án được ghi ở đây.
Định dạng theo [Keep a Changelog](https://keepachangelog.com/vi/1.1.0/),
phiên bản theo [Semantic Versioning](https://semver.org/lang/vi/).

> Quy tắc: mỗi PR đổi hành vi thêm **1 dòng** vào mục `Unreleased` (WORKFLOW.md mục 13.5).

## [Unreleased]

### Added — hạ tầng & công cụ
- `Makefile` (17 lệnh, tự dò `python3.12` và Docker CLI), `docker-compose.yml` (MySQL 8.0, cổng 3307,
  Adminer ở profile `tools`), `requirements*.txt` pin phiên bản, `pyproject.toml` (ruff/black/pytest/coverage)
- `pre-commit` 11 hook: chặn secret, file lớn, `.env`, commit lên `main`/`develop`; format ruff/black
- CI 2 job (`Lint & format`, `Test` với MySQL service + Qt headless) và pipeline đóng gói
  Windows trên `windows-latest` (tự bật khi có `installer/*.iss`)
- Khung 10 thư mục code (`api/`, `gui/`, `db/`, `shared/`, `tests/`, `scripts/`, `infra/`,
  `installer/`, `assets/`, `report/`) — mỗi thư mục có README nêu owner, đặt gì, **không** đặt gì

### Added — quy trình & tài liệu
- `docs/plan.md` — kế hoạch 8 tuần: mục tiêu + cổng từng tuần, thứ tự giao việc theo "sóng",
  thứ tự cắt scope khi trễ, việc điều phối của D
- `WORKFLOW.md` — quy chuẩn làm việc cho người và AI (nguồn chân lý)
- `AGENTS.md` — điểm vào cho AI agent + bảng định tuyến "sắp làm gì → đọc skill nào"
- `CONTRIBUTING.md`, `docs/standup.md`, `docs/setup-github.md`
- `docs/erd.md` — **chốt v1**: 9 bảng, từ điển dữ liệu, 7 bất biến dữ liệu, kế hoạch seed
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

## [0.1.0] — 2026-11-04

### Added
- Khởi tạo repository.
- Thiết lập môi trường phát triển dùng chung: Python 3.12, Docker cho MySQL,
  pre-commit, ruff + black, pytest.
- Thiết lập quy trình GitHub: bảo vệ nhánh `main`/`develop`, yêu cầu review, CI bắt buộc.
