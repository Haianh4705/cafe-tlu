# Chương 6: Triển khai, Kiểm thử, Đóng gói & Deploy

> **Người phụ trách:** D (@Haianh4705) — Infra, QA & Docs Lead
> **Cổng gắn kết & Hạn hoàn thành:** G2/G3 (CI & bộ cài) → G4 (deploy backend) → G5 (chốt số liệu QA trước hạn nộp 3 ngày)
> **Độ dài dự kiến:** 3–5 trang

## Mục lục dự kiến

- `6.1` Mở đầu
- `6.2` Chuẩn hoá môi trường phát triển với Docker Compose & `Makefile`
- `6.3` Kiểm thử tự động & Đường ống CI/CD GitHub Actions
- `6.4` Đóng gói bộ cài Windows (`PyInstaller` + `Inno Setup`)
- `6.5` Triển khai Backend công khai & Tổng kết

## Nội dung dự kiến

- Container MySQL 8.0 ánh xạ cổng `3307` (ADR-004) và lệnh kiểm tra môi trường `make doctor` bắt buộc trên 3/3 máy A, C, D (ADR-012).
- Phân tầng kiểm thử `pytest` (unit, API, DB `_test`, GUI offscreen) trên `.github/workflows/ci.yml` kết hợp 24 ca kiểm thử ở `docs/test-cases.md`.
- Đóng gói `--onedir` qua `installer/cafetlu.spec` + `installer/cafetlu.iss` trên runner `windows-latest` (ADR-005) và kiểm thử cài/gỡ sạch bằng `scripts/verify_installer.ps1`.
- Triển khai `infra/Dockerfile` (user non-root, `HEALTHCHECK /health`), HTTPS, biến môi trường tách khỏi mã nguồn và sao lưu DB định kỳ ở G4.

## Danh sách ảnh cần chụp & minh chứng

- **Đã có:** `docs/screenshots/installer/gui-after-install.png` (kèm báo cáo 13 bước tại `docs/screenshots/installer/ci-run-report.md`).
- **Cần chụp (G4/G5):** `docs/screenshots/installer/setup-wizard-<YYYYMMDD>-01.png` (trình cài đặt trên máy Windows) và `docs/screenshots/infra/prod-health-<YYYYMMDD>-01.png` (API deploy trả `/health` 200).
