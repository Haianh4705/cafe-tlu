# CafeTLU — Quản lý quán café TLU

Ứng dụng desktop quản lý quán café cho **BTL học phần Python 2026 — Đề tài 5**.

> **Trạng thái hiện tại: GIAI ĐOẠN 0 — HẠ TẦNG ĐÃ CHẠY.**
> Đã kiểm chứng trên máy thật: `make install` → `make up` (MySQL 8.0 healthy ở cổng 3307)
> → `make doctor` xanh → CI xanh trên `main`/`develop`. Repo **public**, branch protection
> đã bật (1 approval + CI bắt buộc). **Chưa có code ứng dụng** — `api/`, `gui/` sẽ được tạo
> ở tuần 1, cổng G2.

## Kiến trúc

```
PySide6 (gui/)  ──HTTP/JSON──►  FastAPI (api/)  ──SQLAlchemy──►  MySQL 8.0
                                   │
                                   └── /docs (Swagger tự sinh)
```

Chi tiết: `WORKFLOW.md` mục 4.

## Yêu cầu môi trường

| Công cụ | Phiên bản | Ghi chú |
|---|---|---|
| **Python** | 3.12.x | `python3.12 -V`. Bản 3.13 có thể thiếu wheel — tránh |
| **Docker Desktop** | mới nhất | **Bắt buộc**, dùng để chạy MySQL. macOS: bản Apple Silicon |
| **Git** | ≥ 2.40 | |
| **make** | bất kỳ | Windows: dùng Git Bash / WSL |
| **VS Code** | mới nhất | + extension Python, Pylance, Ruff, Docker, GitLens |

Không cần cài MySQL, không cần cài Inno Setup (bộ cài Windows được build trên GitHub Actions).

## Chạy lần đầu (4 lệnh)

```bash
git clone <repo-url> && cd cafe-tlu
make install      # tạo .venv, cài thư viện, cài pre-commit hook, tạo .env
make up           # bật MySQL 8.0 trong Docker (cổng 3307)
make doctor       # kiểm tra môi trường — phải thấy Python OK + MySQL sẵn sàng
```

