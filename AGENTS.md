# AGENTS.md — Điểm vào cho AI Agent

> Repo: **CafeTLU** — Ứng dụng Desktop quản lý quán café TLU (BTL Python 2026, Đề tài 5).
> Stack: PySide6 GUI → FastAPI backend → MySQL 8. Docker + PyInstaller/Inno Setup.

**Bạn là AI agent làm việc trong repo này. Đọc hết file này trước khi làm bất cứ điều gì.**

---

## 1. Thứ tự đọc bắt buộc

| # | File | Vì sao |
|---|---|---|
| 1 | `WORKFLOW.md` | **Toàn bộ quy chuẩn.** Mục 15 là quy tắc dành riêng cho bạn |
| 2 | `docs/decisions.md` | Các quyết định kỹ thuật đã chốt (không mở lại) |
| 3 | `docs/api-contract.md` | Hợp đồng API — nguồn chân lý, không tự đổi |
| 4 | `docs/erd.md` | Thiết kế dữ liệu **do B viết** — có thể còn là khung nếu B chưa chốt |
| 5 | Issue được giao | Phạm vi duy nhất bạn được làm |
| 6 | `docs/log/<vai>.md` | Nhật ký của người bạn đang làm việc cùng — **phải cập nhật cuối phiên** |

Nếu thiếu file nào ở trên → **báo lại**, đừng tự tạo phiên bản riêng.

## 1.5. Kỹ năng (skill) — đọc theo các tầng Issue chạm tới

Mỗi skill là một file hướng dẫn chi tiết cho một loại việc. **Đọc tất cả skill tương ứng với các tầng chức năng trong Issue trước khi viết code**, không phải sau. Đường dẫn: `.claude/skills/<tên>/SKILL.md`.

| Sắp làm gì | Đọc skill |
|---|---|
| **Không biết làm gì / mở phiên mới** | `next-task` |
| **Bất kỳ việc code nào (đọc trước tiên)** | `minimal-change` |
| Thêm/sửa endpoint API | `fastapi-endpoint` |
| Thêm/sửa bảng, cột, migration, seed | `sqlalchemy-model` |
| Làm màn hình, form, bố cục | `pyside6-screen` **+** `ui-design` |
| Chỉnh màu, font, khoảng cách, "cho đẹp" | `ui-design` |
| Viết test, sửa bug phải kèm test | `pytest-db` |
| Build bộ cài, lỗi đóng gói | `win-installer` |
| Xuất Excel/PDF, in hoá đơn, báo cáo | `report-export` |
| Login, phân quyền, secret, trước deploy | `security` |

**Skill không thay thế `WORKFLOW.md`.** Khi mâu thuẫn: `WORKFLOW.md` thắng.
Nếu một skill sai hoặc thiếu, sửa skill đó bằng PR — đừng lách qua một bên.

---

## 2. Mười một điều không được vi phạm

1. **Không push** lên `main` / `develop` (repo chặn cả admin). Mọi chức năng và sửa lỗi phải đi qua **Issue → Nhánh → Pull Request**.
2. **Không sửa migration đã merge**; chỉ mở rộng `db/schema.sql` hoặc `docs/api-contract.md` khi thuộc yêu cầu của Issue và phải cập nhật đồng bộ migration Alembic mới, `docs/erd.md`, `db/verify_seed.sql` / `docs/api-contract.md`.
3. **Không thêm dependency** vào `requirements.txt` khi chưa được duyệt.
4. **Không commit** `.env`, secret, token, `dist/`, `build/`, `.venv/`, `*.db`.
5. **Không `git add .`** — chỉ add path cụ thể, review `git status` trước khi commit.
6. **Không sửa test cho pass.** Test đỏ = sửa code (hoặc chứng minh test sai).
7. **Không `print()`** trong code sản phẩm — dùng `logger`.
8. **Không nói "đã test"** khi chưa thực sự chạy `make lint && make test` và dán kết quả.
9. **Không làm ngoài phạm vi Issue** (không refactor tiện tay, không đổi format toàn file).
10. **Không merge PR khi CI chưa xanh hoặc chưa có lệnh của người dùng** (quy trình nhóm đã bỏ bắt buộc approve — thành viên tự Squash & merge khi CI xanh + đủ minh chứng).
11. **Không kết thúc phiên mà không ghi** `docs/log/<vai>.md` của đúng thành viên bạn đang hỗ trợ (việc đã làm + AI đã làm gì + chỗ người dùng còn chưa giải thích được).

---

## 3. Quy trình mỗi phiên (không bỏ bước)

```bash
git switch develop && git pull --ff-only
git switch -c feature/<scope>-<slug>-<ten>
make lint && make test          # BASELINE — ghi lại kết quả TRƯỚC khi sửa
# ... sửa code trọn gói các tầng thuộc phạm vi Issue ...
make lint && make test          # KIỂM CHỨNG — phải xanh
# ghi 1–3 dòng vào docs/log/<vai>.md (mục 2 + 3) — trước khi commit
git add <path-cụ-thể>
git commit -m "feat(order): thêm endpoint gộp bàn"
git push -u origin HEAD
gh pr create --base develop --template .github/pull_request_template.md
```

Ghi `Refs #<issue>` và gắn nhãn theo các tầng chạm tới trong PR. Sau khi CI xanh và người dùng xác nhận (hoặc tự thao tác), **Squash & merge** vào `develop`, kiểm chứng kết quả trên `develop` rồi đóng Issue.

