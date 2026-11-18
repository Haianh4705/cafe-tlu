# CafeTLU — Quản lý quán café TLU

![CI](https://github.com/Haianh4705/cafe-tlu/actions/workflows/ci.yml/badge.svg)

Ứng dụng desktop quản lý quán café — **BTL học phần Python 2026, Đề tài 5**.

```
PySide6 (gui/)  ──HTTP/JSON──►  FastAPI (api/)  ──SQLAlchemy──►  MySQL 8.0
```

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
make start       # MySQL + API + giao diện (Docker Desktop phải đang mở)
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
| `make start` | Chạy MySQL, API và giao diện; đóng GUI sẽ dừng API |
| `make up` / `make down` | Bật / tắt MySQL |
| `make tools` | Adminer xem DB tại <http://localhost:8081> |
| `make reset-db` | **Xoá sạch** dữ liệu MySQL local rồi bật lại |
| `make api` / `make gui` | Chạy riêng backend / giao diện (dùng khi debug) |
| `make check` | lint + test — **bắt buộc trước khi mở PR** |
| `make lint` / `make fmt` | Kiểm tra / tự sửa format |
| `make build-installer` | Build bộ cài Windows (bật ở cổng G4) |

## Cấu trúc

```
api/            Backend FastAPI (routers, services, models, schemas)
gui/            Giao diện PySide6 (views, widgets, api_client, theme, i18n)
db/             schema.sql, seed, verify_seed, migrations (Alembic)
shared/         mã lỗi, version, paths dùng chung
tests/          pytest (unit, API, DB, smoke)
scripts/        next_task.sh, smoke test, seed data, build script
infra/          Dockerfile, compose production, deploy
installer/      Inno Setup .spec/.iss
docs/           erd, api-contract, plan, workflow, defense, decisions, log/
report/         báo cáo BTL (10 file theo chương)
.claude/skills/ 10 skill hướng dẫn theo tầng kỹ thuật / loại việc
```

Mỗi thư mục có `README.md` riêng: vai trò tầng · đặt gì · **không** đặt gì · skill cần đọc.

## Thành viên & Nhật ký (giao việc theo chức năng — ADR-014)

> Công việc được gán **theo từng chức năng trên GitHub Issue** (người nhận sửa trọn gói `db/` → `api/` → `gui/` → `tests/` của chức năng đó, giữ kiến trúc `gui → api → db`).

| Mã | GitHub | Thế mạnh tham khảo | Nhật ký cá nhân |
|---|---|---|---|
| **A** | [@bao20062005dh-creator](https://github.com/bao20062005dh-creator) | Backend / FastAPI / Auth / Test | [`docs/log/A.md`](docs/log/A.md) |
| **B** | [@trungdunxg](https://github.com/trungdunxg) | MySQL / Schema / Báo cáo Excel & PDF | [`docs/log/B.md`](docs/log/B.md) |
| **C** | [@MeoCamGuitar](https://github.com/MeoCamGuitar) | Giao diện PySide6 / UX / Theme TLU | [`docs/log/C.md`](docs/log/C.md) |
| **D** | [@Haianh4705](https://github.com/Haianh4705) | Infra / CI-CD / Đóng gói / QA / Điều phối | [`docs/log/D.md`](docs/log/D.md) |

## Sáu cổng bàn giao

Xem tiến độ và người phụ trách theo từng chức năng tại [milestone GitHub](https://github.com/Haianh4705/cafe-tlu/milestones). Xem [quy tắc qua cổng và nhật ký](WORKFLOW.md#163-cổng-kiểm-tra-theo-mốc-không-qua-cổng-thì-không-đi-tiếp) và [lộ trình Issue chức năng](docs/plan.md).

| Cổng | Minh chứng chính |
|---|---|
| [G1 — Nền móng ✅](https://github.com/Haianh4705/cafe-tlu/issues?q=milestone%3AG1) | Máy A và D chạy được theo README, CI xanh, Swagger mở, có 50 món mẫu và bộ cài chạy trên Windows sạch (ADR-015) |
| [G2 — Lát cắt dọc](https://github.com/Haianh4705/cafe-tlu/issues?q=milestone%3AG2) | Demo login, phân quyền và CRUD món trên máy người khác. Có kiểm thử cho ít nhất 12 endpoint |
| [G3 — MVP](https://github.com/Haianh4705/cafe-tlu/issues?q=milestone%3AG3) | Đủ sáu yêu cầu đề bài, demo toàn luồng và cài được bộ cài từ CI trên Windows sạch |
| [G4 — Deploy](https://github.com/Haianh4705/cafe-tlu/issues?q=milestone%3AG4) | Backend có URL công khai và tag kích hoạt build bộ cài qua CI |
| [G5 — QA](https://github.com/Haianh4705/cafe-tlu/issues?q=milestone%3AG5) | Test case đạt ít nhất 95%, báo cáo đạt 80% và có video demo |
| [G6 — Đóng băng](https://github.com/Haianh4705/cafe-tlu/issues?q=milestone%3AG6) | Đóng băng trước hạn ba ngày, chỉ nhận hotfix và đã tập bảo vệ |

## Làm việc nhóm

1. **100% chức năng qua Issue & PR** (không push thẳng lên `main`/`develop`; repo bật `enforce_admins: true`).
2. `make check` phải xanh → commit Conventional Commits → mở **PR** từ nhánh `feature/*`/`fix/*` với `Refs #<issue>`.
3. **Bỏ bắt buộc approve:** chờ **CI xanh** (`Lint & format`, `Test`) + hoàn thành checklist (3 câu bảo vệ + nhật ký cá nhân) → tác giả tự **Squash & merge** vào `develop`, nghiệm thu rồi đóng Issue ([WORKFLOW mục 3.2](WORKFLOW.md#32-quy-tắc-kiểm-tra-và-merge-pr)).

| Tài liệu | Nội dung |
|---|---|
| [`WORKFLOW.md`](WORKFLOW.md) | Quy chuẩn làm việc đầy đủ — **nguồn chân lý** |
| [`docs/plan.md`](docs/plan.md) | **Phạm vi từng cổng, phụ thuộc và danh sách Issue chức năng** |
| [`docs/workflow.md`](docs/workflow.md) | Quy trình làm một chức năng từ Issue đến đóng trên `develop` |
| [`docs/defense.md`](docs/defense.md) | Ngân hàng câu hỏi bảo vệ + cách hiểu bài mình viết |
| [`docs/log/`](docs/log/README.md) | **Nhật ký cá nhân A/B/C/D** — mỗi người ghi Issue chức năng mình làm + AI đã hỗ trợ gì |
| [`AGENTS.md`](AGENTS.md) | Quy tắc cho AI agent |
| [`.claude/skills/`](.claude/skills/README.md) | 10 skill: API, DB, GUI, UI, test, đóng gói, báo cáo, bảo mật, tối giản, hỏi việc |

## Skill — đọc theo tầng chạm tới (10 skill)

Skill là file hướng dẫn chi tiết cho **một loại việc**: bất biến cần giữ, khuôn mẫu copy được,
checklist trước khi mở PR. **Đọc trước khi viết code**, không phải sau. Đường dẫn:
`.claude/skills/<tên>/SKILL.md`. Khi mâu thuẫn với `WORKFLOW.md` → `WORKFLOW.md` thắng.

| Skill | Đọc khi | Tầng áp dụng |
|---|---|---|
| [`next-task`](.claude/skills/next-task/SKILL.md) | **"Tôi cần làm gì?"** — tra Issue được gán, trả lời theo thứ tự | Cả nhóm |
| [`minimal-change`](.claude/skills/minimal-change/SKILL.md) | **Mọi việc code** — chọn cách nhỏ nhất đủ dùng | Cả nhóm |
| [`fastapi-endpoint`](.claude/skills/fastapi-endpoint/SKILL.md) | Thêm/sửa endpoint, test route | Khi chạm `api/` |
| [`sqlalchemy-model`](.claude/skills/sqlalchemy-model/SKILL.md) | Thêm bảng/cột, migration, seed | Khi chạm `db/` |
| [`pyside6-screen`](.claude/skills/pyside6-screen/SKILL.md) | Làm màn hình, form, trạng thái UI | Khi chạm `gui/` |
| [`ui-design`](.claude/skills/ui-design/SKILL.md) | Màu, font, khoảng cách, chống "AI slop" | Khi chạm `gui/` |
| [`pytest-db`](.claude/skills/pytest-db/SKILL.md) | Fixture DB, test API, test hồi quy | Khi viết test |
| [`report-export`](.claude/skills/report-export/SKILL.md) | Xuất Excel/PDF, in hoá đơn | Khi làm báo cáo / bill |
| [`win-installer`](.claude/skills/win-installer/SKILL.md) | Build `.exe`, lỗi đóng gói | Khi chạm `installer/` / CI |
| [`security`](.claude/skills/security/SKILL.md) | Auth, phân quyền, secret, review trước deploy | Mọi chức năng liên quan auth / deploy |

**Cách dùng nhanh:** mở phiên AI agent ở gốc repo và nói

> Đọc `AGENTS.md` và skill `next-task`, cho tôi biết việc tiếp theo của tôi.

Muốn tra tay thì chạy `make next` (lấy Issue đang gán cho bạn, kèm skill phải đọc).
Quy ước viết skill mới: xem [`.claude/skills/README.md`](.claude/skills/README.md).

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