Sau khi có code (tuần 1): `make api` (backend, http://127.0.0.1:8000/docs) và `make gui`.

## Lệnh thường dùng

| Lệnh | Việc |
|---|---|
| `make` | Xem toàn bộ lệnh |
| `make doctor` | Kiểm tra môi trường máy |
| `make install` | Cài đặt lần đầu (venv + thư viện + hooks) |
| `make up` / `make down` | Bật / tắt MySQL |
| `make tools` | Bật Adminer xem DB tại http://localhost:8081 |
| `make reset-db` | **Xoá sạch** dữ liệu MySQL local rồi bật lại |
| `make api` | Chạy backend FastAPI |
| `make gui` | Chạy giao diện desktop |
| `make test` | Chạy test |
| `make lint` / `make fmt` | Kiểm tra / tự sửa format |
| `make check` | lint + test (bắt buộc trước khi mở PR) |
| `make build-installer` | Build bộ cài Windows (cần `installer/*.iss`) |

## Cấu trúc thư mục

```
├── api/                    # Backend FastAPI (A) — tuần 1
├── gui/                    # Giao diện PySide6 (C) — tuần 1
├── db/                     # schema.sql, seed.sql, migrations (B) — tuần 1
├── shared/                 # hằng số, mã lỗi, version dùng chung
├── tests/                  # pytest
├── scripts/                # smoke_test.py, build_installer.sh
├── infra/                  # Dockerfile backend, deploy.md (G4)
├── installer/              # Inno Setup .iss (G4)
├── assets/                 # icon, ảnh món
├── docs/                   # decisions, api-contract, erd, test-cases, screenshots
├── report/                 # báo cáo BTL (mỗi người 1 chương)
├── .github/                # CI, release, CODEOWNERS, template Issue/PR
├── docker-compose.yml      # MySQL 8.0 (+ Adminer profile tools)
├── Makefile
├── WORKFLOW.md             # ⭐ quy chuẩn làm việc — đọc trước khi làm
└── AGENTS.md               # ⭐ điểm vào cho AI agent
```

## Quy trình làm việc (tóm tắt 5 dòng)

1. Đọc `WORKFLOW.md`. Mọi việc bắt đầu từ **Issue**.
2. Tạo nhánh từ `develop`: `git switch -c feature/<scope>-<slug>-<tên>`.
3. `make check` phải xanh. Commit theo Conventional Commits.
4. Mở **PR** vào `develop`, cần **1 approval** + **CI xanh**.
5. Merge bằng **Squash** → nhánh tự xoá.

Chi tiết đầy đủ: `WORKFLOW.md` mục 5–6.

## Thành viên & vai trò

| | Vai trò | Vùng phụ trách | GitHub |
|---|---|---|---|
| **A** | Backend/API Lead | `api/` — xác thực, phân quyền, nghiệp vụ | *(chốt ở buổi sync tuần 1)* |
| **B** | Data & Reports | `db/`, query thống kê, xuất Excel/PDF | *(chốt ở buổi sync tuần 1)* |
| **C** | GUI/UX Lead | `gui/`, theme, toàn bộ màn hình | *(chốt ở buổi sync tuần 1)* |
| **D** | Infra + QA + Docs | `infra/`, `installer/`, `.github/`, `docs/`, báo cáo | [@Haianh4705](https://github.com/Haianh4705) |

Tài khoản GitHub của nhóm: `@Haianh4705` · `@bao20062005dh-creator` · `@MeoCamGuitar` · `@trungdunxg`.

Khi đã chốt vai, cập nhật `.github/CODEOWNERS` (mục 2) bằng một PR 1 dòng — sau đó bật
**Require review from Code Owners** để GitHub tự gán đúng người review.

Phân quyền chi tiết: `WORKFLOW.md` mục 3. Quyết định kỹ thuật: `docs/decisions.md`.

## Lộ trình & cổng kiểm tra

| Cổng | Tuần | Điều kiện xanh |
|---|---|---|
| **G1** Nền móng | 1 | Cả 4 máy chạy được bằng README; CI xanh; build installer thử lần 1 |
| **G2** Lát cắt dọc | 2 | Login + phân quyền + CRUD món chạy end-to-end |
| **G3** MVP | 4 | Đủ 6 yêu cầu đề bài; installer cài được trên máy sạch |
| **G4** Deploy | 6 | Backend có URL công khai; tag → CI tự build installer |
| **G5** QA | 7 | Test case pass ≥ 95%; báo cáo 80%; video demo |
| **G6** Đóng băng | 8 | Trước hạn 3 ngày, không merge gì trừ hotfix |

## Xử lý sự cố

| Hiện tượng | Nguyên nhân thường gặp | Cách sửa |
|---|---|---|
| `make: docker: No such file or directory` | Docker CLI chưa nằm trong PATH của shell (Docker Desktop đặt ở `~/.docker/bin`) | Makefile đã tự dò đường dẫn này. Nếu vẫn lỗi: mở terminal mới, hoặc thêm `export PATH="$HOME/.docker/bin:$PATH"` vào `~/.zshrc` |
| `error getting credentials - docker-credential-desktop not found` | Thiếu credential helper trong PATH | Docker Desktop → Settings → Advanced → ✅ **Install CLI tools to system**; hoặc để Makefile tự nạp `~/.docker/bin` |
| `bind: address already in use` | Cổng 3307 bị chiếm | `lsof -i :3307` rồi tắt tiến trình, hoặc đổi `DB_PORT` trong `.env` |
| `make up` treo ở "chờ MySQL" | Docker Desktop chưa chạy | Mở Docker Desktop, chờ biểu tượng hết nhấp nháy |
| `python -V` ra 3.9 | macOS dùng python hệ thống | Dùng `python3.12` hoặc `make install` (Makefile ưu tiên `.venv`) |
| `pytest` báo "no tests ran" | Chưa có test (giai đoạn setup) | Bình thường — Makefile coi exit code 5 là đạt |
| `pre-commit` chặn commit | Code chưa format / có secret / đang ở nhánh `main`/`develop` | `make fmt` rồi commit lại, hoặc tạo nhánh `feature/*`. **Không** dùng `--no-verify` |
| MySQL sai mật khẩu | `.env` khác với volume cũ | `make reset-db` (xoá dữ liệu local) |
| Pylance báo đỏ toàn file | Chưa chọn interpreter | VS Code → chọn `.venv/bin/python` |

## Tài liệu

| File | Nội dung |
|---|---|
| `WORKFLOW.md` | Quy chuẩn làm việc cho người và AI (nguồn chân lý) |
| `AGENTS.md` | Quy tắc cho AI agent |
| `.claude/skills/` | **8 skill** hướng dẫn theo loại việc (API, DB, GUI, UI, test, đóng gói, báo cáo, bảo mật) |
| `docs/setup-github.md` | Thiết lập branch protection, nhãn, board |
| `docs/decisions.md` | Nhật ký quyết định kỹ thuật |
| `docs/api-contract.md` | Đặc tả API |
| `docs/erd.md` | Sơ đồ dữ liệu |
| `docs/test-cases.md` | Danh sách ca kiểm thử |
| `CHANGELOG.md` | Lịch sử thay đổi |