Nếu **baseline đã đỏ** từ trước: báo ngay, không tự sửa ngoài phạm vi để dọn.

---

## 4. Giao việc theo chức năng & phạm vi sửa file (ADR-014)

- Không khoá cứng thư mục theo vai `A/B/C/D`. Khi được gán Issue chức năng, được sửa trọn gói `db/` + `api/` + `gui/` + `shared/` + `tests/` + `docs/` thuộc phạm vi chức năng đó.
- Nhãn trên Issue (`api`, `gui`, `db`, `report`, `infra`, `docs`) cho biết **các tầng kỹ thuật cần chạm và các skill phải đọc**, không giới hạn người làm.
- Vẫn giữ phân tách thay đổi dùng chung: sửa `db/schema.sql`, `docs/api-contract.md`, `requirements.txt`, `.github/workflows/`, `installer/` phải nêu rõ trong Issue/PR và cập nhật đồng bộ tài liệu.
- Nếu cần chỉnh phần nằm **ngoài phạm vi Issue** được giao → **hỏi người dùng trước**.

---

## 5. Kiến trúc bất biến

```
gui/  ──HTTP──►  api/routers  ──►  api/services  ──►  api/models  ──►  MySQL
```

- `gui/` **không** import `api.models`, **không** kết nối DB. Mọi I/O qua `gui/api_client.py`.
- `api/routers/` chỉ validate + gọi service. **Không** SQL, **không** business logic.
- Chiều phụ thuộc một chiều. Không circular import.
- Response JSON theo đúng format trong `WORKFLOW.md` mục 9.3 (`data`/`meta`/`error.code`).

---

## 6. Lệnh phải biết

```bash
make up          # docker compose up -d mysql  (cổng 3307)
make start       # MySQL + API + GUI; đóng GUI hoặc Ctrl+C sẽ dừng API
make api         # uvicorn api.main:app --reload   → http://127.0.0.1:8000/docs
make gui         # python -m gui.main
make lint        # ruff check . && black --check .
make test        # pytest -q  (chưa có test thì coi là đạt)
make check       # lint + test — chạy trước khi mở PR
make build-installer   # PyInstaller + Inno Setup (chỉ D, bật ở G4)
make reset-db    # xoá sạch DB local rồi bật lại (nguy hiểm)
make doctor      # kiểm tra môi trường máy
```

---

## 7. Định nghĩa "xong" (trước khi báo hoàn thành)

- [ ] `make lint` clean, `make test` xanh — **kết quả thật được dán**
- [ ] Đúng phạm vi Issue, không file thừa trong diff
- [ ] Có test cho hành vi mới (hoặc lý do chính đáng không có)
- [ ] Đã cập nhật `docs/api-contract.md` / `CHANGELOG.md` nếu đổi hành vi
- [ ] Ảnh chụp màn hình **chỉ khi** PR hoàn thiện/đổi màn hình (UI) → `docs/screenshots/<module>/`;
      PR backend/DB/CI/docs thay bằng log + link lần chạy CI
- [ ] **Trả lời được** 3 câu trong mục "Giải thích được" của PR (`docs/defense.md`) — nếu bạn
      không viết được 3 câu đó thay cho người dùng, thì code chưa đủ rõ để họ bảo vệ
- [ ] Commit message đúng Conventional Commits, có `Co-authored-by` nếu code do AI sinh
- [ ] Đã ghi `docs/log/<vai>.md`: 1 dòng việc + 1 dòng AI, và mục 5 nếu còn chỗ chưa hiểu
- [ ] Trạng thái và blocker nằm trên GitHub Issue. Sau khi CI xanh và **Squash & merge** vào `develop` (không cần approve), xác nhận nghiệm thu rồi đóng Issue.

---

## 8. Định dạng báo cáo bắt buộc khi kết thúc phiên

```markdown
## Tóm tắt
<1–3 câu>

## Đã thay đổi
| File | Thay đổi | Lý do |

## Cách kiểm chứng
| Lệnh | Kết quả |

## Chưa làm / còn lại / rủi ro
- ...

## Câu hỏi cần người quyết
- ...
```

Không có báo cáo này = phiên làm việc chưa kết thúc hợp lệ.

---

## 9. Khi không chắc chắn

| Tình huống | Hành vi |
|---|---|
| Thiếu thông tin nghiệp vụ | Dừng, hỏi 1–3 câu cụ thể, kèm phương án đề xuất |
| Nhiều cách hợp lý | Chọn cách đơn giản nhất đáp ứng Issue, ghi rõ đã cân nhắc gì khác |
| Cần đổi schema / contract / dependency | **Không tự làm** — đề xuất, chờ duyệt |
| Bị chặn > 2 giờ | Báo ngay, không im lặng |

---

## 10. Chống đạo văn (điều kiện bắt buộc của môn học)

Đề bài quy định **copy = 0 điểm**. Vì vậy:

- Code bạn sinh ra phải **giải thích được** cho một thành viên hiểu (2–4 dòng trong PR: làm gì, vì sao chọn cách đó).
- Không tạo ra "hộp đen" mà thành viên không thể bảo vệ trước giảng viên.
- Không bịa số liệu, không bịa kết quả test, không viết báo cáo thay khi không có dữ liệu thật của nhóm.

**Bị chặn:**
- Tự quyết định thay đổi kiến trúc hoặc phạm vi đề tài.
- Đưa code từ nguồn không rõ giấy phép vào repo.
