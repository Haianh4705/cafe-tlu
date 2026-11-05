# CafeTLU — Quản lý quán café TLU

![CI](https://github.com/Haianh4705/cafe-tlu/actions/workflows/ci.yml/badge.svg)

Ứng dụng desktop quản lý quán café — **BTL học phần Python 2026, Đề tài 5**.

```
PySide6 (gui/)  ──HTTP/JSON──►  FastAPI (api/)  ──SQLAlchemy──►  MySQL 8.0
                                   └── /docs (Swagger tự sinh)
```

> **Trạng thái:** hạ tầng đã chạy (`make install` → `make up` → `make doctor` xanh, CI xanh,
> branch protection bật). **Chưa có code ứng dụng** — `api/`, `gui/`, `db/` sẽ có ở tuần 1 (cổng G2).

---

## Bắt đầu trong 5 phút

```bash
git clone https://github.com/Haianh4705/cafe-tlu.git && cd cafe-tlu
make install     # .venv Python 3.12 + thư viện + pre-commit hook + .env
make up          # MySQL 8.0 trong Docker (cổng 3307)
make doctor      # phải xanh 8/8 mục
```

Cần có: **Python 3.12**, **Docker Desktop**, **Git ≥ 2.40**, **make** (Windows: dùng Git Bash/WSL).
Không cần cài MySQL, không cần Inno Setup (bộ cài `.exe` được build trên GitHub Actions).

Sau khi có code: `make api` → <http://127.0.0.1:8000/docs> · `make gui`

## Lệnh thường dùng

| Lệnh | Việc |
|---|---|
| `make` | Danh sách toàn bộ lệnh |
| `make doctor` | Kiểm tra môi trường máy |
| `make install` | Cài lần đầu (venv + thư viện + hooks) |
| `make up` / `make down` | Bật / tắt MySQL |
| `make tools` | Adminer xem DB tại <http://localhost:8081> |
| `make reset-db` | **Xoá sạch** dữ liệu MySQL local rồi bật lại |
| `make api` / `make gui` | Chạy backend / giao diện |
| `make check` | lint + test — **bắt buộc trước khi mở PR** |
| `make lint` / `make fmt` | Kiểm tra / tự sửa format |
| `make build-installer` | Build bộ cài Windows (bật ở G4) |

## Cấu trúc

```
api/            Backend FastAPI — A
gui/            Giao diện PySide6 — C
db/             schema.sql, seed.sql, migrations — B
shared/         hằng số, mã lỗi, version dùng chung
tests/          pytest
scripts/        smoke test, build script
infra/          Dockerfile, deploy — D
installer/      Inno Setup .iss — D
docs/           erd, api-contract, decisions, test-cases, screenshots
report/         báo cáo BTL (mỗi người 1 chương)
.claude/skills/ 9 skill hướng dẫn theo loại việc
```

## Làm việc nhóm

1. Mọi việc bắt đầu từ **Issue** → nhánh `feature/*` từ `develop`.
2. `make check` phải xanh → commit Conventional Commits → mở **PR**.
3. Cần **1 approval** + **CI xanh** → merge **Squash**.

| Tài liệu | Nội dung |
|---|---|
| [`WORKFLOW.md`](WORKFLOW.md) | Quy chuẩn làm việc đầy đủ — **nguồn chân lý** |
| [`docs/workflow.md`](docs/workflow.md) | **Ai làm gì, xong thì bàn giao cho ai** |
| [`docs/defense.md`](docs/defense.md) | **Ngân hàng câu hỏi bảo vệ + cách hiểu bài mình viết** |
| [`AGENTS.md`](AGENTS.md) | Quy tắc cho AI agent |
| [`.claude/skills/`](.claude/skills/README.md) | Hướng dẫn theo từng loại việc |

## Thành viên

| | Vai trò | Vùng phụ trách | GitHub |
|---|---|---|---|
| **A** | Backend/API | `api/` — xác thực, phân quyền, nghiệp vụ | *(chốt tuần 1)* |
| **B** | Data & Reports | `db/`, query thống kê, Excel/PDF | *(chốt tuần 1)* |
| **C** | GUI/UX | `gui/`, theme, màn hình | *(chốt tuần 1)* |
| **D** | Infra + QA + Docs | `infra/`, `installer/`, `.github/`, `docs/`, báo cáo | [@Haianh4705](https://github.com/Haianh4705) |

Nhóm: `@Haianh4705` · `@bao20062005dh-creator` · `@MeoCamGuitar` · `@trungdunxg`

## Xử lý sự cố

| Hiện tượng | Cách sửa |
|---|---|
| `make: docker: No such file or directory` | Makefile đã tự dò `~/.docker/bin`. Vẫn lỗi: `export PATH="$HOME/.docker/bin:$PATH"` |
| `docker-credential-desktop not found` | Docker Desktop → Settings → Advanced → ✅ **Install CLI tools to system** |
| `bind: address already in use` | `lsof -i :3307` rồi tắt tiến trình, hoặc đổi `DB_PORT` trong `.env` |
| `make up` treo ở "chờ MySQL" | Mở Docker Desktop, chờ biểu tượng hết nhấp nháy |
| `python -V` ra 3.9 | `make install` (Makefile ưu tiên `python3.12` và `.venv`) |
| `no tests ran` | Bình thường khi chưa có test — Makefile coi exit code 5 là đạt |
| `pre-commit` chặn commit | `make fmt`; nếu đang ở `main`/`develop` thì tạo nhánh `feature/*` |
| MySQL sai mật khẩu | `make reset-db` (xoá dữ liệu local) |
| Pylance báo đỏ toàn file | VS Code → chọn interpreter `.venv/bin/python` |

## Tài liệu khác

[`docs/erd.md`](docs/erd.md) · [`docs/api-contract.md`](docs/api-contract.md) ·
[`docs/decisions.md`](docs/decisions.md) · [`docs/test-cases.md`](docs/test-cases.md) ·
[`docs/setup-github.md`](docs/setup-github.md) · [`CHANGELOG.md`](CHANGELOG.md) ·
[đề bài gốc (PDF)](Danh-sach-BTL-hoc-phan-Python-TLU-2026.pdf)
