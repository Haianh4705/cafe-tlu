# Nhật ký — D (Hạ tầng · CI/CD · Đóng gói · QA)

> Quy tắc + mẫu: [`README.md`](README.md). **File này là bản mẫu** — người khác làm theo độ chi tiết
> này (không cần dài hơn).
> **Người giữ file:** D — @Haianh4705.

**Vùng:** `infra/`, `installer/`, `.github/`, `docs/`, `report/`, `Makefile`, `docker-compose.yml`

## 1. Tôi phụ trách gì

- **Môi trường chạy giống nhau cho 4 máy:** `docker-compose.yml` (MySQL 8.0, host port 3307),
  `Makefile` (`up`/`doctor`/`reset-db`/`check`), `.env.example`, `.pre-commit-config.yaml`
- **Đóng gói backend:** `infra/Dockerfile` (non-root, `HEALTHCHECK`), khung `infra/docker-compose.prod.yml`
- **CI/CD:** `.github/workflows/ci.yml` (lint + test với MySQL thật), `release.yml` (build `.exe` trên
  `windows-latest`), bảo vệ nhánh `develop`, CODEOWNERS, template PR/Issue
- **Bộ cài Windows:** `installer/cafetlu.spec` (PyInstaller onedir) + `installer/cafetlu.iss` (Inno
  Setup) + `scripts/build_installer.sh` + `installer/app.ico`
- **Tài liệu & QA:** `docs/plan.md` (lộ trình theo cổng), `docs/workflow.md`, `docs/defense*.md`,
  `docs/test-cases.md`, `CHANGELOG.md`, biên tập `README.md` và báo cáo

## 2. Việc đã làm

| Ngày | Issue | PR / commit | File chính | Làm gì (1 câu) | Vì sao cách đó (1 câu) |
|---|---|---|---|---|---|
| 11-04 | — | #8 | `.github/dependabot.yml` | gom cập nhật thư viện theo nhóm hằng tuần | giảm 19 PR lẻ thành 1, đỡ nhiễu review |
| 11-04 | — | #10 | `Makefile` | `make up` tìm được Docker CLI + credential helper | Docker Desktop trên macOS không nạp `~/.docker/bin` vào PATH |
| 11-04 | — | #11, #37 | `.github/CODEOWNERS` | gán reviewer theo vùng A/B/C/D | owner vùng duy nhất nên không bật "require code owner review", tránh PR tự kẹt |
| 11-04 | — | #12, #14, #15 | `.claude/skills/*` | 8 skill hướng dẫn (minimal-change, ui-design, win-installer…) | quy tắc viết trong skill thì AI đọc được, trong chat thì mất |
| 11-05 | — | #16 | `shared/paths.py`, `docs/defense.md` | khung thư mục + cơ chế "giải thích được" | đề bài copy = 0 điểm → phải có chỗ ghi và chỗ hỏi |
| 11-06 | — | #38 | `docs/erd.md` | ERD thành **khung** để B tự thiết kế | D không được viết ERD hộ B (ranh giới vai) |
| 11-06 | — | #39 | `scripts/next_task.sh` | `make next` trả lời "việc tiếp theo của tôi" | giảm thời gian chờ D giao việc |
| 11-07 | #42 | #43 | `pyproject.toml` | thêm `pythonpath = ["."]` cho pytest | CI đỏ vì `ModuleNotFoundError: gui` — test import package từ gốc repo |
| 11-09 | #32 | #46 | `docs/plan.md` | thay kế hoạch 8 tuần bằng 6 cổng G1–G6 | tuần không kiểm chứng được; cổng thì kiểm bằng lệnh |
| 11-09 | #26 | #47 | `infra/Dockerfile`, `installer/*`, `scripts/build_installer.sh`, `release.yml` | build bộ cài `.exe` đầu tiên trên CI + đóng gói backend | đề bài bắt buộc có bộ cài, cả nhóm dùng macOS (ADR-005) |
| 11-09 | #27 | #48 | `Makefile`, `infra/docker-compose.prod.yml` | `doctor` đọc health MySQL + thử socket 3307; khung compose prod | container `running` vẫn chưa nhận truy vấn |
| 11-11 | — | — | `docs/defense-D.md`, `docs/log/` | tài liệu ôn bảo vệ + nhật ký cá nhân | kiến thức rải trong chat sẽ mất, phải nằm trong repo để cả nhóm dùng |
| 11-11 | — | — | `WORKFLOW.md`, `AGENTS.md`, `docs/log/` | thêm **nhật ký cá nhân bắt buộc** cho 4 người, nối vào DoD + PR template + cổng | kiến thức nằm trong chat sẽ mất; file trong repo thì lúc bảo vệ mở ra là có |

> Chi tiết từng quyết định: `docs/decisions.md` (ADR-003…005, 009, 010) · kết quả kiểm chứng:
> CI xanh, Release `v0.1.0` có `CafeTLU-Setup-v0.1.0.exe` (39,4 MB), `pytest` 15 passed.

## 3. AI đã làm gì

> Ghi thật. Đây là phần giảng viên hay hỏi nhất: "AI viết bao nhiêu, em hiểu gì?"

