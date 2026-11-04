# Changelog

Mọi thay đổi đáng chú ý của dự án được ghi ở đây.
Định dạng theo [Keep a Changelog](https://keepachangelog.com/vi/1.1.0/),
phiên bản theo [Semantic Versioning](https://semver.org/lang/vi/).

> Quy tắc: mỗi PR đổi hành vi thêm **1 dòng** vào mục `Unreleased` (WORKFLOW.md mục 13.5).

## [Unreleased]

### Added
- `docs/workflow.md` — sơ đồ bàn giao giữa 4 vai trò, bảng "xong việc gì → đến ai",
  SLA review, việc nên làm khi đang chờ người khác
- **8 skill hướng dẫn trong `.claude/skills/`**: `fastapi-endpoint`, `sqlalchemy-model`,
  `pyside6-screen`, `ui-design` (chống "AI slop"), `pytest-db`, `win-installer`,
  `report-export`, `security`
- `AGENTS.md` mục 1.5: bảng định tuyến "sắp làm gì → đọc skill nào"
- Khung hạ tầng dự án: `Makefile`, `docker-compose` (MySQL 8.0, cổng 3307), `requirements*.txt`
- Quy chuẩn làm việc `WORKFLOW.md` và điểm vào cho AI `AGENTS.md`
- CI (lint + test) và pipeline đóng gói Windows (bật khi có `installer/*.iss`)
- Template Issue/PR, `CODEOWNERS`, Dependabot, pre-commit hooks
- Khung tài liệu: `docs/api-contract.md`, `docs/erd.md`, `docs/decisions.md`, `docs/test-cases.md`, `docs/setup-github.md`
- **Chốt hợp đồng API v1** (23 endpoint) — `docs/api-contract.md`
- **Chốt ERD v1** (9 bảng + từ điển dữ liệu + bất biến dữ liệu) — `docs/erd.md`

### Fixed
- `make install` chạy pip nhầm vào Python hệ thống (PEP 668) — nay dùng đúng python của `.venv`
- Đồng bộ phiên bản ruff giữa `requirements-dev.txt` và pre-commit hook (0.17.3)
- `make up`/`down`/`logs`/`tools` không tìm thấy Docker CLI và credential helper khi
  `~/.docker/bin` chưa nằm trong PATH (macOS Docker Desktop) — nay Makefile tự dò và dùng
  đường dẫn tuyệt đối, tránh cả lỗi của fast-path trong GNU make 3.81

### Changed
- `ui-design` viết lại theo **nhận diện TLU**: bảng màu lấy từ token CSS của `thanglong.edu.vn`
  + logo chính thức (navy `#000066`, đỏ logo `#F32409`, tint `#F1F5FF`), kèm ngưỡng tương phản
  WCAG cho từng cặp màu và luật "navy = hành động, đỏ = nguy hiểm"
- Repo chuyển sang **public** → bật được branch protection cho `main` và `develop`
  (1 approval + CI `Lint & format` & `Test` bắt buộc, linear history, squash-only)

## [0.1.0] — 2026-11-04

### Added
- Khởi tạo repository.
- Thiết lập môi trường phát triển dùng chung: Python 3.12, Docker cho MySQL,
  pre-commit, ruff + black, pytest.
- Thiết lập quy trình GitHub: bảo vệ nhánh `main`/`develop`, yêu cầu review, CI bắt buộc.
