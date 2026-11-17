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
| 11-11 | #52 | #54 | `.github/workflows/ci.yml`, `release.yml` | thêm `timeout-minutes` + `timeout`/`Acquire::*` cho apt, chặn job treo 10–30 phút | apt treo 3 lần liên tiếp (9–13 phút) phải cancel tay; giới hạn thời gian thì fail nhanh để rerun |
| 11-11 | — | — | `WORKFLOW.md`, `AGENTS.md`, `docs/log/` | thêm **nhật ký cá nhân bắt buộc** cho 4 người, nối vào DoD + PR template + cổng | kiến thức nằm trong chat sẽ mất; file trong repo thì lúc bảo vệ mở ra là có |
| 11-17 | #56 | PR `docs/adr-health-exemption-d` | `WORKFLOW.md` §9.3, `docs/decisions.md` | ghi `/health` là ngoại lệ duy nhất của envelope + ADR-011 | ba consumer của `/health` (Docker healthcheck, `make doctor`, probe bộ cài) không đi qua GUI nên không parse envelope |
| 11-17 | #26 | PR `feat/installer-verify-windows` | `scripts/verify_installer.ps1`, `.github/workflows/release.yml` | job CI cài thử bộ cài trên Windows sạch: cài im lặng → chạy app → chụp ảnh cửa sổ → gỡ cài, ghi báo cáo 13 bước | cả nhóm dùng macOS, chỉ runner `windows-latest` (máy ảo mới mỗi lần chạy) mới là "Windows sạch" kiểm chứng được |
| 11-17 | — | PR `docs/skill-table-readme-d` | `README.md` | đưa bảng 10 skill (đọc khi nào · của ai) vào README chính | bảng skill nằm trong `.claude/skills/README.md` nhưng thành viên không mở file đó |
| 11-17 | — | PR `docs/screenshot-policy-optional-d` | `WORKFLOW.md`, `AGENTS.md`, `.github/pull_request_template.md`, 3 skill, `docs/defense-D.md` | ảnh chụp thành **có điều kiện**: chỉ bắt buộc khi xong/đổi một màn hình; PR backend/DB/CI dùng log + link CI | chụp ảnh mọi PR làm chậm việc backend/DB mà không thêm thông tin; ảnh vẫn giữ cho báo cáo và lúc bảo vệ |
| 11-17 | — | PR `docs/readme-gate-board-d` | `README.md`, `WORKFLOW.md` 12.6, `docs/plan.md`, PR template, `AGENTS.md` | đưa bảng 6 cổng (ai làm gì · ✅/🟡/⬜) vào README + quy tắc cập nhật mỗi lần trạng thái đổi | bảng nằm trong chat thì mỗi người phải hỏi lại; trong README thì mở ra là biết, và có luật bắt cập nhật |
| 11-17 | #17 #18 #28 #31 | #55 (**D làm thay B**) | `db/schema.sql`, `db/seed.sql`, `db/verify_seed.sql`, `docs/erd.md`, `db/README.md` | làm nốt phần DB của B: sửa 3 mã trùng trong seed (118→120 đơn), thêm `deleted_at` + cột ảo UNIQUE, `open_table_id` UNIQUE, 9 `CHECK`, index ghép, `details` → JSON, script kiểm 21 phép | quy ước ghi trong `erd.md` thì không chặn được dữ liệu sai; đưa xuống ràng buộc DB mới kiểm chứng được — B vắng nên D làm thay và ghi rõ trong PR + log để B vẫn bảo vệ được |
| 11-17 | #49 | #44 (merge) | `README.md` | merge màn Order của C (`--squash --admin` vì nhánh `BEHIND`) rồi tick #55/#44 thành ✅, sửa "Đang chặn ngay" chỉ còn #56 | bảng 6 cổng phải khớp sự thật trong cùng ngày (12.6), không để người sau đọc phải trạng thái cũ |
| 11-17 | #19 #20 | #56 (merge) | `README.md` | duyệt #56 kèm kiểm chứng chạy thật (MySQL 8.0: `/health` 200, `/docs` 200, tắt DB 503, bật lại 200), merge, đóng #19/#20, tick bảng cổng | review chỉ đọc diff thì không biết `/health` có sống thật không — chạy uvicorn với DB thật mới chứng minh được tiêu chí "Swagger mở" của G1 |
| 11-18 | #33 | PR `docs/doctor-3-may-adr012` | `docs/decisions.md`, `README.md`, `docs/plan.md`, `WORKFLOW.md` §16.3, `docs/workflow.md`, `docs/defense-D.md` | ADR-012: điều kiện ra G1 đổi từ 4/4 máy `make doctor` thành **3/3 (A, C, D)**, máy B không tính | phần DB của B kiểm bằng `db/verify_seed.sql` trên máy nào cũng được, còn B vắng từ 11-11 — giữ 4/4 là để một cổng kỹ thuật kẹt theo lịch của một người |
| 11-18 | #21 | #65 (merge) | `README.md` | duyệt #65 kèm đối chiếu 9 bảng ORM vs `information_schema` trên MySQL thật (khớp 100% cột), đếm qua ORM đúng seed, thử `CHECK` qua ORM, merge, đóng #21 | test của A chỉ compile DDL, không chạm DB — chỉ chạy trên schema thật mới biết model có lệch cột hay không (tên cột như `order_code`, `invoice_code`, `table_number` khác tên hay đoán, review bằng mắt dễ sai) |
| 11-18 | #22 (phần DB) | PR `docs/refresh-token-schema-d` | `db/schema.sql`, `db/verify_seed.sql`, `docs/erd.md`, `docs/decisions.md`, `CHANGELOG.md`, `db/README.md`, `report/03-phan-tich.md` | chốt với A: thêm bảng `refresh_tokens` (ADR-013), **D làm thay B**; kiểm trên MySQL thật (chèn token, CHECK chặn `expires_at` quá khứ, UNIQUE chặn trùng hash, CASCADE khi xoá user), `verify_seed` 23/23 PASS | A hỏi đúng chỗ: hợp đồng có `/auth/logout` "thu hồi token" nhưng ERD không có chỗ lưu trạng thái — chọn thêm 1 bảng để logout có hiệu lực thật, thay vì nới luật security cho nhanh |
| 11-18 | #22 | #71 (merge) | `README.md` | review #71: bắt lỗi `User-Agent` > 255 ký tự làm login **500** (MySQL 1406), yêu cầu A cắt 255 + test; kiểm lại trên MySQL thật (54 test pass, UA 300/400 ký tự → 200, hash 64 ký tự, logout → refresh 401), duyệt + merge, đóng #22 và 8 issue đã xong | review bằng cách chạy thật mới thấy lỗi 500 chỉ xảy ra khi header dài — đọc diff thì thấy code đúng; sau khi sửa phải kiểm lại cả luồng chứ không chỉ test mới |
| 11-18 | #29 | #73 (merge) | `README.md` | duyệt #73 bằng cách chạy 7 endpoint thật trên MySQL (phân trang, `autoescape` khi search `%`, 409 trùng tên kể cả khác hoa/thường, 403 staff, 204 xoá mềm, tạo lại tên cũ 201); merge, đóng #29, tick bảng cổng G2 | test của A chạy trên DB tạo từ metadata, còn DB thật dùng `db/schema.sql` — chỉ gọi API trên schema thật mới chắc `active_name`/`deleted_at` hoạt động đúng |

