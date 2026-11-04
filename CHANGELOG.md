# Changelog

Mọi thay đổi đáng chú ý của dự án được ghi ở đây.
Định dạng theo [Keep a Changelog](https://keepachangelog.com/vi/1.1.0/),
phiên bản theo [Semantic Versioning](https://semver.org/lang/vi/).

> Quy tắc: mỗi PR đổi hành vi thêm **1 dòng** vào mục `Unreleased` (WORKFLOW.md mục 13.5).

## [Unreleased]

### Added
- Khung hạ tầng dự án: `Makefile`, `docker-compose` (MySQL 8.0, cổng 3307), `requirements*.txt`
- Quy chuẩn làm việc `WORKFLOW.md` và điểm vào cho AI `AGENTS.md`
- CI (lint + test) và pipeline đóng gói Windows (bật khi có `installer/*.iss`)
- Template Issue/PR, `CODEOWNERS`, Dependabot, pre-commit hooks
- Khung tài liệu: `docs/api-contract.md`, `docs/erd.md`, `docs/decisions.md`, `docs/test-cases.md`, `docs/setup-github.md`

## [0.1.0] — 2026-11-04

### Added
- Khởi tạo repository.
- Thiết lập môi trường phát triển dùng chung: Python 3.12, Docker cho MySQL,
  pre-commit, ruff + black, pytest.
- Thiết lập quy trình GitHub: bảo vệ nhánh `main`/`develop`, yêu cầu review, CI bắt buộc.