| Ngày | Công cụ | AI làm gì | Tôi sửa / kiểm chứng gì |
|---|---|---|---|
| 11-04 → 11-06 | AI agent trong repo (Claude/DSH) | soạn nháp `WORKFLOW.md`, `AGENTS.md`, 8 skill, README, `docs/defense.md` | đọc lại từng mục, bỏ phần không khớp đề bài; chốt phân vai A/B/C/D |
| 11-09 | AI agent | soạn nháp `infra/Dockerfile`, `.dockerignore`, `docker-compose.prod.yml`, `cafetlu.spec`, `cafetlu.iss`, `build_installer.sh`, `release.yml` | **sửa 3 lỗi thật:** (1) spec trỏ `SPECPATH.parent.parent` ra `~/Desktop` → `FileNotFoundError`; (2) Git Bash đổi `/DMyAppVersion` thành đường dẫn Windows → ISCC báo "more than one script filename", sửa bằng `MSYS_NO_PATHCONV=1`; (3) `doctor` chỉ kiểm container chạy → đổi sang health + socket. Kiểm chứng: build local ra `dist/CafeTLU/`, CI release xanh, chạy `make doctor` từng dòng |
| 11-09 | AI agent | soạn nháp `docs/plan.md` theo cổng, `docs/workflow.md` | tự viết lại phần điều kiện ra cổng cho đo được; bỏ toàn bộ mốc tuần |
| 11-11 | AI agent | soạn `docs/defense-D.md` + khung `docs/log/README.md` + 4 file A–D, nối quy tắc vào `WORKFLOW.md`/`AGENTS.md`/PR template | đối chiếu từng câu trả lời với code thật, sửa 4 số liệu sai (số ca kiểm thử, số dòng file, cổng compose); tự chốt 6 mục nhật ký, **không** thêm check CI tự động vì dễ chặn nhầm |

## 4. Câu hỏi thầy hay hỏi (vùng D)

> Bản đầy đủ: [`docs/defense-D.md`](../defense-D.md).

| # | Câu hỏi | Trả lời ngắn (2–4 câu) | Chỉ vào |
|---|---|---|---|
| 1 | Docker là gì? Vì sao dùng cho MySQL? | image là khuôn chỉ đọc, container là tiến trình chạy từ image; 4 máy dùng đúng 1 phiên bản MySQL 8.0, xoá sạch bằng 1 lệnh | `docker-compose.yml` |
| 2 | Vì sao cổng 3307 không 3306? | tránh đụng MySQL cài sẵn; chỉ đổi **host port**, trong container vẫn 3306 nên code không sửa | ADR-004, `docker-compose.yml:25-27` |
| 3 | `hiddenimports` để làm gì? | PyInstaller dò import tĩnh nên bỏ sót import động/plugin Qt → thiếu là `ModuleNotFoundError` chỉ trên máy đã đóng gói | `installer/cafetlu.spec:33-38` |
| 4 | Vì sao `--onedir` không `--onefile`? | onefile giải nén ra `%TEMP%` mỗi lần chạy: chậm 3–10 s và dễ bị Defender cách ly | `cafetlu.spec:69-76` |
| 5 | App đọc ảnh thế nào khi đã đóng gói? | khai `datas` trong spec; `resource_path` kiểm `sys._MEIPASS` để biết frozen hay dev | `shared/paths.py:7-16` |
| 6 | CI làm gì? Mấy job? Khi nào chạy? | 2 job lint + test (MySQL 8.0 trong service container), chạy mọi PR và push vào `main`/`develop` | `.github/workflows/ci.yml` |
| 7 | Build `.exe` khi cả nhóm dùng macOS thế nào? | tag `v*` → `windows-latest` chạy PyInstaller + Inno Setup → đính vào Release | `release.yml`, ADR-005 |
| 8 | Đã chạy bao nhiêu test case, pass bao nhiêu? | 24 ca thiết kế, **0 PASS end-to-end** (chưa có API/DB), 15 unit test xanh | `docs/test-cases.md` |
| 9 | Làm sao chắc app chạy trên máy người khác? | phải cài trên Windows sạch (TC-PKG-01) — **chưa làm**, đang mở ở #26 | `docs/test-cases.md` |
| 10 | Deploy thế nào, bảo mật ra sao? | khung Dockerfile + compose prod: non-root, không mở cổng DB, `${VAR:?}` bắt buộc; deploy thật là G4 | `infra/`, skill `security` |

## 5. Chưa làm / chưa hiểu

- [ ] Image backend 1,37 GB vì `requirements.txt` dùng chung kéo PySide6 → G4 tách `requirements-api.txt`
- [ ] CI chỉ chạy test trên Ubuntu; Windows chỉ **build**, không chạy test
- [ ] Chưa cài thử `Setup.exe` trên Windows sạch, chưa kiểm gỡ cài đặt sạch (TC-PKG-01/02, #26)
- [ ] Không có test tự động cho Dockerfile/installer — chỉ kiểm tay
- [ ] Chưa ký số (code signing) → SmartScreen cảnh báo "Unknown publisher"
- [ ] Bảo vệ nhánh để `enforce_admins` tắt → còn đường `--admin` merge (lỗ hổng có chủ ý, đã ghi lý do)
- [ ] `api/` chưa có `/health` nên `HEALTHCHECK` trong Dockerfile sẽ unhealthy tới khi #19 xong

## 6. Nhật ký theo cổng

| Cổng | Ngày | Đã xong gì | Còn thiếu gì |
|---|---|---|---|
| G1 | _(chưa ra cổng)_ | CI xanh; bộ cài build + Release `v0.1.0`; `make doctor` kiểm health + cổng; Dockerfile backend; lộ trình cổng | Swagger (A #19), DB 50 món (B #17/#18), 4/4 máy doctor, cài thử trên Windows sạch |
| G2 | | | |
| G3 | | | |
| G4 | | | |
