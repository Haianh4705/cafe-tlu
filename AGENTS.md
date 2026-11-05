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
| 4 | `docs/erd.md` | Sơ đồ dữ liệu + từ điển cột |
| 5 | Issue được giao | Phạm vi duy nhất bạn được làm |

Nếu thiếu file nào ở trên → **báo lại**, đừng tự tạo phiên bản riêng.

## 1.5. Kỹ năng (skill) — đọc theo vùng việc

Mỗi skill là một file hướng dẫn chi tiết cho một loại việc. **Đọc skill trước khi viết code**,
không phải sau. Đường dẫn: `.claude/skills/<tên>/SKILL.md`.

| Sắp làm gì | Đọc skill |
|---|---|
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

## 2. Mười điều không được vi phạm

1. **Không push** lên `main` / `develop`. Luôn tạo nhánh `feature/*` hoặc `fix/*`.
2. **Không tự đổi** `db/schema.sql`, migration đã merge, `docs/api-contract.md` → phải hỏi.
3. **Không thêm dependency** vào `requirements.txt` khi chưa được duyệt.
4. **Không commit** `.env`, secret, token, `dist/`, `build/`, `.venv/`, `*.db`.
5. **Không `git add .`** — chỉ add path cụ thể, review `git status` trước khi commit.
6. **Không sửa test cho pass.** Test đỏ = sửa code (hoặc chứng minh test sai).
7. **Không `print()`** trong code sản phẩm — dùng `logger`.
8. **Không nói "đã test"** khi chưa thực sự chạy `make lint && make test` và dán kết quả.
9. **Không làm ngoài phạm vi Issue** (không refactor tiện tay, không đổi format toàn file).
10. **Không tự merge/approve** PR của mình.

---

## 3. Quy trình mỗi phiên (không bỏ bước)

```bash
git switch develop && git pull --ff-only
git switch -c feature/<scope>-<slug>-<ten>
make lint && make test          # BASELINE — ghi lại kết quả TRƯỚC khi sửa
# ... sửa code, thay đổi nhỏ nhất đủ đáp ứng Issue ...
make lint && make test          # KIỂM CHỨNG — phải xanh
git add <path-cụ-thể>
git commit -m "feat(order): thêm endpoint gộp bàn"
git push -u origin HEAD
```

Sau đó mở PR theo template trong `WORKFLOW.md` mục 18.2 và gán reviewer là **owner vùng bị sửa**.

Nếu **baseline đã đỏ** từ trước: báo ngay, không tự sửa ngoài phạm vi để dọn.

---

## 4. Ranh giới sở hữu

| Vùng | Owner | Được sửa khi |
|---|---|---|
| `api/` | A | Issue có label `api`/`auth`/`order` |
| `db/`, `api/services/reports.py` | B | Issue có label `db`/`report` |
| `gui/`, `assets/` | C | Issue có label `gui` |
| `infra/`, `installer/`, `.github/`, `docs/`, `report/` | D | Issue có label `infra`/`ci`/`docs` |
| `shared/` | Chung | Được sửa, nhưng phải nêu trong PR |

Chạm file ngoài vùng mình > 10 dòng → **hỏi trước**.

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
- [ ] Ảnh chụp màn hình (nếu là UI) lưu vào `docs/screenshots/<module>/`
- [ ] **Trả lời được** 3 câu trong mục "Giải thích được" của PR (`docs/defense.md`) — nếu bạn
      không viết được 3 câu đó thay cho người dùng, thì code chưa đủ rõ để họ bảo vệ
- [ ] Commit message đúng Conventional Commits, có `Co-authored-by` nếu code do AI sinh

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
