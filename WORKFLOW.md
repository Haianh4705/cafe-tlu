# WORKFLOW — Quy chuẩn làm việc của dự án

> **Dự án:** Ứng dụng Desktop quản lý quán café TLU (BTL học phần Python 2026 — Đề tài 5)
> **Phiên bản:** 2.0 · **Cập nhật:** 2026-11-18 · **Người duy trì:** D (Infra/QA/Docs)
> **Đối tượng áp dụng:** toàn bộ 4 thành viên **và mọi AI agent** làm việc trong repo này.

> ⚠️ **File này là nguồn chân lý duy nhất (single source of truth) về cách làm việc.**
> Khi có mâu thuẫn giữa thói quen cá nhân / hướng dẫn trên mạng / câu trả lời của AI với file này → **file này thắng**.
> Thay đổi quy định phải mở Issue và Pull Request vào `develop`, vượt qua CI xanh và thông báo cho cả nhóm.

---

## Mục lục

0. [TL;DR — đọc trong 5 phút](#0-tldr--đọc-trong-5-phút)
1. [Mục đích & phạm vi](#1-mục-đích--phạm-vi)
2. [Từ khoá quy ước & thứ tự ưu tiên](#2-từ-khoá-quy-ước--thứ-tự-ưu-tiên)
3. [Thành viên, gán theo chức năng và cơ chế Merge](#3-thành-viên-gán-theo-chức-năng-và-cơ-chế-merge)
4. [Kiến trúc bất biến và phạm vi sửa các tầng](#4-kiến-trúc-bất-biến-và-phạm-vi-sửa-các-tầng)
5. [Vòng đời một việc (quy trình chuẩn)](#5-vòng-đời-một-việc-quy-trình-chuẩn)
6. [Definition of Ready / Definition of Done](#6-definition-of-ready--definition-of-done)
7. [Quy chuẩn code Python](#7-quy-chuẩn-code-python)
8. [Quy chuẩn cơ sở dữ liệu (MySQL)](#8-quy-chuẩn-cơ-sở-dữ-liệu-mysql)
9. [Quy chuẩn API](#9-quy-chuẩn-api)
10. [Quy chuẩn GUI](#10-quy-chuẩn-gui)
11. [Quy chuẩn kiểm thử](#11-quy-chuẩn-kiểm-thử)
12. [Quy chuẩn tài liệu & minh chứng](#12-quy-chuẩn-tài-liệu--minh-chứng)
13. [Quy chuẩn đóng gói & phát hành](#13-quy-chuẩn-đóng-gói--phát-hành)
14. [Bảo mật & dữ liệu](#14-bảo-mật--dữ-liệu)
15. [Quy tắc dành riêng cho AI Agent](#15-quy-tắc-dành-riêng-cho-ai-agent)
16. [Nhịp làm việc & giao tiếp](#16-nhịp-làm-việc--giao-tiếp)
17. [Xung đột, trễ hạn, rủi ro](#17-xung-đột-trễ-hạn-rủi-ro)
18. [Phụ lục: template & lệnh thường dùng](#18-phụ-lục-template--lệnh-thường-dùng)
19. [Lịch sử thay đổi](#19-lịch-sử-thay-đổi)

---

## 0. TL;DR — đọc trong 5 phút

Vòng làm việc: **Issue (gán theo chức năng) → Nhánh → Code + Test → PR → CI xanh → Squash merge vào `develop` → Nghiệm thu & Đóng Issue.**

1. **Cấm push trực tiếp** lên `main` và `develop` (repo bật `enforce_admins: true`). **100% chức năng và sửa lỗi đi qua Issue + Pull Request.**
2. **Giao việc theo chức năng cần làm (ADR-014):** một chức năng = một Issue = một nhánh = một PR. Người nhận Issue được sửa trọn gói `db/` + `api/` + `gui/` + `tests/` của chức năng đó, giữ kiến trúc `gui → api → db`.
3. **Bỏ bắt buộc approve:** chỉ cần **CI xanh** (`Lint & format`, `Test`) + đủ checklist (test, 3 câu bảo vệ, nhật ký cá nhân) → tác giả **tự Squash & merge** vào `develop`, nghiệm thu rồi đóng Issue.
4. **Commit theo Conventional Commits**: `feat(order): thêm gộp bàn`.
5. **Không commit** `.env`, `dist/`, `build/`, `.venv/`, file DB, ảnh nặng.
6. **Không hardcode** mật khẩu / connection string / đường dẫn tuyệt đối của máy mình.
7. **Đổi schema DB hoặc API contract → ghi rõ trong Issue/PR**, tạo migration Alembic mới và cập nhật đồng bộ `db/schema.sql`, `docs/erd.md` hoặc `docs/api-contract.md`.
8. **Thêm thư viện mới → phải xin phép** (1 dòng trong Issue là đủ, nhưng phải có).
9. **Code xong là phải có test**; không sửa test cho pass thay vì sửa code.
10. Cập nhật tài liệu liên quan và lưu ảnh khi hoàn thiện hoặc đổi màn hình.
11. **AI agent cũng là thành viên**: đọc file này trước, tuân thủ mục 15, báo cáo theo mẫu 15.4.
12. **Mỗi người giữ `docs/log/<vai>.md`** (A/B/C/D): ghi mọi Issue chức năng mình làm · AI đã làm gì · câu hỏi thầy hay hỏi. Cập nhật **trong PR**, không để cuối kỳ (mục 12.5).
13. Khi không chắc → **dừng lại và hỏi trong Issue**, đừng đoán.

---

## 1. Mục đích & phạm vi

### 1.1 Mục đích

- Bảo đảm **4 người + AI** làm song song mà không giẫm chân nhau, không "integration hell" ở tuần cuối.
- Bảo đảm sản phẩm đạt **mốc 8–9** theo rubric môn học: đủ chức năng, giao diện tối ưu, có đóng gói/CI-CD/deploy, tài liệu đầy đủ.
- Tạo bằng chứng minh bạch về **đóng góp từng cá nhân** (lịch sử Git + PR + báo cáo).
- Cho phép AI agent tham gia an toàn: có phạm vi rõ, có kiểm chứng, có báo cáo.

### 1.2 Trong phạm vi

Toàn bộ mã nguồn, CSDL, tài liệu, kịch bản build/deploy, cấu hình CI của dự án.

### 1.3 Ngoài phạm vi

Quy định của trường/GV (ưu tiên cao hơn nếu khác), quy định về nộp bài, thang điểm (xem PDF đề bài).

### 1.4 Bản đồ file để AI/người mới đọc nhanh

| File | Vai trò | Ai đọc |
|---|---|---|
| `WORKFLOW.md` | Quy chuẩn làm việc (file này) | Tất cả, **bắt buộc** |
| `AGENTS.md` | Điểm vào cho AI agent, trỏ về file này | AI agent |
| `README.md` | Cách cài & chạy trong 3 lệnh | Tất cả, GV |
| `CONTRIBUTING.md` | Bản rút gọn của mục 5–6 cho người mới | Thành viên mới |
| `docs/decisions.md` | Nhật ký quyết định kỹ thuật (ADR-lite) | Tất cả |
| `docs/plan.md` | **Lộ trình theo cổng + Issue chức năng theo cổng** | D, cả nhóm |
| `docs/workflow.md` | **Luồng chức năng từ Issue đến đóng trên `develop`** | Tất cả |
| `docs/api-contract.md` | Đặc tả API (nguồn chân lý của hợp đồng) | Cả nhóm |
| `docs/erd.md` | Thiết kế dữ liệu (ERD, từ điển, bất biến) | Cả nhóm |
| `docs/defense.md` | Ngân hàng câu hỏi bảo vệ + cách hiểu bài mình viết | Tất cả |
| `docs/test-cases.md` | Danh sách ca kiểm thử (PASS/FAIL) | Cả nhóm |
| `docs/setup-github.md` | Thiết lập GitHub (branch protection, nhãn, milestone) | D |
| `docs/standup.md` | Mẫu báo blocker | Tất cả |
| `.claude/skills/` | 10 skill hướng dẫn theo tầng kỹ thuật / loại việc | Tất cả + AI |
| `<thư mục>/README.md` | Mỗi thư mục có README: vai trò tầng, đặt gì, **không** đặt gì | Người chạm thư mục |
| `CHANGELOG.md` | Lịch sử thay đổi theo phiên bản | Cả nhóm (D biên tập) |
| `db/schema.sql`, `db/seed.sql` | Cấu trúc DB + dữ liệu mẫu | Cả nhóm khi setup |

---

## 2. Từ khoá quy ước & thứ tự ưu tiên

Dùng đúng các từ sau (theo RFC 2119, Việt hoá):

| Từ | Nghĩa | Vi phạm thì |
|---|---|---|
| **BẮT BUỘC / PHẢI** | Không làm là sai quy trình | PR bị từ chối |
| **KHÔNG ĐƯỢC / CẤM** | Tuyệt đối không | Revert + báo nhóm |
| **NÊN** | Làm trừ khi có lý do chính đáng, ghi lý do vào PR | Không sao, nhưng phải giải thích |
| **CÓ THỂ** | Tuỳ chọn | – |

**Thứ tự ưu tiên khi mâu thuẫn (cao → thấp):**

1. Yêu cầu của GV / đề bài
2. `WORKFLOW.md` (file này)
3. `docs/api-contract.md` và `docs/decisions.md` (đã chốt)
4. Quy ước công cụ (ruff/black/commitlint)
5. Sở thích cá nhân

> Quy tắc: **"Im lặng = đồng ý" không tồn tại.** Mọi thay đổi ảnh hưởng người khác phải được ghi lại bằng văn bản (Issue/PR/ADR).

---

## 3. Thành viên, gán theo chức năng và cơ chế Merge

### 3.1 Thành viên và nguyên tắc gán việc theo chức năng (ADR-014)

Nhóm bỏ khoá cứng thư mục theo vai (`api/` chỉ A sửa, `gui/` chỉ C sửa...). Thay vào đó, công việc được **chia theo từng chức năng cần làm trên GitHub Issue** (trọn gói end-to-end hoặc tách Issue con theo lát cắt), mỗi Issue có đúng **1 assignee**:

| Mã | Tài khoản GitHub | Thế mạnh tham khảo | File nhật ký cá nhân |
|---|---|---|---|
| **A** | `@bao20062005dh-creator` | Backend / FastAPI / Auth / Test API | [`docs/log/A.md`](docs/log/A.md) |
| **B** | `@trungdunxg` | MySQL / Schema / Báo cáo Excel & PDF | [`docs/log/B.md`](docs/log/B.md) |
| **C** | `@MeoCamGuitar` | Giao diện PySide6 / UX / Theme TLU | [`docs/log/C.md`](docs/log/C.md) |
| **D** | `@Haianh4705` | Infra / CI-CD / Đóng gói / QA / Điều phối | [`docs/log/D.md`](docs/log/D.md) |

- **Mọi chức năng đều qua Issue & PR:** thành viên được D gán Issue (hoặc tự nhận Issue chưa có assignee sau khi báo trong Issue/nhóm). D giữ điều phối tiến độ, cân bằng tải và cập nhật trạng thái cổng trên GitHub.
- **Sửa trọn gói các tầng:** khi nhận Issue chức năng, thành viên được sửa `db/` + `api/` + `gui/` + `shared/` + `tests/` + `docs/` thuộc phạm vi chức năng đó để chạy end-to-end, nhưng **PHẢI** giữ nguyên kiến trúc tại [mục 4.1](#41-kiến-trúc-mục-tiêu).
- **Nhật ký theo người, không theo thư mục:** làm Issue chức năng nào thì ghi dòng nhật ký của Issue đó vào đúng `docs/log/<vai>.md` của chính mình.

### 3.2 Quy tắc kiểm tra và Merge PR

- **Bỏ bắt buộc approve:** cấu hình Branch Protection trên `develop` và `main` đặt `required_approving_review_count = 0` và **không** bật yêu cầu duyệt từ CODEOWNERS (ADR-014).
- **Bắt buộc qua PR & CI (chặn cả admin):** bật `enforce_admins: true` và giữ `required_pull_request_reviews` trên cả `develop` và `main` → không ai được phép push trực tiếp lên nhánh chung; 100% thay đổi phải đi qua Pull Request.
- **Tự Squash & merge:** tác giả PR (hoặc người điều phối D khi hỗ trợ) **được tự bấm Squash & merge** vào `develop` khi thoả đủ 5 điều kiện sau:
  1. Hai check bắt buộc **`Lint & format`** và **`Test`** đều xanh và nhánh đã cập nhật với `develop` (`strict: true`).
  2. Có test cho hành vi mới (hoặc lý do chính đáng nêu trong PR) và `make check` xanh ở local.
  3. Đã điền đủ mục **"Giải thích được" (3 câu)** theo `docs/defense.md`.
  4. Đã cập nhật tài liệu liên quan, `CHANGELOG.md` (nếu đổi hành vi) và `docs/log/<vai>.md` của chính mình.
  5. Mọi comment thảo luận trên PR (nếu có) đã được giải quyết (`resolved`).
- **Review đồng đội tự nguyện & hậu kiểm:** thành viên vẫn được khuyến khích tag đồng đội xem giúp ở PR phức tạp (như đổi schema, API contract, CI/deploy hoặc diff lớn > 400 dòng), nhưng đây là hỗ trợ tự nguyện, không chặn quyền merge. Nếu sau merge phát hiện sai sót trên `develop`, mở Issue `[bug]` theo mục 11.3 và sửa qua PR mới.

### 3.3 Kênh liên lạc chính thức

| Kênh | Dùng cho |
|---|---|
| GitHub Issue | Việc cần làm, báo lỗi, câu hỏi kỹ thuật (**nguồn chân lý**) |
| GitHub PR | Thảo luận code, review |
| `docs/decisions.md` | Quyết định kiến trúc đã chốt |
| Zalo/Discord nhóm | Trao đổi nhanh; ghi quyết định và blocker vào Issue |
| `docs/standup.md` (tuỳ chọn) | Mẫu nhắn nhanh về blocker |

> Quy ước: **quyết định kỹ thuật chốt trên chat miệng = không tồn tại.** Phải được dán lại vào Issue/ADR.

---

## 4. Kiến trúc bất biến và phạm vi sửa các tầng

### 4.1 Kiến trúc mục tiêu

```
┌─────────────────────┐        HTTPS/JSON        ┌──────────────────────┐
│  GUI Desktop        │ ───────────────────────► │  FastAPI Backend     │
│  PySide6            │ ◄─────────────────────── │  JWT + RBAC          │
│  gui/               │                          │  api/                │
└─────────────────────┘                          └──────────┬───────────┘
                                                            │ SQLAlchemy
                                                 ┌──────────▼───────────┐
                                                 │  MySQL 8 (Docker)    │
                                                 └──────────────────────┘
     CI/CD, Docker, Đóng gói: infra/, installer/, .github/workflows/
```

**Quy tắc kiến trúc (BẮT BUỘC):**

- GUI **KHÔNG ĐƯỢC** kết nối MySQL trực tiếp. Mọi truy cập dữ liệu đi qua `gui/api_client.py` → REST API.
- Router **KHÔNG ĐƯỢC** chứa business logic hay câu SQL. Router → Service → Model.
- Service **KHÔNG ĐƯỢC** import từ `gui/`. Chiều phụ thuộc một chiều: `gui → api → db`.
- Không import vòng (circular import). Nếu cần → tách interface.
- Dù **cùng một người** làm trọn gói cả GUI lẫn API cho một chức năng trong Issue, vẫn **CẤM** gọi tắt từ `gui/` sang `api.models` hoặc SQL.

### 4.2 Cấu trúc thư mục

```
cafe-tlu/
├── api/                    # Backend FastAPI (skill: fastapi-endpoint)
│   ├── main.py             # tạo FastAPI app, mount router
│   ├── core/               # config, security, deps (get_db, get_current_user)
│   ├── routers/            # mỏng: chỉ validate + gọi service
│   ├── services/           # business logic (reports.py cho thống kê & export)
│   ├── models/             # SQLAlchemy models
│   └── schemas/            # Pydantic
├── db/                     # MySQL (skill: sqlalchemy-model)
│   ├── schema.sql          # DDL chuẩn (nguồn chân lý)
│   ├── seed.sql            # dữ liệu mẫu 51 món, 120 đơn
│   ├── verify_seed.sql     # kiểm chứng dữ liệu mẫu (23 phép)
│   └── migrations/         # Alembic
├── gui/                    # Giao diện PySide6 (skill: pyside6-screen + ui-design)
│   ├── main.py
│   ├── api_client.py       # lớp duy nhất gọi HTTP
│   ├── views/              # mỗi màn hình 1 file
│   ├── widgets/            # component tái sử dụng
│   ├── theme.py            # màu, font, spacing — không hardcode trong view
│   └── i18n.py             # chuỗi tiếng Việt tập trung
├── shared/                 # dùng chung: constants, error codes, paths, version
├── scripts/                # next_task.sh, smoke_test.py, seed_data.py, backup_db.sh, build_installer.sh
├── tests/                  # pytest (skill: pytest-db)
├── infra/                  # Docker prod, nginx, deploy.md
├── installer/              # Inno Setup .iss, .spec, app.ico (skill: win-installer)
├── assets/                 # icon, ảnh món, logo, font Manrope
├── docs/                   # decisions, api-contract, erd, plan, workflow, test-cases, log/
├── report/                 # báo cáo BTL (10 file theo chương)
├── .github/workflows/      # CI/CD (ci.yml, release.yml)
├── .env.example            # BẮT BUỘC có, commit
├── Makefile                # make next / doctor / up / api / gui / test / lint / build-installer
├── requirements.txt
├── CHANGELOG.md
└── README.md
```

### 4.3 Phạm vi sửa file theo Issue chức năng

| Được sửa trọn gói theo Issue chức năng | Phải ghi rõ trong Issue/PR & đồng bộ tài liệu | CẤM tuyệt đối |
|---|---|---|
| `api/` (routers, services, models, schemas) | `db/schema.sql` (kèm migration Alembic mới + `docs/erd.md` + `verify_seed.sql`) | `main`, `develop` (push trực tiếp — bị chặn) |
| `gui/`, `assets/` | `docs/api-contract.md` (cập nhật contract & trạng thái) | Sửa migration Alembic **đã merge** |
| `db/seed.sql`, migration Alembic **mới** | `requirements.txt` (thêm/đổi thư viện, ghi lý do 1 dòng trong Issue) | Sửa `docs/log/<vai>.md` của **người khác** |
| `shared/` (nêu rõ trong PR nếu đổi contract chung) | `.github/workflows/`, `installer/`, `Makefile` | Commit `.env` thật, secret, token, `*.db`, `dist/`, `build/` |
| `tests/`, `docs/`, `report/` thuộc chức năng | `WORKFLOW.md` (mở Issue/PR riêng và báo nhóm) | Đưa code/logic vòng qua kiến trúc `gui → api → db` |

---

## 5. Vòng đời một việc (quy trình chuẩn)

```
Issue (gán theo chức năng) → Branch → Code + Test → Commit → Push → PR
   → CI xanh + Checklist đủ → Squash vào develop → Nghiệm thu → Đóng Issue
   → (theo lịch) release/vX.Y → merge main + tag → build installer tự động
```

### 5.1 Issue

Mỗi chức năng hoặc công việc có một Issue, **1 assignee** (thành viên thực hiện), **1 milestone** (cổng), các nhãn tầng kỹ thuật chạm tới (`api`, `gui`, `db`, `report`, `infra`, `docs`) và ước lượng S/M/L. Việc dưới 30 phút dùng nhãn `quick`. Nội dung gồm **kết quả, nghiệm thu và phụ thuộc** theo mục 6.1. Báo lỗi dùng nhãn `bug`, ghi cách tái hiện, môi trường, kết quả thực tế và log liên quan ngay trong mục nghiệm thu.

### 5.2 Nhánh

Đặt tên: `<loại>/<scope>-<mô-tả-ngắn>-<viết-tắt-tên>`

| Loại | Dùng khi | Ví dụ |
|---|---|---|
| `feature/` | Tính năng mới | `feature/order-merge-table-cuong` |
| `fix/` | Sửa lỗi | `fix/auth-token-expired-an` |
| `docs/` | Chỉ tài liệu | `docs/report-chapter3-dung` |
| `chore/` | Cấu hình, dependency | `chore/add-pytest-qt` |
| `hotfix/` | Sửa gấp từ `main` | `hotfix/installer-missing-dll` |

**Tạo và đồng bộ nhánh:**

- Luôn tạo nhánh từ `develop` **mới nhất**: `git switch develop && git pull && git switch -c feature/...`
- **Sau 3 ngày**, rà lại phạm vi nhánh và đồng bộ `develop` nếu cần.
- Trước khi mở PR: `git rebase develop` (không merge `develop` vào nhánh feature).

### 5.3 Commit

Theo **Conventional Commits**: `<loại>(<scope>): <mô tả ngắn ở thể mệnh lệnh>`

| Loại | Dùng khi |
|---|---|
| `feat` | Thêm chức năng |
| `fix` | Sửa lỗi |
| `refactor` | Đổi cấu trúc, không đổi hành vi |
| `test` | Thêm/sửa test |
| `docs` | Tài liệu |
| `chore` | Build, CI, dependency |
| `perf` | Tối ưu hiệu năng |
| `style` | Format, không đổi logic |

**Scope hợp lệ:** `db`, `api`, `auth`, `order`, `product`, `report`, `gui`, `infra`, `ci`, `installer`, `docs`, `deps`.

**Quy tắc commit:**

- Mỗi commit **một ý**; không commit 40 file lung tung.
- Dòng tiêu đề ≤ 72 ký tự, tiếng Việt có dấu, **không viết hoa đầu câu**, **không dấu chấm cuối**.
- Thân commit (nếu cần) giải thích **vì sao**, không phải **cái gì** (cái gì đã thấy trong diff).
- **KHÔNG ĐƯỢC** commit: `.venv/`, `dist/`, `build/`, `__pycache__/`, `*.pyc`, `.env`, `*.db`, `*.sqlite`, ảnh > 2MB, file > 5MB.
- **KHÔNG ĐƯỢC** `git add .` mù quáng → luôn `git add <path>` cụ thể hoặc review `git status` trước.
- Nếu code do AI sinh ra: thêm dòng cuối `Co-authored-by: <Tên AI> <model>` và ghi chú trong PR.

### 5.4 Pull Request

- Dùng tiêu đề Conventional Commits vì squash merge dùng tiêu đề PR. Tự assign chính mình, ghi `Refs #<issue>` để truy vết, gắn nhãn các tầng chạm tới và điền [mẫu PR](.github/pull_request_template.md).
- Mẫu PR giữ kết quả thay đổi, bằng chứng kiểm chứng và ba câu bảo vệ. UI có ảnh khi hoàn thiện hoặc đổi màn hình. Backend, DB, CI và docs dùng lệnh, kết quả và link CI.
- Khoảng 400 dòng diff là mốc rà phạm vi. Tách phần độc lập khi có thể. Nếu các thay đổi cần đi cùng nhau, ghi lý do trong PR.

### 5.5 Tự kiểm & Review tự nguyện

Trước khi merge (hoặc khi đồng đội xem giúp theo lời tag), dùng checklist chung trong [mẫu PR](.github/pull_request_template.md) và kiểm kỹ ba điểm hay sót:

- **Đọc cả vùng code bị chạm, không chỉ diff** — mở file gọi tới hàm/endpoint/component vừa đổi.
  Lỗi hay nằm ở file *không* có trong diff.
- **Test phải kiểm tra hành vi**, không phải test cho có (assert phải đỏ được nếu logic sai).
- **Diff không chứa code "để sau này"**; chỗ cố ý cắt bớt phải có `shortcut:` (mục 7.1).

Khi đồng đội góp ý trên PR, dùng tiền tố phân loại để rõ mức độ:

| Tiền tố | Ý nghĩa | Người viết code |
|---|---|---|
| `[must]` | Lỗi nghiêm trọng / vỡ hợp đồng cần sửa trước khi merge (hoặc mở Issue `[bug]` ngay) | Phải xử lý |
| `[should]` | Nên sửa | Sửa hoặc giải thích lý do |
| `[nit]` | Nhỏ, không chặn | Tuỳ |
| `[question]` | Cần làm rõ | Trả lời |
| `[praise]` | Khen (khuyến khích dùng) | – |

### 5.6 Merge & phát hành

- Merge vào `develop` bằng **Squash and merge** (giữ lịch sử sạch, 1 commit = 1 việc). Khi CI xanh và đủ checklist mục 3.2, tác giả tự bấm merge mà **không cần chờ approve**.
- Tác giả (hoặc người điều phối D) xác nhận tiêu chí Issue trên `develop`, thêm link PR vào Issue, rồi đóng Issue khi đạt Definition of Done. PR merge vào `develop` cần bước này vì nhánh mặc định là `main`. Xoá nhánh sau merge.
- `develop` **PHẢI** luôn chạy được: hết mỗi ngày, CI xanh.
- Phát hành: `develop → release/vX.Y` → test → CI build installer → `main` + tag `vX.Y.Z` + GitHub Release.

---

## 6. Definition of Ready / Definition of Done

### 6.1 Definition of Ready

- **Kết quả** rõ ràng và có **tiêu chí nghiệm thu** kiểm được.
- **Phụ thuộc** ghi theo Issue, API, bảng hoặc dữ liệu cần có. Đổi contract/schema hoặc thêm thư viện cần nêu rõ theo mục 4.
- Có metadata theo mục 5.1 (assignee theo chức năng, milestone, nhãn tầng kỹ thuật). Assignee nhận việc khi các phụ thuộc bắt buộc đã sẵn sàng.

### 6.2 Definition of Done

- PR có kiểm thử hoặc lý do phù hợp, bằng chứng kiểm chứng thật và checklist chung đã rà.
- Local chạy `make check`. CI xanh, comment đã resolve (nếu có), tự squash vào `develop` và xác nhận tiêu chí trên nhánh này.
- Cập nhật tài liệu liên quan, changelog khi đổi hành vi, ảnh vào `docs/screenshots/` khi đổi màn hình và nhật ký cá nhân ở mục 2 và 3.
- Tác giả trả lời được ba câu bảo vệ trong PR, ghi link PR và đóng Issue sau khi xác nhận các mục trên.

## 6.3 Hiểu bài — điều kiện không thể thương lượng

Đề bài: **copy = 0 điểm**. Giảng viên có thể hỏi **bất kỳ phần nào**, kể cả phần của người khác.

| Việc | Ở đâu |
|---|---|
| Mỗi PR phải có 3 câu "Giải thích được" | Template PR, `docs/defense.md` |
| Ngân hàng câu hỏi GV hay hỏi theo từng vùng | `docs/defense.md` mục "Ngân hàng câu hỏi" |
| Hỏi chéo 15 phút mỗi thứ 6 (2 câu về vùng người khác) | `docs/defense.md` mục "Quy trình 15 phút" |
| Câu chưa trả lời được → ghi sổ, trả lời lại tuần sau | `docs/defense.md` mục "Sổ chưa trả lời được" |

**Luật cứng:** không merge PR mà mình không giải thích được, kể cả khi CI xanh.

> 💡 Ảnh chụp lưu **ngay khi xong việc** là mẹo ăn điểm mốc 8 ("chụp ảnh các bước đầy đủ, cẩn thận") — đến G5 không phải dựng lại app để chụp.

---

## 7. Quy chuẩn code Python

### 7.1 Chung

- **Python 3.12+**, mỗi người dùng `venv` riêng trong repo: `python -m venv .venv`.
- **BẮT BUỘC** type hints cho mọi hàm public.
- **BẮT BUỘC** docstring ngắn (1–3 dòng) cho module, class, hàm public.
- Format & lint **BẮT BUỘC** qua `ruff` + `black` (dòng 100 ký tự). Không tranh luận style bằng tay — để công cụ quyết.
- `pre-commit` **NÊN** được cài để tự chạy trước mỗi commit.
- Độ dài hàm **NÊN** ≤ 50 dòng; file **NÊN** ≤ 400 dòng. Vượt → tách.
- **CẤM** `print()` trong code sản phẩm → dùng `logger`.
- **CẤM** `except:` trần hoặc `except Exception: pass`. Phải bắt cụ thể và xử lý/log.
- **CẤM** hardcode: mật khẩu, connection string, đường dẫn tuyệt đối (`C:\Users\...`), URL server, magic number có ý nghĩa → đưa vào `api/core/config.py` hoặc `shared/constants.py`.

#### Quy ước `shortcut:` — đánh dấu chỗ cắt bớt có chủ ý

Khi cố ý làm bản đơn giản hơn để kịp tiến độ, **BẮT BUỘC** để lại một comment đúng dạng:

```python
# shortcut: bỏ gộp bàn khác khu vực, nâng cấp khi có yêu cầu từ quán (mốc 8)
# shortcut: chưa giới hạn số lần đăng nhập sai, thêm rate limit trước G4
```

Lý do: "để sau" rất dễ thành "không bao giờ". Comment này cho phép:

- `grep -rn "shortcut:" --include=*.py .` ra toàn bộ nợ kỹ thuật hiện có;
- đưa thẳng vào chương **"Khó khăn & hướng phát triển"** của báo cáo;
- reviewer biết đó là quyết định, không phải sơ suất.

**CẤM** lạm dụng: `shortcut:` không phải giấy phép bỏ qua validate ở trust boundary, xử lý lỗi
chống mất dữ liệu, bảo mật, hay accessibility (xem `WORKFLOW.md` mục 9 và skill `security`).

### 7.2 Đặt tên

| Loại | Quy ước | Ví dụ |
|---|---|---|
| Module/file | `snake_case` | `order_service.py` |
| Class | `PascalCase` | `OrderService`, `ProductView` |
| Hàm/biến | `snake_case` | `calculate_total`, `unit_price` |
| Hằng số | `UPPER_SNAKE` | `MAX_PAGE_SIZE = 100` |
| Private | tiền tố `_` | `_build_query()` |
| Enum | `PascalCase` class, `UPPER_SNAKE` member | `class OrderStatus: PENDING = "pending"` |
| Handler sự kiện GUI | `on_<hành_động>` | `on_save_clicked` |

**CẤM** viết tắt khó hiểu (`prd`, `usr`), tên tiếng Việt không dấu (`them_mon`), tên 1 ký tự ngoài vòng lặp.

### 7.3 Xử lý lỗi & logging

- Lỗi nghiệp vụ → raise exception riêng, kế thừa `AppError` (trong `shared/errors.py`), có `code` + `message` tiếng Việt cho người dùng.
- API trả lỗi theo format mục 9.3. **Không** trả stack trace ra client.
- Logging: dùng `logging` với `logger = logging.getLogger(__name__)`.
  - `INFO`: hành động nghiệp vụ (tạo đơn, đăng nhập).
  - `WARNING`: bất thường có thể xử lý (sai mật khẩu, hết tồn kho).
  - `ERROR`: exception, kèm `exc_info=True`.
  - **CẤM** log mật khẩu, token, số điện thoại/CCCD đầy đủ.
- Mọi thao tác DB trong service **PHẢI** có transaction rõ ràng; lỗi → rollback.

### 7.4 Dependency

- Chỉ thêm thư viện khi **thực sự cần** và **có bảo trì** (kiểm tra sao trên GitHub, ngày cập nhật cuối).
- **PHẢI** xin phép trong Issue trước khi thêm; ghi lý do 1 dòng.
- Pin phiên bản trong `requirements.txt` (`PySide6==6.7.2`), không dùng `latest`.
- Tách `requirements-dev.txt` (pytest, ruff, black, pre-commit).
- **CẤM** thêm thư viện không rõ nguồn gốc hoặc copy từ tutorial mà không đọc code.

---

## 8. Quy chuẩn cơ sở dữ liệu (MySQL)

### 8.1 Quy tắc chung

- **`db/schema.sql` là nguồn chân lý của DDL.** Mọi thay đổi đi kèm migration Alembic + cập nhật file này.
- **CẤM** sửa migration đã merge. Cần đổi → tạo migration **mới**.
- **CẤM** `DROP TABLE` / `TRUNCATE` / `DELETE` không có `WHERE` trên dữ liệu thật. Script dọn dữ liệu phải có backup trước.
- **CẤM** đổi tên/xoá cột đang dùng mà không thông báo — phải thêm cột mới + migrate dữ liệu, rồi mới xoá ở phiên bản sau.
- Charset **bắt buộc** `utf8mb4`, collation `utf8mb4_unicode_ci`.
- Engine **bắt buộc** `InnoDB`.

### 8.2 Quy ước đặt tên

| Đối tượng | Quy ước | Ví dụ |
|---|---|---|
| Bảng | `snake_case`, **số nhiều** | `products`, `order_items` |
| Cột | `snake_case` | `unit_price` |
| Khoá chính | `id` (`BIGINT UNSIGNED AUTO_INCREMENT`) | `id` |
| Khoá ngoại | `<bảng_số_ít>_id` | `product_id`, `order_id` |
| Boolean | tiền tố `is_` / `has_` | `is_available`, `is_deleted` |
| Thời gian | `created_at`, `updated_at`, `deleted_at` | DATETIME, default `CURRENT_TIMESTAMP` |
| Index | `idx_<bảng>_<cột>` | `idx_products_name` |
| Unique | `uq_<bảng>_<cột>` | `uq_users_username` |
| FK | `fk_<bảng>_<bảng_cha>` | `fk_orders_tables` |

### 8.3 Bắt buộc

- Mọi bảng nghiệp vụ **PHẢI** có `created_at`, `updated_at`.
- Xoá mềm bằng `is_deleted` (mặc định `0`) với dữ liệu quan trọng (đơn hàng, hoá đơn); **không** xoá cứng.
- Tiền tệ: `DECIMAL(12,0)` (VNĐ, không phần lẻ) — **CẤM** dùng `FLOAT`/`DOUBLE` cho tiền.
- Unique constraint cho nghiệp vụ: `username`, `(order_id, product_id)` nếu cần.
- Index cho cột tìm kiếm/lọc thường dùng (`products.name` — cân nhắc `FULLTEXT`), cột FK, cột ngày trong báo cáo.
- Query thống kê **PHẢI** dùng `GROUP BY`/`JOIN` trong SQL, **CẤM** lấy hết dữ liệu về Python rồi lặp.
- `seed.sql` **PHẢI** idempotent (`INSERT ... ON DUPLICATE KEY UPDATE` hoặc `INSERT IGNORE`) để chạy lại không lỗi.
- Truy vấn từ code **PHẢI** dùng tham số hoá (SQLAlchemy ORM / `text()` + bind params). **CẤM** nối chuỗi SQL → chống SQL injection.

---

## 9. Quy chuẩn API

### 9.1 Contract-first (BẮT BUỘC)

- `docs/api-contract.md` được chốt trước khi code các phần phụ thuộc lẫn nhau.
- Đổi hoặc bổ sung contract (thêm/xoá/đổi endpoint, field, mã lỗi) → ghi rõ trong Issue/PR, cập nhật `docs/api-contract.md` đồng bộ với code (hoặc PR riêng trước đó) và thông báo nhóm; **không** sửa lén mà không báo.
- FastAPI **PHẢI** sinh Swagger tại `/docs` và `/redoc` — dùng làm tài liệu chính thức.

### 9.2 Quy ước endpoint

- Tiền tố: `/api/v1/...` (version trong path).
- Tài nguyên số nhiều: `GET /api/v1/products`, `GET /api/v1/products/{id}`.
- Hành động phi CRUD: động từ ở cuối: `POST /api/v1/orders/{id}/checkout`, `POST /api/v1/orders/{id}/merge-table`.
- Phân trang: `?page=1&page_size=20` (mặc định 20, tối đa 100).
- Lọc & tìm: `?search=trà&category_id=3&min_price=20000&sort=-created_at`.
- Mã HTTP đúng nghĩa: 200/201/204/400/401/403/404/409/422/500.
- Response **PHẢI** là JSON, `Content-Type: application/json; charset=utf-8`.

### 9.3 Định dạng response (BẮT BUỘC thống nhất)

Thành công:
```json
{
  "data": { "id": 12, "name": "Trà đào cam sả", "price": 35000 },
  "meta": null
}
```

Danh sách có phân trang:
```json
{
  "data": [ { "id": 1 } ],
  "meta": { "page": 1, "page_size": 20, "total": 57, "total_pages": 3 }
}
```

Lỗi:
```json
{
  "error": {
    "code": "PRODUCT_NAME_DUPLICATED",
    "message": "Tên món đã tồn tại",
    "details": { "field": "name" }
  }
}
```

- `code` là **hằng số UPPER_SNAKE** trong `shared/error_codes.py`, không đổi sau khi đã phát hành.
- `message` là tiếng Việt, hiển thị được trực tiếp cho người dùng cuối.
- **CẤM** trả `detail` mặc định của FastAPI ra ngoài — phải qua exception handler chung.

**Ngoại lệ duy nhất: `/health`** (và bí danh `/api/v1/health`) — xem ADR-011.

```json
{ "status": "ok", "version": "0.1.0", "database": "ok" }
```

- Trả **phẳng**, không bọc `data`/`meta`/`error`. Lý do: Docker `healthcheck`, script `make doctor`
  và probe của bộ cài đọc thẳng `status`/`database`, không qua lớp xử lý response của GUI.
- HTTP **200** khi DB thông, **503** khi DB không thông (`status: "degraded"`, `database: "error"`).
  Trường hợp 503 vẫn **không** dùng envelope `error`.
- Ngoại lệ này **chỉ** áp cho health check. Mọi endpoint khác, kể cả nội bộ, phải theo mục 9.3.

### 9.4 Bảo mật API

- JWT trong header `Authorization: Bearer <token>`; access token 30 phút, refresh 7 ngày.
- Mọi endpoint (trừ `/auth/login`, `/health`) **PHẢI** yêu cầu xác thực.
- Kiểm tra quyền **ở server**, không chỉ ẩn nút ở GUI. Ẩn nút chỉ là UX.
- Rate limit cơ bản cho `/auth/login` (VD 5 lần/phút/IP) — chống dò mật khẩu.

---

## 10. Quy chuẩn GUI

- **KHÔNG** gọi DB trực tiếp; mọi dữ liệu qua `gui/api_client.py`.
- Mỗi màn hình = 1 class kế thừa `BaseView` (`gui/views/base.py`), có `load()`, `refresh()`, `on_close()`.
- Màu, font, spacing **CHỈ** khai báo trong `gui/theme.py`. **CẤM** `setStyleSheet("color: #ff0000")` rải rác trong view.
- Chuỗi hiển thị **CHỈ** trong `gui/i18n.py` (hỗ trợ sửa hàng loạt, tránh lỗi font). Tiếng Việt có dấu, UTF-8.
- Mọi tác vụ gọi API **PHẢI** chạy nền (QThread/`QThreadPool` hoặc worker), **CẤM** gọi HTTP đồng bộ trên luồng UI → treo app.
- Mọi màn hình **PHẢI** có 4 trạng thái: `loading`, `empty`, `error`, `data`.
- Mọi form **PHẢI** validate trước khi gửi: bắt buộc nhập, giá > 0, độ dài, trùng tên.
- Thao tác phá huỷ (xoá, huỷ đơn) **PHẢI** có hộp thoại xác nhận.
- Thông báo **NÊN** dùng toast/inline, hạn chế `QMessageBox` cho lỗi thường gặp.
- Phím tắt **NÊN** có: `Ctrl+F` tìm, `F5` refresh, `Ctrl+S` lưu, `Esc` đóng dialog.
- **PHẢI** test resize cửa sổ ở 3 kích thước (1280×720, 1600×900, full HD) trước khi mở PR.

---

## 11. Quy chuẩn kiểm thử

### 11.1 Phân tầng test

| Tầng | Công cụ | Phạm vi | Trách nhiệm |
|---|---|---|---|
| Unit | `pytest` | Service, tính toán tiền, validate, phân quyền | Người làm Issue chức năng |
| API | `pytest` + `TestClient` | Endpoint: đúng mã HTTP, đúng schema, đúng quyền | Người làm Issue chức năng |
| DB | `pytest` + `cafe_tlu_test` | Query thống kê, migration, ràng buộc CHECK/FK | Người làm Issue chức năng |
| Smoke | `scripts/smoke_test.py` | Luồng chính: login → order → thanh toán → xem báo cáo | Người nhận Issue G3 (#97) |
| UI thủ công | Checklist trong `docs/test-cases.md` | Từng màn hình end-to-end | Người làm chức năng + QA G5 |

### 11.2 Quy tắc

- Mọi **bug fix PHẢI** kèm test tái hiện bug (test đỏ trước, xanh sau).
- **CẤM** sửa/xoá test để CI xanh, trừ khi test đó sai — và phải nói rõ lý do trong PR.
- Test **PHẢI** độc lập, không phụ thuộc thứ tự chạy, không gọi mạng thật (dùng mock/fixture).
- Dùng DB test riêng (`cafe_tlu_test`), **CẤM** test trên DB dev.
- Coverage mục tiêu: `api/services` ≥ **60%** (không đặt nặng con số, đặt nặng hành vi quan trọng).
- Mọi test **PHẢI** chạy được bằng **một lệnh**: `make test`.
- Kết quả test của lần chạy cuối phải được dán vào PR (số pass/fail), không nói "em test rồi".

### 11.3 Bug report (Issue label `bug`)

**PHẢI** có: môi trường (OS, phiên bản app), bước tái hiện (1-2-3), kết quả mong đợi, kết quả thực tế, log liên quan;
ảnh chụp/video **chỉ khi** lỗi nằm ở giao diện. Thiếu bước tái hiện → không xử lý.

---

## 12. Quy chuẩn tài liệu & minh chứng

### 12.1 Nguyên tắc "tài liệu đi cùng code"

- Mỗi PR đổi hành vi **PHẢI** cập nhật tài liệu liên quan **trong cùng PR** (không tách PR sau).
- **CẤM** để tài liệu lỗi thời: nếu code khác docs, docs là sai và phải sửa ngay.

### 12.2 Ai viết gì

| Tài liệu | Trách nhiệm | Ghi chú |
|---|---|---|
| `docs/api-contract.md` | Người thêm/sửa endpoint | Cập nhật đồng bộ mỗi khi thêm hoặc đổi endpoint |
| `docs/erd.md` | Người đổi schema (khi chạm DB) | Giữ khớp `db/schema.sql`, từ điển cột và bất biến |
| `README.md` | D điều phối | Cài & chạy trong 3 lệnh + tiêu chí 6 cổng và link milestone |
| `CHANGELOG.md` | Cả nhóm (D biên tập) | Mỗi PR đổi hành vi thêm 1 dòng vào mục `Unreleased` |
| `docs/decisions.md` | Người ra quyết định | ADR-lite, xem 18.4 |
| `docs/test-cases.md` | Người làm chức năng + QA (G5) | Điền PASS/FAIL thật sau khi chạy end-to-end |
| `docs/log/<vai>.md` | **Chính chủ file đó** (`A/B/C/D`) | Ghi mọi Issue chức năng mình làm + AI đã hỗ trợ, xem 12.5 |
| Báo cáo BTL (`report/`) | Chia theo Issue/chương (D biên tập) | Điền từ code và số liệu thật của nhóm |
| Video demo | Người nhận Issue G5 (#103) | 3–5 phút, có thuyết minh tiếng Việt |

### 12.3 Chụp ảnh màn hình (phục vụ báo cáo mốc 8)

- Lưu tại `docs/screenshots/<module>/<mô-tả>-<YYYYMMDD>-<số>.png`.
- VD: `docs/screenshots/order/order-merge-table-20261120-01.png`.
- **PHẢI**: chụp **toàn cửa sổ**, dữ liệu thật (không để trống), độ phân giải ≥ 1280px ngang, không chụp màn hình có thông báo Zalo/trình duyệt cá nhân.
- Mỗi ảnh dùng trong báo cáo **PHẢI** có caption giải thích.

### 12.4 Ngôn ngữ & định dạng báo cáo

- Tiếng Việt, có dấu, font Times New Roman 13 / Arial 12 (thống nhất toàn báo cáo).
- Mỗi chương: mở đầu bằng 2–3 câu dẫn, kết bằng 1 đoạn tổng kết ngắn.
- Code trong báo cáo dùng font monospace, **≤ 30 dòng** mỗi đoạn, có caption "Hình X.Y: ...".
- **CẤM** dán ảnh chụp code dài; **CẤM** copy nguyên văn tài liệu nước ngoài không trích nguồn.

### 12.5 Nhật ký cá nhân — `docs/log/<vai>.md` (BẮT BUỘC)

Mỗi thành viên giữ **một** file: [`docs/log/A.md`](docs/log/A.md) · `B.md` · `C.md` · `D.md`
(quy tắc + mẫu ở [`docs/log/README.md`](docs/log/README.md)).

**Để làm gì:** khi GV hỏi *"phần này em làm gì? AI làm gì? sao không dùng cách khác?"* — mở đúng 1
file, trả lời trong 30 giây, kèm commit/PR/lệnh đã chạy. Đây là **sổ bằng chứng**, không phải báo
cáo nộp bài (báo cáo ở `report/`).

**Sáu mục bắt buộc:**

| Mục | Nội dung |
|---|---|
| 1. Tôi phụ trách gì | 3–5 gạch đầu dòng, kèm Issue |
| 2. Việc đã làm | 1 dòng/PR: ngày · Issue · PR/commit · file chính · làm gì · **vì sao cách đó** |
| 3. AI đã làm gì | 1 dòng/phiên: công cụ · AI làm gì · **tôi sửa/kiểm chứng gì** |
| 4. Câu hỏi thầy hay hỏi | 5–8 câu vùng mình + trả lời 2–4 câu + chỉ vào `file:dòng` |
| 5. Chưa làm / chưa hiểu | danh sách thật — đây là đề cương ôn của bạn |
| 6. Nhật ký theo cổng | 1 dòng/cổng: đã xong gì, còn thiếu gì |

**Năm quy tắc:**

1. **Cập nhật trong cùng PR** đã làm việc — 3–5 phút, không dồn (DoD mục 6.2).
2. **Kiểm chứng được:** commit hash / số PR / lệnh đã chạy / ảnh. **CẤM** viết "đã hoàn thành".
3. **Ghi cả AI, không giấu.** Giấu rồi bị phát hiện = rủi ro 0 điểm; ghi rõ (AI nháp gì, mình sửa gì,
   kiểm chứng bằng gì) = minh bạch và được điểm quy trình.
4. **Chỉ người đó sửa file của mình.** Người khác nhắc qua comment, không sửa hộ.
5. **Không bịa số.** Chưa có thì ghi `chưa có`.

**Nhịp:** mỗi PR 3–5 phút · trước mỗi cổng 15 phút (rà mục 2, 4, 6) · trước bảo vệ 20 phút (đọc to
mục 4, xoá câu không chỉ được vào code). File trống ở thời điểm cổng = **cổng chưa xanh**.

---

### 12.6 Theo dõi tiến độ và kết quả qua cổng

- **GitHub Issues** giữ trạng thái và người phụ trách. Dùng [milestone G1–G6](https://github.com/Haianh4705/cafe-tlu/milestones) hoặc Project để xem cùng các Issue.
- Ghi phụ thuộc, blocker, PR và kết quả nghiệm thu trên Issue. Người phụ trách cập nhật khi có thay đổi. Người merge đóng Issue theo mục 5.6.
- **README** giữ tiêu chí, link từng milestone và kết quả khi qua cổng. **`docs/plan.md`** giữ phạm vi và thứ tự giao việc. D cập nhật kết quả cổng khi có minh chứng.

## 13. Quy chuẩn đóng gói & phát hành

### 13.1 Phiên bản

- Semantic Versioning `MAJOR.MINOR.PATCH`:
  - `MAJOR` = thay đổi phá vỡ (đổi schema/contract, mất tương thích)
  - `MINOR` = thêm chức năng
  - `PATCH` = sửa lỗi
- Phiên bản khai báo **một chỗ duy nhất**: `shared/version.py` (`__version__`), đọc lại ở GUI (About), installer, và API `/health`.
- Tag Git: `v1.0.0` trên `main`. **CẤM** tag trên `develop`.

### 13.2 Bản cài đặt (BẮT BUỘC — đề bài yêu cầu)

- Build bằng `PyInstaller` (`--onedir` cho khởi động nhanh) + `Inno Setup` → `CafeTLU-Setup-vX.Y.Z.exe`.
- **PHẢI** có: icon, license, shortcut Desktop + Start Menu, **uninstaller sạch**, không để lại file trong `Program Files`.
- **PHẢI** hoạt động trên máy **chưa cài Python và chưa cài MySQL client**.
- **PHẢI** có auto-update (kiểm tra version từ GitHub Releases khi khởi động, có nút "Cập nhật").
- Build **PHẢI** chạy tự động trên CI khi push tag — không build tay rồi upload (trừ khi CI hỏng, phải ghi lý do).
- **PHẢI** test trên máy ảo Windows sạch trước khi phát hành.

### 13.3 CI/CD (BẮT BUỘC, tối thiểu 3 job)

| Job | Trigger | Việc làm | Chặn merge? |
|---|---|---|---|
| `lint` | mọi PR | ruff + black --check | Có |
| `test` | mọi PR | pytest + coverage | Có |
| `build-installer` | tag `v*` | PyInstaller + Inno Setup → Release | – |
| `docker-image` | tag `v*` | build & push image backend | – |

- CI **PHẢI** xanh trước khi merge. Không có ngoại lệ "chạy lại là được" (flaky test phải sửa).
- Thời gian CI mục tiêu < 10 phút.

### 13.4 Deploy backend

- `docker compose up -d` trên VPS (hoặc Render/Railway).
- **PHẢI** có: healthcheck `/health`, HTTPS, biến môi trường qua `.env` (không commit), backup DB định kỳ.
- Ghi lại URL + hướng dẫn deploy vào `infra/deploy.md` để GV truy cập.

### 13.5 CHANGELOG

Theo [Keep a Changelog](https://keepachangelog.com/): mục `Unreleased` (Added/Changed/Fixed/Removed) + mỗi phiên bản có ngày. Mọi PR đổi hành vi **PHẢI** thêm 1 dòng.

---

## 14. Bảo mật & dữ liệu

- `.env` **BẮT BUỘC** nằm trong `.gitignore`. Chỉ commit `.env.example` (giá trị giả).
- **CẤM** commit: mật khẩu, token, API key, `*.pem`, `*.key`, backup DB, dữ liệu khách thật.
- Nếu lỡ commit secret → **báo ngay trong nhóm trong 5 phút**, đổi secret, và dùng `git filter-repo` để xoá khỏi lịch sử. Không chỉ xoá ở commit mới.
- Mật khẩu người dùng: hash **bcrypt** (cost ≥ 12). **CẤM** MD5/SHA1/plaintext.
- Nguyên tắc quyền tối thiểu: mỗi role chỉ thấy menu và gọi được API mình cần.
- Mọi thao tác ghi dữ liệu quan trọng (xoá đơn, đổi giá, sửa quyền) **PHẢI** ghi `audit_logs` (ai, làm gì, khi nào, giá trị cũ/mới).
- Dữ liệu demo/screenshot **PHẢI** dùng dữ liệu giả (không dùng tên/SĐT người thật).

---

## 15. Quy tắc dành riêng cho AI Agent

> Mục này áp dụng cho **mọi** AI (ChatGPT, Claude, Copilot, Cursor, DSH, agent CLI...) khi được dùng trong dự án. Người dùng AI vẫn **chịu trách nhiệm cuối cùng** về code được commit.

### 15.1 Nguyên tắc gốc

1. **Đọc trước, code sau.** PHẢI đọc `AGENTS.md` → `WORKFLOW.md` → `docs/decisions.md` → `docs/api-contract.md` → Issue được giao.
2. **Phạm vi tối thiểu.** Chỉ sửa file cần thiết cho Issue. Không "tiện tay" refactor, đổi format toàn file, hay đổi tên biến ngoài phạm vi.
3. **Không tự mở rộng yêu cầu.** Không thêm tính năng, thư viện, pattern mới mà Issue không yêu cầu.
4. **Không đoán khi thiếu thông tin.** Thiếu dữ kiện → dừng, hỏi, hoặc ghi rõ giả định trong báo cáo.
5. **Kiểm chứng trước khi báo xong.** Phải chạy lint + test và dán kết quả thật. **CẤM** nói "đã test" khi chưa chạy.
6. **Minh bạch nguồn gốc.** Mọi đoạn code AI sinh phải được người review hiểu; thêm `Co-authored-by` khi commit.

### 15.2 Ba mức quyền

| ✅ ĐƯỢC PHÉP | ⚠️ PHẢI HỎI TRƯỚC | ⛔ BỊ CẤM |
|---|---|---|
| Đọc mọi file trong repo | Đổi `db/schema.sql`, ERD khi Issue không yêu cầu | Push trực tiếp `main`/`develop` |
| Tạo nhánh `feature/*`, `fix/*`, `docs/*` | Đổi API contract (nhất là breaking) | `git push --force` lên nhánh chung |
| Sửa file thuộc phạm vi **Issue chức năng** được giao (`api/`, `gui/`, `db/`, `tests/`, `docs/`...) | Thêm/đổi dependency trong `requirements.txt` | Commit `.env`, secret, token, key |
| Thêm/sửa test | Đổi cấu trúc thư mục, tên module | `DROP`/`TRUNCATE`/`DELETE` không `WHERE` |
| Chạy `make lint`, `make test`, `make api`, `make up` | Đổi `.github/workflows/`, `installer/` (ngoài phạm vi Issue) | Sửa test để pass thay vì sửa code |
| Tạo migration **mới** (khi Issue cần) | Bump version / tạo tag / tạo Release | Xoá file không liên quan tới Issue |
| Cập nhật docs cùng PR | Sửa file **ngoài phạm vi** Issue được giao | `git add .` / `git commit -am` |
| Chạy script smoke test | Bật/tắt cờ tính năng | Đưa `print()` debug vào code sản phẩm |
| Đề xuất cải tiến (dạng ghi chú) | Đổi `WORKFLOW.md` | Tự bấm merge PR khi chưa được người dùng yêu cầu hoặc khi CI chưa xanh |
| | | Bịa kết quả test / bịa log |

### 15.3 Quy trình bắt buộc mỗi phiên làm việc

```
1. ĐỌC      : AGENTS.md, WORKFLOW.md, docs/decisions.md, docs/api-contract.md, Issue
2. ĐỒNG BỘ  : git switch develop && git pull --ff-only
3. NHÁNH    : git switch -c feature/<scope>-<slug>-<ten>
4. BASELINE : make lint && make test        # ghi lại trạng thái TRƯỚC khi sửa
5. LÀM      : thay đổi nhỏ nhất đủ đáp ứng Issue, từng bước có thể chạy được
6. KIỂM CHỨNG: make lint && make test  (+ chạy tay luồng chính nếu là GUI/API)
7. TÀI LIỆU : cập nhật docs liên quan + CHANGELOG + docs/log/<vai>.md
             (+ ảnh chụp nếu vừa hoàn thiện/đổi một màn hình — để dành cho báo cáo)
8. COMMIT   : conventional commit, nhỏ, đúng scope
9. PR       : theo template, ghi Refs #<issue>, gắn nhãn các tầng chạm tới
10. MERGE   : chờ CI xanh → (theo lệnh người dùng) Squash vào develop → nghiệm thu & đóng Issue
11. BÁO CÁO : theo mẫu 15.4 (dán vào PR hoặc chat cho người giao việc)
```

**CẤM** bỏ qua bước 4 và 6. Nếu bước 4 đã đỏ từ trước → báo ngay, không tự sửa ngoài phạm vi để "dọn".

### 15.4 Mẫu báo cáo bàn giao (handoff) — BẮT BUỘC

AI **PHẢI** kết thúc phiên bằng báo cáo đúng cấu trúc này:

```markdown
## Tóm tắt
<1–3 câu: đã làm gì, cho Issue nào>

## Đã thay đổi
| File | Thay đổi | Lý do |
|---|---|---|
| api/routers/orders.py | thêm endpoint merge-table | Issue #42 |

## Cách kiểm chứng
| Lệnh | Kết quả |
|---|---|
| `make test` | 48 passed, 2 skipped |
| `make lint` | clean |
| Thủ công | đăng nhập role staff → order 3 món → gộp bàn OK |

## Ảnh chụp / minh chứng
docs/screenshots/order/order-merge-table-20261120-01.png

## Chưa làm / còn lại
- Chưa xử lý gộp bàn khi 2 bàn đã thanh toán (đề xuất Issue mới)

## Rủi ro / lưu ý cho reviewer
- Endpoint mới cần index `idx_orders_table_id` để chạy nhanh với 5k đơn

## Câu hỏi cần người quyết
- Có cho phép gộp bàn khác khu vực không?
```

### 15.5 Khi không chắc chắn

AI **PHẢI** chọn một trong ba hành vi sau (không được im lặng):

| Tình huống | Hành vi |
|---|---|
| Thiếu thông tin nghiệp vụ | **Dừng**, hỏi cụ thể 1–3 câu, kèm phương án đề xuất |
| Có nhiều cách làm hợp lý | Chọn cách **đơn giản nhất đáp ứng Issue**, ghi rõ đã cân nhắc gì khác |
| Việc vượt phạm vi (cần đổi schema/contract/dependency) | **Không tự làm**, mở ghi chú đề xuất + chờ duyệt |

### 15.6 Chống đạo văn (điều kiện bắt buộc của môn học)

- Đề bài: **copy = 0 điểm**. AI **KHÔNG ĐƯỢC** tạo ra bài "dán vào là xong" mà thành viên không hiểu.
- Mọi đoạn code AI sinh **PHẢI**: (a) được một thành viên đọc và hiểu, (b) được review trong PR, (c) ghi chú `Co-authored-by` trong commit.
- AI **PHẢI** giải thích ngắn gọn (2–4 dòng trong PR) đoạn code quan trọng làm gì và **vì sao chọn cách đó** — để người học hiểu và bảo vệ được trước GV.
- **CẤM** dùng AI để viết nguyên chương báo cáo mà không có dữ liệu/số liệu thật của nhóm.

### 15.7 AI phải ghi nhật ký thay người dùng

Kết thúc mỗi phiên, AI **PHẢI**:

1. Thêm **1 dòng** vào mục 2 của `docs/log/<vai>.md` (việc đã làm + vì sao cách đó) và **1 dòng** vào
   mục 3 (AI nháp gì · người dùng đã sửa/kiểm chứng gì).
2. Nếu phát hiện điều người dùng **chưa giải thích được** → thêm vào mục 5 thay vì bỏ qua.
3. Nếu chưa biết đó là vai nào → hỏi, **không tự chọn** file của người khác.
4. **CẤM** ghi vào `docs/log/` của người khác; **CẤM** ghi "đã test" khi chưa chạy.

Lý do: nhật ký viết sau (vài tuần) sẽ mất chi tiết và dễ thành văn mẫu — đúng thứ bị hỏi khi bảo vệ.

---

## 16. Nhịp làm việc & giao tiếp

### 16.1 Khi có thay đổi hoặc blocker

Ghi thay đổi trạng thái ngay trên Issue hoặc trên thẻ Issue trong Project. Nếu bị chặn quá hai giờ, ghi điều đang chờ và tag người xử lý cùng D trong Issue. Chat dùng để báo nhanh khi cần.

### 16.2 Demo và sync

- **Thứ Sáu:** demo luồng tích hợp trên `develop`, rà điều kiện ra cổng và hỏi chéo để chuẩn bị bảo vệ. D ghi kết quả ở Issue cổng hoặc milestone.
- Sync khi cần chốt quyết định, gỡ blocker hoặc đổi phạm vi. Người chủ trì ghi quyết định vào Issue và cập nhật ADR khi cần.
- Nhật ký cá nhân cập nhật trong PR theo mục 12.5.

### 16.3 Cổng kiểm tra theo mốc (không qua cổng thì không đi tiếp)

| Cổng | Thời điểm | Điều kiện xanh |
|---|---|---|
| **G1 — Nền móng** | Khi xong 3 sóng | Máy **A và D** kiểm bằng `make doctor` và chạy được theo README (C miễn riêng ở G1 theo ADR-015) · CI xanh · Swagger mở · 50 món mẫu · bộ cài chạy trên Windows sạch |
| **G2 — Lát cắt dọc** | Khi CRUD món chạy end-to-end | Login, phân quyền và CRUD món chạy end-to-end từ GUI trên máy người khác · xác nhận staff bị 403 ở thao tác dành cho admin · ≥12 endpoint có test |
| **G3 — MVP** | Khi đủ 6 yêu cầu đề bài | Đủ 6 yêu cầu đề bài · demo toàn luồng · installer từ CI cài được trên Windows sạch |
| **G4 — Deploy** | Khi backend có URL công khai | Backend có URL công khai; tag → CI tự build installer |
| **G5 — QA** | Khi test case pass ≥ 95% | Test case pass ≥ 95%; báo cáo đủ 80%; video demo có |
| **G6 — Đóng băng** | Trước hạn 3 ngày | Không merge gì trừ `hotfix`; tập bảo vệ xong |

**Điều kiện chung cho mọi cổng:** mỗi người đã cập nhật `docs/log/<vai>.md` (mục 2 + mục 6).
File còn trống = cổng chưa xanh, dù code đã chạy.

### 16.4 WIP limit

Mỗi người tối đa **2 thẻ `In progress`**. Quá → đang làm dở mọi thứ, phải chốt xong trước khi mở thẻ mới.

---

## 17. Xung đột, trễ hạn, rủi ro

### 17.1 Bất đồng kỹ thuật

1. Tranh luận **trong Issue** bằng dữ liệu (VD: "cách A nhanh hơn 40ms với 5k dòng"), không cảm tính.
2. Không thống nhất sau 15 phút → **người nhận Issue chức năng đề xuất**, hoặc **D quyết định** (điều phối dự án) và ghi vào `docs/decisions.md`.
3. Quyết định đã chốt **không mở lại** trừ khi có dữ liệu mới.

### 17.2 Trễ hạn

- Trễ ≥ 1 ngày → **chủ động báo trong Issue**, không chờ bị hỏi.
- Trễ ≥ 2 ngày → nhóm họp cắt scope: **bỏ tính năng phụ, giữ luồng chính chạy được**. Một app ít tính năng mà chạy ổn định ăn điểm cao hơn app nhiều tính năng mà vỡ.

### 17.3 Sổ rủi ro (cập nhật trong `docs/decisions.md`)

| Rủi ro | Dấu hiệu sớm | Hành động |
|---|---|---|
| Integration hell | Hết G2 vẫn chưa ghép được | Giao Issue chức năng end-to-end; demo thứ Sáu |
| Installer vỡ phút cuối | Chưa build lần nào tới G6 | Build thử ngay G1, CI build mỗi lần tag |
| Một người im lặng | Issue đang làm thiếu cập nhật 2 ngày | D nhắn riêng, chuyển assignee hoặc gặp trực tiếp trong 24h |
| Bus factor = 1 | Chỉ 1 người hiểu được một chức năng/tầng | Không khoá thư mục; mỗi PR đủ 3 câu giải thích + tập bảo vệ chéo |
| Báo cáo dồn cuối kỳ | Qua G3 chưa có chương nào | Khung 10 chương mở từ G2, điền dần theo Issue |
| Flaky test làm mất tin cậy CI | Test lúc xanh lúc đỏ | Sửa ngay, không `skip` |

### 17.4 Quy tắc "không im lặng"

Bất kỳ ai (người hoặc AI) bị chặn **> 2 giờ** phải báo. Bị chặn mà im lặng là lỗi quy trình, không phải lỗi cá nhân.

---

## 18. Phụ lục: template & lệnh thường dùng

> Các template **sống ở đúng chỗ GitHub dùng** — không chép lại ở đây để khỏi lệch nhau.

### 18.1 Template Issue

[`.github/ISSUE_TEMPLATE/task.md`](.github/ISSUE_TEMPLATE/task.md) (việc cần làm) ·
[`.github/ISSUE_TEMPLATE/bug.md`](.github/ISSUE_TEMPLATE/bug.md) (báo lỗi).
GitHub dùng mẫu từ nhánh mặc định `main` khi bấm **New issue**.

### 18.2 Template Pull Request

[`.github/pull_request_template.md`](.github/pull_request_template.md) — dùng mẫu khi mở PR. GitHub tự điền từ nhánh mặc định `main`.
Phần **"Giải thích được" 3 câu** trong đó là bắt buộc (mục 6.3, `docs/defense.md`).

### 18.3 Checklist tự kiểm & Review

Dùng checklist chung trong [mẫu PR](.github/pull_request_template.md) và hướng dẫn ở mục 5.5.

### 18.4 Template ADR

Mẫu nằm ở cuối [`docs/decisions.md`](docs/decisions.md) — chép vào đó, đánh số tiếp theo.
ADR đã `Chấp nhận` thì không mở lại trừ khi có dữ liệu mới.

### 18.5 Lệnh thường dùng

```bash
# Thiết lập lần đầu
make install     # tạo .venv + thư viện + pre-commit + .env
make up          # MySQL 8.0 trong Docker (cổng 3307)
make doctor      # kiểm tra môi trường

# Hằng ngày
make api         # backend  → http://127.0.0.1:8000/docs
make gui         # giao diện desktop
make check       # lint + test — BẮT BUỘC trước khi mở PR

# Git
git switch develop && git pull --ff-only
git switch -c feature/order-merge-table-cuong
git add api/routers/orders.py
git commit -m "feat(order): thêm endpoint gộp bàn"
git push -u origin HEAD
gh pr create --base develop --template .github/pull_request_template.md

# Đóng gói (D)
make build-installer   # PyInstaller + Inno Setup
```

> Danh sách lệnh đầy đủ: `make` (không tham số). Nguồn chân lý là `Makefile`, không phải mục này.

### 18.6 Mẫu báo blocker

[`docs/standup.md`](docs/standup.md) — mẫu nhắn khi một việc bị chặn.

## 19. Lịch sử thay đổi

| Phiên bản | Ngày | Thay đổi | Người duy trì |
|---|---|---|---|
| 1.0 | 2026-11-04 | Ban hành lần đầu | D |
| 1.1 | 2026-11-18 | Gọn Issue/PR, review chéo và theo dõi tiến độ trên GitHub (#90) | D |
| 2.0 | 2026-11-18 | Giao việc theo chức năng (bỏ khoá thư mục), bỏ bắt buộc approve trên GitHub & tài liệu, 100% qua Issue & PR (ADR-014, #90) | D |

---

> **Ghi nhớ cuối cùng:** quy trình này tồn tại để nhóm **không mất điểm vì những lỗi không liên quan tới trình độ** — merge nhầm, mất code, installer vỡ, báo cáo thiếu ảnh, một người làm hết. Hãy giữ nó nhẹ và thực dụng: nếu một quy định không giúp gì trong 2 tuần, hãy đề xuất bỏ nó bằng một PR.
