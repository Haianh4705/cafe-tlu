# WORKFLOW — Quy chuẩn làm việc của dự án

> **Dự án:** Ứng dụng Desktop quản lý quán café TLU (BTL học phần Python 2026 — Đề tài 5)
> **Phiên bản:** 1.0 · **Ngày ban hành:** 2026-11-04 · **Người duy trì:** D (Infra/QA/Docs)
> **Đối tượng áp dụng:** toàn bộ 4 thành viên **và mọi AI agent** làm việc trong repo này.

> ⚠️ **File này là nguồn chân lý duy nhất (single source of truth) về cách làm việc.**
> Khi có mâu thuẫn giữa thói quen cá nhân / hướng dẫn trên mạng / câu trả lời của AI với file này → **file này thắng**.
> Muốn đổi quy định → mở PR sửa file này, cần **≥ 2 người approve** (trong đó có D).

---

## Mục lục

0. [TL;DR — đọc trong 5 phút](#0-tldr--đọc-trong-5-phút)
1. [Mục đích & phạm vi](#1-mục-đích--phạm-vi)
2. [Từ khoá quy ước & thứ tự ưu tiên](#2-từ-khoá-quy-ước--thứ-tự-ưu-tiên)
3. [Vai trò & quyền quyết định](#3-vai-trò--quyền-quyết-định)
4. [Kiến trúc & ranh giới sở hữu](#4-kiến-trúc--ranh-giới-sở-hữu)
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

Nếu bạn chỉ đọc 12 dòng này, hãy nhớ:

1. **Không ai push trực tiếp** lên `main` và `develop`. Mọi thay đổi đi qua **Pull Request**.
2. **Một việc = một Issue = một nhánh = một PR.** PR nhỏ dưới **400 dòng**.
3. **Bắt buộc 1 người review** (không tự merge PR của mình) + **CI xanh** mới được merge.
4. **Commit theo Conventional Commits**: `feat(order): thêm gộp bàn`.
5. **Không commit** `.env`, `dist/`, `build/`, `.venv/`, file DB, ảnh nặng.
6. **Không hardcode** mật khẩu / connection string / đường dẫn tuyệt đối của máy mình.
7. **Đổi schema DB hoặc API contract → phải bàn trước**, không tự ý đổi.
8. **Thêm thư viện mới → phải xin phép** (1 dòng trong Issue là đủ, nhưng phải có).
9. **Code xong là phải có test**; không sửa test cho pass thay vì sửa code.
10. **Xong việc = cập nhật docs + chụp ảnh màn hình** ngay lúc đó, không để tuần cuối.
11. **AI agent cũng là thành viên**: đọc file này trước, tuân thủ mục 15, báo cáo theo mẫu 15.4.
12. Khi không chắc → **dừng lại và hỏi trong Issue**, đừng đoán.

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
| `docs/api-contract.md` | Đặc tả API (nguồn chân lý của hợp đồng) | A, B, C |
| `docs/erd.md` | Sơ đồ ERD + từ điển dữ liệu | A, B |
| `CHANGELOG.md` | Lịch sử thay đổi theo phiên bản | D, GV |
| `db/schema.sql`, `db/seed.sql` | Cấu trúc DB + dữ liệu mẫu | B, tất cả khi setup |

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

## 3. Vai trò & quyền quyết định

### 3.1 Bốn vai trò

| Mã | Vai trò | Sở hữu chính | Quyền approve |
|---|---|---|---|
| **A** | Backend/API Lead | `api/` (routers, services, auth, RBAC) | PR vào `api/` |
| **B** | Data & Reports | `db/`, `api/services/reports.py`, `reports/` | PR vào `db/`, migration, query thống kê |
| **C** | GUI/UX Lead | `gui/`, `assets/`, theme | PR vào `gui/` |
| **D** | Infra + QA + Docs | `infra/`, `installer/`, `.github/`, `docs/`, `report/` | PR vào `infra/`, `docs/`; **điều phối tiến độ** |

### 3.2 Quy tắc approve

- Mỗi PR **PHẢI** có **1 approval** từ **owner của vùng bị sửa**.
- PR chạm **≥ 2 vùng** → cần **2 approval** (mỗi owner một phiếu).
- PR sửa `WORKFLOW.md`, `docs/api-contract.md`, `db/schema.sql` (thay đổi breaking) → cần **2 approval trong đó có D** và **được nêu trong buổi sync gần nhất**.
- **KHÔNG ĐƯỢC** tự approve/merge PR của chính mình (kể cả khi là owner).
- Trường hợp khẩn cấp (buổi demo sắp bắt đầu, lỗi chặn toàn bộ): được merge với 1 approval + ghi rõ `[HOTFIX]` trong PR, và **phải bổ sung test + review sau trong 24h**.

### 3.3 Kênh liên lạc chính thức

| Kênh | Dùng cho |
|---|---|
| GitHub Issue | Việc cần làm, báo lỗi, câu hỏi kỹ thuật (**nguồn chân lý**) |
| GitHub PR | Thảo luận code, review |
| `docs/decisions.md` | Quyết định kiến trúc đã chốt |
| Zalo/Discord nhóm | Trao đổi nhanh, standup async |
| `docs/standup.md` (tuỳ chọn) | Lưu standup nếu nhóm muốn tra cứu lại |

> Quy ước: **quyết định kỹ thuật chốt trên chat miệng = không tồn tại.** Phải được dán lại vào Issue/ADR.

---

## 4. Kiến trúc & ranh giới sở hữu

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
        D: Docker compose, CI/CD, PyInstaller/Inno Setup, deploy
```

**Quy tắc kiến trúc (BẮT BUỘC):**

- GUI **KHÔNG ĐƯỢC** kết nối MySQL trực tiếp. Mọi truy cập dữ liệu đi qua `gui/api_client.py` → REST API.
- Router **KHÔNG ĐƯỢC** chứa business logic hay câu SQL. Router → Service → Model.
- Service **KHÔNG ĐƯỢC** import từ `gui/`. Chiều phụ thuộc một chiều: `gui → api → db`.
- Không import vòng (circular import). Nếu cần → tách interface.

### 4.2 Cấu trúc thư mục

```
cafe-tlu/
├── api/                    # A sở hữu
│   ├── main.py             # tạo FastAPI app, mount router
│   ├── core/               # config, security, deps (get_db, get_current_user)
│   ├── routers/            # mỏng: chỉ validate + gọi service
│   ├── services/           # business logic
│   │   └── reports.py      # B sở hữu
│   ├── models/             # SQLAlchemy models (B review mọi thay đổi)
│   └── schemas/            # Pydantic
├── db/                     # B sở hữu
│   ├── schema.sql          # DDL chuẩn (nguồn chân lý)
│   ├── seed.sql            # dữ liệu mẫu 50+ món
│   └── migrations/         # Alembic
├── gui/                    # C sở hữu
│   ├── main.py
│   ├── api_client.py       # lớp duy nhất gọi HTTP
│   ├── views/              # mỗi màn hình 1 file
│   ├── widgets/            # component tái sử dụng
│   ├── theme.py            # màu, font, spacing — không hardcode trong view
│   └── i18n.py             # chuỗi tiếng Việt tập trung
├── shared/                 # dùng chung: constants, enums, error codes
├── scripts/                # smoke_test.py, backup.py, build_installer.py
├── tests/                  # pytest
├── infra/                  # D: docker-compose, Dockerfile, nginx, deploy.md
├── installer/              # D: Inno Setup .iss, icon, license
├── assets/                 # icon, ảnh món, logo
├── docs/                   # D biên tập: decisions, api-contract, erd, screenshots
├── report/                 # báo cáo BTL (chia chương theo người)
├── .github/workflows/      # CI/CD
├── .env.example            # BẮT BUỘC có, commit
├── Makefile                # make up / api / gui / test / lint / build
├── requirements.txt
├── CHANGELOG.md
└── README.md
```

### 4.3 Ranh giới sửa file

| Được sửa tự do (trong nhánh của mình) | **PHẢI** báo trước | **CẤM** tự ý |
|---|---|---|
| File trong vùng mình sở hữu | File của người khác (≤ 10 dòng, sửa lỗi nhỏ) | `main`, `develop` (push trực tiếp) |
| Test của tính năng mình | `db/schema.sql`, `docs/api-contract.md` | Migration **đã merge** |
| Docs chương báo cáo của mình | `requirements.txt` (thêm thư viện) | `.github/workflows/`, `installer/` (nếu không phải D) |
| `shared/` (báo trong PR) | `WORKFLOW.md`, `Makefile` | Bất kỳ file `.env` thật |

---

## 5. Vòng đời một việc (quy trình chuẩn)

```
Issue (Ready) → Branch → Code + Test → Commit → Push → PR → CI xanh
   → Review 1–2 approval → Squash merge vào develop → Issue Done
   → (theo lịch) release/vX.Y → merge main + tag → build installer tự động
```

### 5.1 Issue

- **Mọi việc đều phải có Issue.** Việc < 30 phút vẫn tạo Issue (để có bằng chứng đóng góp) nhưng dùng label `quick`.
- Tiêu đề Issue: động từ + đối tượng. VD: `Thêm chức năng gộp bàn khi thanh toán`.
- Issue **PHẢI** đạt [Definition of Ready](#6-definition-of-ready--definition-of-done) trước khi vào cột `Ready`.
- Gán: **đúng 1 assignee**, 1 `estimate` (S/M/L), 1 `milestone` (tuần), label theo vùng (`api`/`gui`/`db`/`infra`/`docs`/`bug`/`blocked`).

### 5.2 Nhánh

Đặt tên: `<loại>/<scope>-<mô-tả-ngắn>-<viết-tắt-tên>`

| Loại | Dùng khi | Ví dụ |
|---|---|---|
| `feature/` | Tính năng mới | `feature/order-merge-table-cuong` |
| `fix/` | Sửa lỗi | `fix/auth-token-expired-an` |
| `docs/` | Chỉ tài liệu | `docs/report-chapter3-dung` |
| `chore/` | Cấu hình, dependency | `chore/add-pytest-qt` |
| `hotfix/` | Sửa gấp từ `main` | `hotfix/installer-missing-dll` |

**BẮT BUỘC:**

- Luôn tạo nhánh từ `develop` **mới nhất**: `git switch develop && git pull && git switch -c feature/...`
- **Tuổi thọ nhánh ≤ 3 ngày.** Quá 3 ngày → tách nhỏ hoặc rebase `develop` ngay.
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

- Tiêu đề PR = tiêu đề Issue. Body **PHẢI** theo template ở [mục 18.2](#182-template-pull-request).
- **PHẢI** có: mô tả thay đổi, **cách kiểm chứng** (lệnh đã chạy + kết quả), **ảnh chụp** nếu là UI, `Closes #<issue>`.
- PR nhỏ: **< 400 dòng diff** (không tính file sinh tự động). Lớn hơn → tách.
- Gắn label + reviewer (owner vùng bị sửa). **Tự assign chính mình**, không để "ai đó" làm giúp.
- Không mở PR khi còn `TODO` hoặc code chết, trừ khi ghi rõ `[Draft]`.

### 5.5 Review

Reviewer **PHẢI** kiểm tra (checklist 18.3):

- [ ] Đúng phạm vi Issue, không "tiện tay" sửa thứ khác
- [ ] Tuân thủ ranh giới kiến trúc mục 4 (GUI không gọi SQL, router không chứa logic)
- [ ] Có test; test thực sự kiểm tra hành vi, không phải test cho có
- [ ] Không có secret, không có `print()`, không có code comment-out
- [ ] Xử lý lỗi & trường hợp biên (dữ liệu rỗng, trùng, số âm, mất kết nối)
- [ ] Ảnh chụp/docs cập nhật
- [ ] Đặt tên & style đúng mục 7

**Thời hạn review: 24 giờ.** Reviewer bận → nhắn trong PR và chuyển reviewer khác, không im lặng.

Phân loại comment (bắt buộc dùng tiền tố):

| Tiền tố | Ý nghĩa | Người viết code |
|---|---|---|
| `[must]` | Bắt buộc sửa mới merge | Phải sửa |
| `[should]` | Nên sửa | Sửa hoặc giải thích lý do |
| `[nit]` | Nhỏ, không chặn | Tuỳ |
| `[question]` | Cần làm rõ | Trả lời |
| `[praise]` | Khen (khuyến khích dùng) | – |

### 5.6 Merge & phát hành

- Merge vào `develop` bằng **Squash and merge** (giữ lịch sử sạch, 1 commit = 1 việc).
- Xoá nhánh sau merge.
- `develop` **PHẢI** luôn chạy được: hết mỗi ngày, CI xanh.
- Phát hành: `develop → release/vX.Y` → test → CI build installer → `main` + tag `vX.Y.Z` + GitHub Release.

---

## 6. Definition of Ready / Definition of Done

### 6.1 Definition of Ready (Issue sẵn sàng để làm)

- [ ] Mô tả rõ **kết quả mong đợi**, không chỉ "làm trang X"
- [ ] Có **tiêu chí nghiệm thu** kiểm tra được (VD: "thêm món trùng tên → báo lỗi, không tạo bản ghi")
- [ ] Biết rõ **phụ thuộc** (API nào, bảng nào, ai cung cấp)
- [ ] Có **assignee** và ước lượng S/M/L
- [ ] Nếu ảnh hưởng schema/API → **đã chốt trong `docs/api-contract.md` / `docs/erd.md`**
- [ ] Nếu cần thư viện mới → **đã được duyệt**

### 6.2 Definition of Done (việc thực sự xong)

Chỉ được kéo sang `Done` khi **tất cả** đúng:

- [ ] Chạy được trên `develop` (không phải "chạy trên máy tôi")
- [ ] Có test (unit cho logic; smoke/manual script cho UI) — hoặc ghi rõ lý do không test
- [ ] `make lint && make test` xanh ở local và trên CI
- [ ] Đã review + approve, đã merge
- [ ] Không `print()` debug, không code chết, không `TODO` treo
- [ ] Đã cập nhật `docs/api-contract.md` / `docs/erd.md` nếu có đổi
- [ ] Đã cập nhật `CHANGELOG.md` (mục `Unreleased`)
- [ ] **Có ảnh chụp màn hình** lưu vào `docs/screenshots/<module>/` (nếu là UI)
- [ ] Đã ghi vào `docs/decisions.md` nếu có quyết định kỹ thuật mới

> 💡 Ảnh chụp lưu **ngay khi xong việc** là mẹo ăn điểm mốc 8 ("chụp ảnh các bước đầy đủ, cẩn thận") — đến tuần 7 không phải dựng lại app để chụp.

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

- `docs/api-contract.md` được chốt **trước khi code**. A viết, B và C review.
- Đổi contract (thêm/xoá/đổi field, đổi mã lỗi) → **PR riêng** vào `docs/api-contract.md` + thông báo nhóm; **không** sửa lén trong PR tính năng.
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

| Tầng | Công cụ | Phạm vi | Ai viết |
|---|---|---|---|
| Unit | `pytest` | Service, tính toán tiền, validate, phân quyền | Người viết code |
| API | `pytest` + `TestClient` | Endpoint: đúng mã HTTP, đúng schema, đúng quyền | A (+ B cho reports) |
| DB | `pytest` + DB test riêng | Query thống kê trả đúng số | B |
| Smoke | `scripts/smoke_test.py` | Luồng chính: login → order → thanh toán → xem báo cáo | D |
| UI thủ công | Checklist trong `docs/test-cases.md` | Từng màn hình | C + D |

### 11.2 Quy tắc

- Mọi **bug fix PHẢI** kèm test tái hiện bug (test đỏ trước, xanh sau).
- **CẤM** sửa/xoá test để CI xanh, trừ khi test đó sai — và phải nói rõ lý do trong PR.
- Test **PHẢI** độc lập, không phụ thuộc thứ tự chạy, không gọi mạng thật (dùng mock/fixture).
- Dùng DB test riêng (`cafe_tlu_test`), **CẤM** test trên DB dev.
- Coverage mục tiêu: `api/services` ≥ **60%** (không đặt nặng con số, đặt nặng hành vi quan trọng).
- Mọi test **PHẢI** chạy được bằng **một lệnh**: `make test`.
- Kết quả test của lần chạy cuối phải được dán vào PR (số pass/fail), không nói "em test rồi".

### 11.3 Bug report (Issue label `bug`)

**PHẢI** có: môi trường (OS, phiên bản app), bước tái hiện (1-2-3), kết quả mong đợi, kết quả thực tế, ảnh chụp/video, log liên quan. Thiếu bước tái hiện → không xử lý.

---

## 12. Quy chuẩn tài liệu & minh chứng

### 12.1 Nguyên tắc "tài liệu đi cùng code"

- Mỗi PR đổi hành vi **PHẢI** cập nhật tài liệu liên quan **trong cùng PR** (không tách PR sau).
- **CẤM** để tài liệu lỗi thời: nếu code khác docs, docs là sai và phải sửa ngay.

### 12.2 Ai viết gì

| Tài liệu | Người viết | Ghi chú |
|---|---|---|
| `docs/api-contract.md` | A | Cập nhật mỗi khi đổi endpoint |
| `docs/erd.md` | B | Kèm hình ERD (draw.io/dbdiagram) |
| `README.md` | D biên tập | Cài & chạy trong 3 lệnh |
| `CHANGELOG.md` | D biên tập | Mọi người thêm mục `Unreleased` khi merge |
| `docs/decisions.md` | Người ra quyết định | ADR-lite, xem 18.4 |
| `docs/test-cases.md` | D + C | Bảng test case |
| Báo cáo BTL | Mỗi người 1 chương | D biên tập, thống nhất format |
| Video demo | D | 3–5 phút, có tiếng Việt |

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

---

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
| Đọc mọi file trong repo | Đổi `db/schema.sql`, ERD, migration đã merge | Push trực tiếp `main`/`develop` |
| Tạo nhánh `feature/*`, `fix/*` | Đổi API contract (nhất là breaking) | `git push --force` lên nhánh chung |
| Sửa file trong vùng được giao | Thêm/đổi dependency trong `requirements.txt` | Commit `.env`, secret, token, key |
| Thêm/sửa test | Đổi cấu trúc thư mục, tên module | `DROP`/`TRUNCATE`/`DELETE` không `WHERE` |
| Chạy `make lint`, `make test`, `make api`, `make up` | Đổi `.github/workflows/`, `installer/` | Sửa test để pass thay vì sửa code |
| Tạo migration **mới** | Bump version / tạo tag / tạo Release | Xoá file không liên quan tới Issue |
| Cập nhật docs cùng PR | Sửa code của người khác > 10 dòng | `git add .` / `git commit -am` |
| Chạy script smoke test | Bật/tắt cờ tính năng | Đưa `print()` debug vào code sản phẩm |
| Đề xuất cải tiến (dạng ghi chú) | Đổi `WORKFLOW.md` | Tự merge / tự approve PR của mình |
| | | Bịa kết quả test / bịa log |

### 15.3 Quy trình bắt buộc mỗi phiên làm việc

```
1. ĐỌC      : AGENTS.md, WORKFLOW.md, docs/decisions.md, docs/api-contract.md, Issue
2. ĐỒNG BỘ  : git switch develop && git pull --ff-only
3. NHÁNH    : git switch -c feature/<scope>-<slug>-<ten>
4. BASELINE : make lint && make test        # ghi lại trạng thái TRƯỚC khi sửa
5. LÀM      : thay đổi nhỏ nhất đủ đáp ứng Issue, từng bước có thể chạy được
6. KIỂM CHỨNG: make lint && make test  (+ chạy tay luồng chính nếu là GUI/API)
7. TÀI LIỆU : cập nhật docs liên quan + CHANGELOG + ảnh chụp nếu là UI
8. COMMIT   : conventional commit, nhỏ, đúng scope
9. PR       : theo template, gắn Closes #<issue>, gán reviewer là owner vùng
10. BÁO CÁO : theo mẫu 15.4 (dán vào PR hoặc chat cho người giao việc)
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

---

## 16. Nhịp làm việc & giao tiếp

### 16.1 Hằng ngày

- **Standup async** (Zalo/Discord, trước 10:00, 3 dòng):
  ```
  Hôm qua: ...
  Hôm nay: ...
  Đang chặn: ... (hoặc "không")
  ```
- **CẬP NHẬT BOARD** ngay khi đổi trạng thái, không để cuối ngày.

### 16.2 Hằng tuần

| Thời điểm | Hoạt động | Kết quả bắt buộc |
|---|---|---|
| Thứ 3 | Sync 20–30 phút | Gỡ blocker, chốt việc tuần |
| Thứ 6 | **Demo nội bộ 30 phút** | Mỗi người demo phần mình **chạy thật** trên `develop` |
| Thứ 6 | **Cổng tích hợp** | `develop` phải chạy được end-to-end; nếu không → cắt bớt scope tuần sau |
| Chủ nhật | D tổng hợp tiến độ | 1 báo cáo ngắn 5 dòng gửi nhóm (+ GV nếu cần) |

> **Demo là bắt buộc, không thay bằng slide hay "em sắp xong".** Không demo được = việc đó coi như chưa xong.

### 16.3 Cổng kiểm tra theo mốc (không qua cổng thì không đi tiếp)

| Cổng | Thời điểm | Điều kiện xanh |
|---|---|---|
| **G1 — Nền móng** | Cuối tuần 1 | Cả 4 máy chạy `make up && make api && make gui` chỉ bằng README; CI xanh; **build installer thử lần 1** |
| **G2 — Lát cắt dọc** | Cuối tuần 2 | Login + phân quyền + CRUD món chạy end-to-end từ GUI |
| **G3 — MVP** | Cuối tuần 4 | Đủ 6 yêu cầu đề bài; installer từ CI cài được trên máy sạch |
| **G4 — Deploy** | Cuối tuần 6 | Backend có URL công khai; tag → CI tự build installer |
| **G5 — QA** | Cuối tuần 7 | Test case pass ≥ 95%; báo cáo đủ 80%; video demo có |
| **G6 — Đóng băng** | Trước hạn 3 ngày | Không merge gì trừ `hotfix`; tập bảo vệ xong |

### 16.4 WIP limit

Mỗi người tối đa **2 thẻ `In progress`**. Quá → đang làm dở mọi thứ, phải chốt xong trước khi mở thẻ mới.

---

## 17. Xung đột, trễ hạn, rủi ro

### 17.1 Bất đồng kỹ thuật

1. Tranh luận **trong Issue** bằng dữ liệu (VD: "cách A nhanh hơn 40ms với 5k dòng"), không cảm tính.
2. Không thống nhất sau 15 phút → **owner vùng quyết định** và ghi vào `docs/decisions.md`.
3. Vẫn bất đồng → **D quyết định** (điều phối dự án). Quyết định đã chốt **không mở lại** trừ khi có dữ liệu mới.

### 17.2 Trễ hạn

- Trễ ≥ 1 ngày → **chủ động báo trong standup**, không chờ bị hỏi.
- Trễ ≥ 2 ngày → nhóm họp cắt scope: **bỏ tính năng phụ, giữ luồng chính chạy được**. Một app ít tính năng mà chạy ổn định ăn điểm cao hơn app nhiều tính năng mà vỡ.

### 17.3 Sổ rủi ro (cập nhật trong `docs/decisions.md`)

| Rủi ro | Dấu hiệu sớm | Hành động |
|---|---|---|
| Integration hell | Cuối tuần 6 vẫn chưa ghép | Cổng G2/G3; demo thứ 6 |
| Installer vỡ phút cuối | Chưa build lần nào tới tuần 8 | Build thử từ tuần 1, CI build mỗi tuần |
| Một người im lặng | Không commit/không standup 2 ngày | D nhắn riêng, gặp trực tiếp trong 24h |
| Bus factor = 1 | Chỉ 1 người biết deploy/GUI | Mỗi module có owner + reviewer; tập bảo vệ chéo |
| Báo cáo dồn cuối kỳ | Tuần 5 chưa có chương nào | Mỗi người viết chương từ tuần 4 |
| Flaky test làm mất tin cậy CI | Test lúc xanh lúc đỏ | Sửa ngay, không `skip` |

### 17.4 Quy tắc "không im lặng"

Bất kỳ ai (người hoặc AI) bị chặn **> 2 giờ** phải báo. Bị chặn mà im lặng là lỗi quy trình, không phải lỗi cá nhân.

---

## 18. Phụ lục: template & lệnh thường dùng

### 18.1 Template Issue

```markdown
## Mục tiêu
<kết quả mong đợi, 1–2 câu>

## Tiêu chí nghiệm thu
- [ ] ...
- [ ] ...

## Phạm vi
- Vùng ảnh hưởng: api / gui / db / infra / docs
- File dự kiến sửa: ...

## Phụ thuộc
- Cần: <endpoint/bảng/người>

## Ước lượng
S / M / L
```

### 18.2 Template Pull Request

```markdown
## Liên kết
Closes #<issue>

## Đã làm gì
...

## Cách kiểm chứng
| Lệnh / bước | Kết quả |
|---|---|
| `make test` | 48 passed |
| `make lint` | clean |
| Thủ công | ... |

## Ảnh chụp
<img ...> (nếu là UI)

## Ghi chú cho reviewer
- ...

## Checklist
- [ ] Đúng phạm vi Issue
- [ ] Tuân thủ kiến trúc mục 4
- [ ] Có test
- [ ] Đã cập nhật docs + CHANGELOG
- [ ] Không có secret / print / code chết
```

### 18.3 Checklist reviewer

- [ ] Logic đúng theo tiêu chí nghiệm thu
- [ ] Ranh giới kiến trúc (GUI không SQL, router không logic)
- [ ] Trường hợp biên: rỗng, trùng, số âm, quá dài, mất mạng
- [ ] Phân quyền được kiểm ở server
- [ ] Test có ý nghĩa, không phải test hình thức
- [ ] Tên biến/hàm rõ nghĩa, không viết tắt khó hiểu
- [ ] Không N+1 query; có index cho cột lọc mới
- [ ] Thông báo lỗi thân thiện với người dùng cuối
- [ ] Docs/ảnh chụp đã cập nhật

### 18.4 Template ADR (thêm vào `docs/decisions.md`)

```markdown
### ADR-007: Dùng PySide6 thay vì Tkinter
- **Ngày:** 2026-11-06 · **Người quyết định:** C · **Trạng thái:** Chấp nhận
- **Bối cảnh:** cần biểu đồ, theme hiện đại, bundle installer.
- **Quyết định:** dùng PySide6 + QSS.
- **Đã cân nhắc:** Tkinter (nhẹ nhưng xấu, chart kém), Flet (mới, ít tài liệu).
- **Hệ quả:** installer nặng thêm ~60MB; cần Qt Designer cho layout.
```

### 18.5 Lệnh thường dùng

```bash
# Thiết lập lần đầu
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env

# Chạy hệ thống
make up          # docker compose up -d mysql
make api         # uvicorn api.main:app --reload
make gui         # python -m gui.main
make test        # pytest -q
make lint        # ruff check . && black --check .

# Git
git switch develop && git pull --ff-only
git switch -c feature/order-merge-table-cuong
git rebase develop
git add api/routers/orders.py
git commit -m "feat(order): thêm endpoint gộp bàn"
git push -u origin HEAD

# Build installer (D)
make installer   # PyInstaller + Inno Setup
```

### 18.6 Mẫu standup

```
Hôm qua: xong endpoint merge-table (#42), còn thiếu test
Hôm nay: viết test + cập nhật api-contract
Đang chặn: cần B xác nhận cột order_items.status có cần không
```

---

## 19. Lịch sử thay đổi

| Phiên bản | Ngày | Thay đổi | Người duy trì |
|---|---|---|---|
| 1.0 | 2026-11-04 | Ban hành lần đầu | D |

---

> **Ghi nhớ cuối cùng:** quy trình này tồn tại để nhóm **không mất điểm vì những lỗi không liên quan tới trình độ** — merge nhầm, mất code, installer vỡ, báo cáo thiếu ảnh, một người làm hết. Hãy giữ nó nhẹ và thực dụng: nếu một quy định không giúp gì trong 2 tuần, hãy đề xuất bỏ nó bằng một PR.
