# CafeTLU — Quản lý quán café TLU

![CI](https://github.com/Haianh4705/cafe-tlu/actions/workflows/ci.yml/badge.svg)

Ứng dụng desktop quản lý quán café — **BTL học phần Python 2026, Đề tài 5**.

```
PySide6 (gui/)  ──HTTP/JSON──►  FastAPI (api/)  ──SQLAlchemy──►  MySQL 8.0
```

> **Trạng thái:** hạ tầng xong, GUI đã có khung + màn Đăng nhập/Thực đơn; `api/` và `db/` còn trống
> — đang ở **cổng G1**. Lộ trình: [`docs/plan.md`](docs/plan.md).

## Hôm nay tôi làm gì?

```bash
make next        # in ra việc tiếp theo + danh sách còn lại, theo đúng thứ tự
```

Lệnh này đọc Issue được gán cho tài khoản `gh` đang đăng nhập và sắp theo phụ thuộc.
Xem việc của người khác (D dùng để điều phối): `make next u=trungdunxg`.

**Dùng AI agent?** Mở agent trong thư mục repo và hỏi:

```
Đọc AGENTS.md và skill next-task, cho tôi biết việc tiếp theo của tôi.
```

Agent sẽ chạy `make next`, đọc Issue, và trả lời: làm gì · xong khi nào · skill nào phải đọc ·
đang chờ ai. Không cần nhớ gì cả.

## Bắt đầu trong 5 phút

```bash
git clone https://github.com/Haianh4705/cafe-tlu.git && cd cafe-tlu
make install     # .venv Python 3.12 + thư viện + pre-commit hook + .env
make up          # MySQL 8.0 trong Docker (cổng 3307)
make doctor      # phải xanh 8/8 mục
```

Cần: **Python 3.12** · **Docker Desktop** · **Git ≥ 2.40** · **make** (Windows: Git Bash/WSL).
Không cần cài MySQL, không cần Inno Setup (bộ cài `.exe` build trên GitHub Actions).

## Lệnh thường dùng

| Lệnh | Việc |
|---|---|
| `make next` | **Việc tiếp theo của bạn** |
| `make` | Danh sách toàn bộ lệnh |
| `make install` | Cài lần đầu (venv + thư viện + hooks + `.env`) |
| `make doctor` | Kiểm tra môi trường máy |
| `make up` / `make down` | Bật / tắt MySQL |
| `make tools` | Adminer xem DB tại <http://localhost:8081> |
| `make reset-db` | **Xoá sạch** dữ liệu MySQL local rồi bật lại |
| `make api` / `make gui` | Chạy backend / giao diện |
| `make check` | lint + test — **bắt buộc trước khi mở PR** |
| `make lint` / `make fmt` | Kiểm tra / tự sửa format |
| `make build-installer` | Build bộ cài Windows (bật ở cổng G4) |

## Cấu trúc

```
api/            Backend FastAPI            — A
gui/            Giao diện PySide6          — C
db/             schema.sql, seed, migrations — B
shared/         mã lỗi, version, paths
tests/          pytest
scripts/        next_task.sh, smoke test, build script
infra/          Dockerfile, deploy         — D
installer/      Inno Setup .spec/.iss      — D
docs/           erd, api-contract, plan, workflow, defense, decisions, log/
report/         báo cáo BTL (mỗi người 1 chương)
.claude/skills/ 10 skill hướng dẫn theo loại việc
```

Mỗi thư mục có `README.md` riêng: owner · đặt gì · **không** đặt gì.

## Vai trò

| | Vai trò | Vùng | GitHub |
|---|---|---|---|
| **A** | Backend/API | `api/`, `shared/` | [@bao20062005dh-creator](https://github.com/bao20062005dh-creator) |
| **B** | Data & Reports | `db/`, reports | [@trungdunxg](https://github.com/trungdunxg) |
| **C** | GUI/UX | `gui/`, `assets/` | [@MeoCamGuitar](https://github.com/MeoCamGuitar) |
| **D** | Infra + QA + Docs | `infra/`, `installer/`, `docs/`, `report/` | [@Haianh4705](https://github.com/Haianh4705) |

## Làm việc nhóm

1. Mọi việc bắt đầu từ **Issue** → nhánh `feature/*` từ `develop`.
2. `make check` phải xanh → commit Conventional Commits → mở **PR**.
3. Cần **1 approval** + **CI xanh** → merge **Squash**.

| Tài liệu | Nội dung |
|---|---|
| [`WORKFLOW.md`](WORKFLOW.md) | Quy chuẩn làm việc đầy đủ — **nguồn chân lý** |
| [`docs/plan.md`](docs/plan.md) | **Lộ trình theo cổng: đang ở đâu, việc gì mở khoá cổng, giao theo thứ tự nào** |
| [`docs/workflow.md`](docs/workflow.md) | Ai làm gì, xong thì bàn giao cho ai |
| [`docs/defense.md`](docs/defense.md) | Ngân hàng câu hỏi bảo vệ + cách hiểu bài mình viết |
| [`docs/log/`](docs/log/README.md) | **Nhật ký cá nhân A/B/C/D** — mỗi người ghi việc đã làm + AI đã hỗ trợ gì |
| [`AGENTS.md`](AGENTS.md) | Quy tắc cho AI agent |
| [`.claude/skills/`](.claude/skills/README.md) | 10 skill: API, DB, GUI, UI, test, đóng gói, báo cáo, bảo mật, tối giản, hỏi việc |

## Xử lý sự cố

| Hiện tượng | Cách sửa |
|---|---|
| `make: docker: No such file or directory` | Makefile tự dò `~/.docker/bin`. Vẫn lỗi: `export PATH="$HOME/.docker/bin:$PATH"` |
| `docker-credential-desktop not found` | Docker Desktop → Settings → Advanced → ✅ **Install CLI tools to system** |
| `bind: address already in use` | `lsof -i :3307` rồi tắt tiến trình, hoặc đổi `DB_PORT` trong `.env` |
| `make up` treo ở "chờ MySQL" | Mở Docker Desktop, chờ biểu tượng hết nhấp nháy |
| `python -V` ra 3.9 | `make install` (Makefile ưu tiên `python3.12`) |
| `make next` báo chưa đăng nhập | `gh auth login` (cài: `brew install gh`) |
| `no tests ran` | Bình thường khi chưa có test — Makefile coi exit code 5 là đạt |
| `pre-commit` chặn commit | `make fmt`; nếu đang ở `main`/`develop` thì tạo nhánh `feature/*` |
| MySQL sai mật khẩu | `make reset-db` (xoá dữ liệu local) |
| Pylance báo đỏ toàn file | VS Code → chọn interpreter `.venv/bin/python` |

## Tài liệu khác

[`docs/erd.md`](docs/erd.md) (B tự thiết kế) · [`docs/api-contract.md`](docs/api-contract.md) ·
[`docs/decisions.md`](docs/decisions.md) · [`docs/test-cases.md`](docs/test-cases.md) ·
[`docs/setup-github.md`](docs/setup-github.md) · [`CHANGELOG.md`](CHANGELOG.md) ·
[đề bài gốc (PDF)](Danh-sach-BTL-hoc-phan-Python-TLU-2026.pdf)