> Chi tiết từng quyết định: `docs/decisions.md` (ADR-003…005, 009, 010) · kết quả kiểm chứng:
> CI xanh, Release `v0.1.0` có `CafeTLU-Setup-v0.1.0.exe` (39,4 MB), `pytest` 15 passed.

## 3. AI đã làm gì

> Ghi thật. Đây là phần giảng viên hay hỏi nhất: "AI viết bao nhiêu, em hiểu gì?"

| Ngày | Công cụ | AI làm gì | Tôi sửa / kiểm chứng gì |
|---|---|---|---|
| 11-04 → 11-06 | AI agent trong repo (Claude/DSH) | soạn nháp `WORKFLOW.md`, `AGENTS.md`, 8 skill, README, `docs/defense.md` | đọc lại từng mục, bỏ phần không khớp đề bài; chốt phân vai A/B/C/D |
| 11-09 | AI agent | soạn nháp `infra/Dockerfile`, `.dockerignore`, `docker-compose.prod.yml`, `cafetlu.spec`, `cafetlu.iss`, `build_installer.sh`, `release.yml` | **sửa 3 lỗi thật:** (1) spec trỏ `SPECPATH.parent.parent` ra `~/Desktop` → `FileNotFoundError`; (2) Git Bash đổi `/DMyAppVersion` thành đường dẫn Windows → ISCC báo "more than one script filename", sửa bằng `MSYS_NO_PATHCONV=1`; (3) `doctor` chỉ kiểm container chạy → đổi sang health + socket. Kiểm chứng: build local ra `dist/CafeTLU/`, CI release xanh, chạy `make doctor` từng dòng |
| 11-09 | AI agent | soạn nháp `docs/plan.md` theo cổng, `docs/workflow.md` | tự viết lại phần điều kiện ra cổng cho đo được; bỏ toàn bộ mốc tuần |
| 11-11 | AI agent | đề xuất `timeout-minutes` + apt `Acquire::*`, viết bản sửa workflow | tự chọn ngưỡng (lint 10', test 15', release 45') dựa trên thời gian chạy thật 15–60s và 6–10 phút; tự kiểm YAML bằng `yaml.safe_load` |
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
| G1 | _(chưa ra cổng)_ | CI xanh; bộ cài build + Release `v0.1.0`; `make doctor` kiểm health + cổng; Dockerfile backend; lộ trình cổng; **Swagger + `/health` (A #56) và 50 món (B #55) đã vào `develop`** | 3/3 máy A/C/D `make doctor` (D xong, còn A + C — ADR-012), cài thử trên Windows sạch |
| G2 | | | |
| G3 | | | |
| G4 | | | |
