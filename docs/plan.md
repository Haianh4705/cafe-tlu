# Kế hoạch 8 tuần — làm gì, giao theo thứ tự nào

> Bổ trợ cho [`docs/workflow.md`](workflow.md) (ai bàn giao cho ai) và `WORKFLOW.md` mục 16.3
> (điều kiện cổng). File này trả lời: **tuần này làm gì, và giao việc theo thứ tự nào.**
>
> **Phân vai đã chốt:** A = [@bao20062005dh-creator](https://github.com/bao20062005dh-creator) ·
> B = [@trungdunxg](https://github.com/trungdunxg) ·
> C = [@MeoCamGuitar](https://github.com/MeoCamGuitar) ·
> D = [@Haianh4705](https://github.com/Haianh4705)

## 0. Năm quy tắc giao việc

1. **Đường găng trước.** `db/schema.sql` chặn A và C → giao cho B **ngay ngày 1**, không chờ họp.
2. **Giao theo "sóng", không giao phẳng.** Sóng 1 = việc không phụ thuộc ai (4 người chạy song song).
   Sóng 2 = việc chỉ chờ sóng 1. Không ai ngồi chờ vì giao sai thứ tự.
3. **Mỗi người tối đa 2 việc đang làm** (WIP limit). Hết việc mới nhận thêm.
4. **Giao kèm 3 thứ**: link Issue, skill cần đọc (`.claude/skills/…`), và người review.
5. **D giữ 20% thời gian** cho việc gỡ chặn, không nhận việc code kín lịch.

## 1. Toàn cảnh

| Tuần | Mục tiêu | Cổng | Đường găng |
|---|---|---|---|
| **W1** | Dữ liệu + khung 2 đầu chạy được | G1 | B: schema → A: models |
| **W2** | Lát cắt dọc: login → CRUD món | G2 | A: CRUD → C: màn hình |
| **W3** | Order tại bàn + hoá đơn | – | A: orders API → C: màn order |
| **W4** | MVP đủ 6 yêu cầu đề bài | G3 | B: thống kê → C: dashboard |
| **W5** | Đánh bóng UI + tối ưu query | – | C: UI polish |
| **W6** | Deploy backend + CI ra `.exe` | G4 | D: Docker + deploy |
| **W7** | QA hồi quy + báo cáo 80% | G5 | D: QA + biên tập |
| **W8** | Đóng băng, tập bảo vệ | G6 | cả nhóm |

---

## 2. W1 — Nền móng

**Mục tiêu:** mỗi người chạy được hệ thống trên máy mình; DB có 50 món; Swagger mở được.
**Cổng G1:** 4/4 máy `make doctor` xanh · CI xanh · **có bản cài cài được** trên Windows sạch.

### Sóng 1 — ngày 1 (không phụ thuộc ai, cả 4 chạy ngay)

| # | Việc | Ai | Issue | ~giờ |
|---|---|---|---|---|
| 1 | **Thiết kế ERD** (`docs/erd.md`) + `db/schema.sql` | B | #17 | 6 |
| 2 | Khung `api/` + `/health` | A | #19 | 2 |
| 3 | Khung `gui/` + `theme.py` (palette TLU) + `BaseView` | C | #23 | 4 |
| 4 | Build installer lần 1 trên CI | D | #26 | 3 |

### Sóng 2 — ngày 2–3 (chờ sóng 1)

| # | Việc | Ai | Issue | Phụ thuộc |
|---|---|---|---|---|
| 5 | `db/seed.sql` — 50 món, 5 users bcrypt | B | #18 | #17 |
| 6 | Config + kết nối MySQL (`get_db`) | A | #20 | #19 |
| 7 | Models theo ERD của B | A | #21 | **#17** |
| 8 | `api_client.py` + `i18n.py` | C | #24 | contract (đã có) |
| 9 | `make doctor` kiểm tra MySQL + Dockerfile | D | #27 | – |

### Sóng 3 — ngày 4–5

| # | Việc | Ai | Issue | Phụ thuộc |
|---|---|---|---|---|
| 10 | Auth JWT + `require_role` | A | #22 | #21 |
| 11 | Màn Đăng nhập (nối API thật) | C | #25 | #24, #22 |

**Cuối W1 phải có:** `make up` + `make api` ra Swagger · 50 món trong DB · cửa sổ GUI mở được ·
1 file `Setup.exe` cài được trên máy Windows · demo thứ 6 + hỏi chéo.

---

## 3. W2 — Lát cắt dọc

**Mục tiêu:** đăng nhập → xem/thêm/sửa/xoá món, chạy end-to-end từ GUI xuống DB.
**Cổng G2:** chạy trên **máy người khác** · `staff` bị 403 ở chức năng admin · ≥ 12 endpoint có test.

### Sóng 1 — ngày 1–2

| # | Việc | Ai | Issue | ~giờ |
|---|---|---|---|---|
| 1 | CRUD products + categories (5 endpoint) | A | #29 | 6 |
| 2 | Sinh 120 đơn trải 30 ngày | B | #28 | 3 |
| 3 | Khung báo cáo + phân chương (10 file) | D | #32 | 3 |

### Sóng 2 — ngày 3–4

| # | Việc | Ai | Issue | Phụ thuộc |
|---|---|---|---|---|
| 4 | Query thống kê: doanh thu, top món | B | #31 | #28 |
| 5 | Màn Danh sách món (bảng + tìm kiếm + 4 trạng thái) | C | #30 | #29, #24 |

### Sóng 3 — ngày 5

| # | Việc | Ai | Việc cụ thể |
|---|---|---|---|
| 6 | Test case `TC-AUTH`, `TC-PRD`, `TC-SRC` | D | điền PASS/FAIL + chụp ảnh |
| 7 | Fix bug do QA phát hiện | A, C | theo Issue mới |

**Cuối W2 phải có:** luồng đầy đủ chạy được · ảnh chụp màn hình mới · Swagger ≥ 12 endpoint ·
mỗi PR có "Giải thích được" 3 câu.

---

## 4. W3 — Order tại bàn

**Mục tiêu:** chọn bàn → thêm món → tính tiền → thanh toán → in hoá đơn.
**Chưa phải cổng**, nhưng là phần lớn nhất của đề bài — trễ ở đây là trễ G3.

### Sóng 1

| # | Việc | Ai |
|---|---|---|
| 1 | Models + API `orders` (tạo đơn, thêm/xoá món) | A |
| 2 | Seed bàn + trạng thái bàn; query doanh thu đã có từ W2 | B |
| 3 | Màn Order: chọn bàn, danh sách món, giỏ | C |
| 4 | Test case `TC-ORD` + smoke test luồng chính | D |

### Sóng 2

| # | Việc | Ai |
|---|---|---|
| 5 | API `checkout` (transaction, tạo `invoices`, đóng bàn) | A |
| 6 | Màn Thanh toán + xác nhận + in bill (reportlab) | C |
| 7 | Bất biến dữ liệu: `total_amount`, `invoices.total` khớp | B |
| 8 | QA: 2 người cùng bàn, huỷ đơn, thanh toán lại | D |

> **Rủi ro lớn nhất tuần này:** transaction của `checkout`. Nếu A và B không thống nhất bất biến
> đã ghi ở mục 3.3 của `docs/erd.md` (do B viết), dữ liệu sẽ lệch và báo cáo sai. Chốt trước khi code (thứ 3).

---

## 5. W4 — MVP (G3)

**Mục tiêu:** đủ **6 yêu cầu đề bài**: CRUD · Login · thống kê · tìm kiếm · bộ cài · phân quyền.
**Cổng G3:** installer cài được trên máy sạch · đủ chức năng · demo chạy full luồng.

### Sóng 1

| # | Việc | Ai |
|---|---|---|
| 1 | API báo cáo: doanh thu ngày/tháng, top món, theo danh mục | A |
| 2 | Xuất Excel (openpyxl) + PDF (reportlab, **font tiếng Việt**) | B |
| 3 | Dashboard: 4 thẻ KPI + 2 biểu đồ | C |
| 4 | Installer bản đầy đủ + test gỡ cài đặt | D |

### Sóng 2

| # | Việc | Ai |
|---|---|---|
| 5 | Tối ưu: index, phân trang, sửa N+1 | A |
| 6 | Đối chiếu số liệu: màn hình vs file xuất vs SQL tay | B |
| 7 | Màn Báo cáo + bộ lọc ngày | C |
| 8 | Chạy toàn bộ `docs/test-cases.md` | D |

**Cuối W4 = MVP.** Từ đây **không thêm tính năng mới** trừ khi đã xong hết việc tối ưu.

---

## 6. W5 — Đánh bóng

**Mục tiêu:** mốc 8 nằm ở đây — "giao diện đẹp, tối ưu, báo cáo viết tốt".

| # | Việc | Ai |
|---|---|---|
| 1 | Rà toàn bộ UI theo skill `ui-design` (spacing 8pt, 4 trạng thái, phím tắt, toast) | C |
| 2 | UI review 30 phút cả nhóm, chốt danh sách sửa | cả nhóm |
| 3 | Vá các `shortcut:` còn rẻ (grep `shortcut:`) | A, B |
| 4 | Đo hiệu năng: 5.000 món / 5.000 đơn — chỗ nào chậm | D |
| 5 | Viết chương báo cáo của mình (mỗi người 1–2 chương) | cả nhóm |

---

## 7. W6 — Deploy (G4)

**Cổng G4:** backend có URL công khai · tag → CI tự build `.exe` · `pip-audit` sạch.

| # | Việc | Ai |
|---|---|---|
| 1 | `infra/Dockerfile` + `docker-compose.prod.yml` + deploy lên VPS/Render | D |
| 2 | Config production: tắt debug, `JWT_SECRET` mới, DB user không phải root | A |
| 3 | Auto-update: kiểm tra version + tải bản mới | D |
| 4 | Review bảo mật theo skill `security` (checklist G4) | A + D |
| 5 | Backup DB định kỳ (`scripts/backup_db.sh`) | B |

---

## 8. W7 — QA & báo cáo (G5)

**Cổng G5:** test case pass ≥ 95% · báo cáo đủ 80% · có video demo.

| # | Việc | Ai |
|---|---|---|
| 1 | QA hồi quy toàn bộ, ghi bug vào Issue | D |
| 2 | Sửa bug (chỉ bug chặn demo) | A, B, C |
| 3 | Quay video demo 3–5 phút | D |
| 4 | Biên tập báo cáo, thống nhất format, chèn ảnh | D |
| 5 | Tập bảo vệ lần 1: mỗi người 5 phút | cả nhóm |

---

## 9. W8 — Đóng băng (G6)

**Cổng G6:** trước hạn 3 ngày · không merge gì trừ `hotfix` · mọi người trình bày được toàn hệ thống.

| # | Việc | Ai |
|---|---|---|
| 1 | **Đóng băng code** — chỉ nhận `hotfix` | D |
| 2 | Chạy demo trên **máy khác** (máy bạn, máy lab) | D |
| 3 | Trả lời lại toàn bộ sổ "chưa trả lời được" | cả nhóm |
| 4 | Hỏi chéo lần cuối: mỗi người 5 câu ngẫu nhiên bất kỳ vùng | cả nhóm |
| 5 | Nộp: installer + source + báo cáo PDF + video | D |

---

## 10. Nếu trễ — cắt theo thứ tự này

Cắt **từ dưới lên**, không cắt tùy ý:

```
1. Ảnh minh hoạ món, icon đẹp            ← cắt được, không mất điểm chức năng
2. Auto-update, màn About
3. Xuất PDF (giữ Excel)
4. Biểu đồ nâng cao (giữ 2 biểu đồ chính)
5. Tồn nguyên liệu, ca làm việc          ← tính năng mốc 8, không có vẫn đủ đề bài
6. Tìm kiếm nâng cao (giữ tìm cơ bản)
7. ─────────────────────────── KHÔNG CẮT DƯỚI ĐÂY ───────────────────────────
   CRUD · Login · phân quyền · thống kê cơ bản · tìm kiếm cơ bản · BỘ CÀI
```

Nếu phải cắt tới mức 6 → **họp nhóm ngay**, báo GV sớm thay vì nộp thiếu.

## 11. D làm gì mỗi tuần (vai trò điều phối)

| Việc | Nhịp |
|---|---|
| Cập nhật bảng điều khiển tuần (Issue `W<n>`) | mỗi tối |
| Rà Issue không assignee / quá hạn → gán hoặc đóng | mỗi tối |
| Review PR của A/B/C trong 24h | khi có PR |
| Gỡ chặn môi trường (`make doctor`, Docker, Python) | khi được gọi |
| Chụp ảnh + điền test case + cập nhật `CHANGELOG.md` | cuối tuần |
| Tổng hợp tiến độ 5 dòng gửi nhóm (+ GV khi cần) | Chủ nhật |

> D **không code hộ**. Chỉ tay, giải thích, để họ gõ — vì đề bài tính điểm cá nhân và hỏi bất kỳ phần nào.
