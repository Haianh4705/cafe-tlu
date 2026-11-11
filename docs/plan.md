# Lộ trình theo cổng — làm gì, giao theo thứ tự nào

> Bổ trợ cho [`docs/workflow.md`](workflow.md) (ai bàn giao cho ai) và `WORKFLOW.md` mục 16.3
> (điều kiện cổng). File này trả lời: **đang ở cổng nào, việc gì mở khoá cổng đó, và giao việc
> theo thứ tự nào.**
>
> Không chia theo tuần. Cổng mở khi **đủ điều kiện**, không phải khi hết lịch — nhóm chạy nhanh
> thì qua cổng sớm, chậm thì cổng dời lại nhưng thứ tự công việc không đổi.
>
> **Phân vai đã chốt:** A = [@bao20062005dh-creator](https://github.com/bao20062005dh-creator) ·
> B = [@trungdunxg](https://github.com/trungdunxg) ·
> C = [@MeoCamGuitar](https://github.com/MeoCamGuitar) ·
> D = [@Haianh4705](https://github.com/Haianh4705)

## 0. Không biết làm gì thì hỏi

```bash
make next                     # người dùng
```

Hoặc mở AI agent trong repo và hỏi: *"Đọc AGENTS.md và skill next-task, cho tôi biết việc tiếp
theo của tôi."* — agent chạy `make next`, đọc Issue và trả lời: làm gì · xong khi nào · skill
nào phải đọc · đang chờ ai.

## 0.1 Sáu quy tắc giao việc

1. **Đường găng trước.** `db/schema.sql` chặn A và C → giao cho B **ngay khi nhận việc**, không chờ họp.
2. **Giao theo "sóng", không giao phẳng.** Sóng 1 = việc không phụ thuộc ai (4 người chạy song song).
   Sóng 2 = việc chỉ chờ sóng 1. Không ai ngồi chờ vì giao sai thứ tự.
3. **Mỗi người tối đa 2 việc đang làm** (WIP limit). Hết việc mới nhận thêm.
4. **Giao kèm 3 thứ**: link Issue, skill cần đọc (`.claude/skills/…`), và người review.
5. **D giữ 20% thời gian** cho việc gỡ chặn, không nhận việc code kín lịch.
6. **Ai làm việc đó thì ghi vào `docs/log/<vai>.md`** — 1–3 dòng/PR, ghi cả phần AI hỗ trợ.
   File trống ở thời điểm cổng = cổng chưa xanh (`WORKFLOW.md` mục 12.5).

## 1. Toàn cảnh

| Cổng | Mục tiêu | Điều kiện ra cổng | Đường găng |
|---|---|---|---|
| **G1 — Nền móng** | Dữ liệu + khung 2 đầu chạy được | 4/4 máy `make doctor` xanh · CI xanh · installer cài được · DB có 50 món · Swagger mở được | B: schema → A: models |
| **G2 — Lát cắt dọc** | Login → CRUD món chạy end-to-end | Chạy trên máy người khác · `staff` bị 403 · ≥ 12 endpoint có test | A: CRUD → C: màn hình |
| **G3 — MVP** | Đủ 6 yêu cầu đề bài | Order + hoá đơn + thống kê + báo cáo chạy · installer từ CI cài trên máy sạch | A: orders API → C: màn order → B: thống kê |
| **G4 — Deploy** | Backend công khai, phát hành tự động | URL công khai · tag → CI build `.exe` · `pip-audit` sạch | D: Docker + deploy |
| **G5 — QA** | Hồi quy + báo cáo | Test case pass ≥ 95% · báo cáo ≥ 80% · có video demo | D: QA + biên tập |
| **G6 — Đóng băng** | Chốt và nộp | Trước hạn 3 ngày · chỉ nhận `hotfix` · cả nhóm trình bày được | cả nhóm |

Giữa **G3 và G4** có một chặng không phải cổng: **đánh bóng UI + tối ưu query** (mục 5).
Chặng này chen vào được bất cứ lúc nào G3 đã xong, trước khi bắt đầu G4.

---

## 2. G1 — Nền móng

**Mục tiêu:** mỗi người chạy được hệ thống trên máy mình; DB có 50 món; Swagger mở được.
**Ra cổng khi:** 4/4 máy `make doctor` xanh · CI xanh · **có bản cài cài được** trên Windows sạch.

### Sóng 1 — không phụ thuộc ai, cả 4 chạy ngay

| # | Việc | Ai | Issue | ~giờ |
|---|---|---|---|---|
| 1 | **Thiết kế ERD** (`docs/erd.md`) + `db/schema.sql` | B | #17 | 6 |
| 2 | Khung `api/` + `/health` | A | #19 | 2 |
| 3 | Khung `gui/` + `theme.py` (palette TLU) + `BaseView` | C | #23 | 4 |
| 4 | Build installer lần 1 trên CI | D | #26 | 3 |

### Sóng 2 — chỉ bắt đầu khi việc phụ thuộc đã xong

| # | Việc | Ai | Issue | Phụ thuộc |
|---|---|---|---|---|
| 5 | `db/seed.sql` — 50 món, 5 users bcrypt | B | #18 | #17 |
| 6 | Config + kết nối MySQL (`get_db`) | A | #20 | #19 |
| 7 | Models theo ERD của B | A | #21 | **#17** |
| 8 | `api_client.py` + `i18n.py` | C | #24 | contract (đã có) |
| 9 | `make doctor` kiểm tra MySQL + Dockerfile | D | #27 | – |

### Sóng 3

| # | Việc | Ai | Issue | Phụ thuộc |
|---|---|---|---|---|
| 10 | Auth JWT + `require_role` | A | #22 | #21 |
| 11 | Màn Đăng nhập (nối API thật) | C | #25 | #24, #22 |

**Ra cổng G1 phải có:** `make up` + `make api` ra Swagger · 50 món trong DB · cửa sổ GUI mở được ·
1 file `Setup.exe` cài được trên máy Windows · demo + hỏi chéo.

---

## 3. G2 — Lát cắt dọc

**Mục tiêu:** đăng nhập → xem/thêm/sửa/xoá món, chạy end-to-end từ GUI xuống DB.
**Ra cổng khi:** chạy trên **máy người khác** · `staff` bị 403 ở chức năng admin · ≥ 12 endpoint có test.

### Sóng 1

| # | Việc | Ai | Issue | ~giờ |
|---|---|---|---|---|
| 1 | CRUD products + categories (5 endpoint) | A | #29 | 6 |
| 2 | Sinh 120 đơn trải 30 ngày | B | #28 | 3 |
| 3 | Khung báo cáo + phân chương (10 file) | D | #32 | 3 |

### Sóng 2

| # | Việc | Ai | Issue | Phụ thuộc |
|---|---|---|---|---|
| 4 | Query thống kê: doanh thu, top món | B | #31 | #28 |
| 5 | Màn Danh sách món (bảng + tìm kiếm + 4 trạng thái) | C | #30 | #29, #24 |

### Sóng 3

| # | Việc | Ai | Việc cụ thể |
|---|---|---|---|
| 6 | Test case `TC-AUTH`, `TC-PRD`, `TC-SRC` | D | điền PASS/FAIL + chụp ảnh |
| 7 | Fix bug do QA phát hiện | A, C | theo Issue mới |

**Ra cổng G2 phải có:** luồng đầy đủ chạy được · ảnh chụp màn hình mới · Swagger ≥ 12 endpoint ·
mỗi PR có "Giải thích được" 3 câu.

---

## 4. G3 — MVP

**Mục tiêu:** đủ **6 yêu cầu đề bài**: CRUD · Login · thống kê · tìm kiếm · bộ cài · phân quyền.
**Ra cổng khi:** installer cài được trên máy sạch · đủ chức năng · demo chạy full luồng.

### Sóng 1 — Order tại bàn

| # | Việc | Ai |
|---|---|---|
| 1 | Models + API `orders` (tạo đơn, thêm/xoá món) | A |
| 2 | Seed bàn + trạng thái bàn | B |
| 3 | Màn Order: chọn bàn, danh sách món, giỏ | C |
| 4 | Test case `TC-ORD` + smoke test luồng chính | D |

### Sóng 2 — Thanh toán + báo cáo

| # | Việc | Ai |
|---|---|---|
| 5 | API `checkout` (transaction, tạo `invoices`, đóng bàn) | A |
| 6 | Màn Thanh toán + xác nhận + in bill (reportlab) | C |
| 7 | API báo cáo: doanh thu ngày/tháng, top món, theo danh mục | A |
| 8 | Xuất Excel (openpyxl) + PDF (reportlab, **font tiếng Việt**) | B |
| 9 | Dashboard: 4 thẻ KPI + 2 biểu đồ | C |
| 10 | Installer bản đầy đủ + test gỡ cài đặt | D |

### Sóng 3 — Chốt MVP

| # | Việc | Ai |
|---|---|---|
| 11 | Tối ưu: index, phân trang, sửa N+1 | A |
| 12 | Đối chiếu số liệu: màn hình vs file xuất vs SQL tay | B |
| 13 | Màn Báo cáo + bộ lọc ngày | C |
| 14 | Chạy toàn bộ `docs/test-cases.md` | D |

> **Rủi ro lớn nhất của G3:** transaction của `checkout`. Nếu A và B không thống nhất bất biến
> đã ghi ở mục 3.3 của `docs/erd.md` (do B viết), dữ liệu sẽ lệch và báo cáo sai. Chốt trước khi code.

**Ra cổng G3 = MVP.** Từ đây **không thêm tính năng mới** trừ khi đã xong hết việc tối ưu.

---

## 5. Giữa G3 và G4 — Đánh bóng

**Mục tiêu:** mốc 8 nằm ở đây — "giao diện đẹp, tối ưu, báo cáo viết tốt". Chặng này mở ngay khi
G3 xong, không cần chờ cổng nào.

| # | Việc | Ai |
|---|---|---|
| 1 | Rà toàn bộ UI theo skill `ui-design` (spacing 8pt, 4 trạng thái, phím tắt, toast) | C |
| 2 | UI review 30 phút cả nhóm, chốt danh sách sửa | cả nhóm |
| 3 | Vá các `shortcut:` còn rẻ (grep `shortcut:`) | A, B |
| 4 | Đo hiệu năng: 5.000 món / 5.000 đơn — chỗ nào chậm | D |
| 5 | Viết chương báo cáo của mình (mỗi người 1–2 chương) | cả nhóm |

---

## 6. G4 — Deploy

**Ra cổng khi:** backend có URL công khai · tag → CI tự build `.exe` · `pip-audit` sạch.

| # | Việc | Ai |
|---|---|---|
| 1 | `infra/Dockerfile` + `docker-compose.prod.yml` + deploy lên VPS/Render | D |
| 2 | Config production: tắt debug, `JWT_SECRET` mới, DB user không phải root | A |
| 3 | Auto-update: kiểm tra version + tải bản mới | D |
| 4 | Review bảo mật theo skill `security` (checklist G4) | A + D |
| 5 | Backup DB định kỳ (`scripts/backup_db.sh`) | B |

---

## 7. G5 — QA & báo cáo

**Ra cổng khi:** test case pass ≥ 95% · báo cáo đủ 80% · có video demo.

| # | Việc | Ai |
|---|---|---|
| 1 | QA hồi quy toàn bộ, ghi bug vào Issue | D |
| 2 | Sửa bug (chỉ bug chặn demo) | A, B, C |
| 3 | Quay video demo 3–5 phút | D |
| 4 | Biên tập báo cáo, thống nhất format, chèn ảnh | D |
| 5 | Tập bảo vệ lần 1: mỗi người 5 phút | cả nhóm |

---

## 8. G6 — Đóng băng

**Ra cổng khi:** trước hạn nộp 3 ngày · không merge gì trừ `hotfix` · mọi người trình bày được
toàn hệ thống.

| # | Việc | Ai |
|---|---|---|
| 1 | **Đóng băng code** — chỉ nhận `hotfix` | D |
| 2 | Chạy demo trên **máy khác** (máy bạn, máy lab) | D |
| 3 | Trả lời lại toàn bộ sổ "chưa trả lời được" | cả nhóm |
| 4 | Hỏi chéo lần cuối: mỗi người 5 câu ngẫu nhiên bất kỳ vùng | cả nhóm |
| 5 | Nộp: installer + source + báo cáo PDF + video | D |

---

## 9. Nếu trễ — cắt theo thứ tự này

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

## 10. Đang chờ người khác thì làm gì

Không ngồi chờ. Mỗi chỗ chờ đều có việc thay thế:

| Đang chờ | Việc thay thế |
|---|---|
| B chưa có `schema.sql` | Viết model nháp theo `docs/erd.md`, dựng UI/mock, viết test case |
| A chưa có endpoint | Dựng GUI với `MOCK_*`, viết test cho phần đã có, chuẩn bị request theo `docs/api-contract.md` |
| C chưa xong màn hình | A viết test API, B chuẩn bị seed/query, D viết test case + chụp ảnh cũ |
| D chưa có installer | Build thử PyInstaller trên máy mình, ghi lại lỗi vào Issue #26 |
| Không ai review PR | Nhắn trực tiếp reviewer, quá 24h thì nhờ D chuyển người |

## 11. D làm gì (vai trò điều phối)

| Việc | Nhịp |
|---|---|
| Cập nhật bảng điều khiển cổng (Issue `G<n>`) | mỗi tối |
| Rà Issue không assignee / quá hạn → gán hoặc đóng | mỗi tối |
| Review PR của A/B/C trong 24h | khi có PR |
| Gỡ chặn môi trường (`make doctor`, Docker, Python) | khi được gọi |
| Chụp ảnh + điền test case + cập nhật `CHANGELOG.md` | khi đóng cổng |
| Kiểm `docs/log/<vai>.md` của 3 người, nhắc ai còn trống (file trống = cổng chưa xanh) | trước mỗi cổng |
| Tổng hợp tiến độ 5 dòng gửi nhóm (+ GV khi cần) | khi có cổng mới hoặc khi trễ |

> D **không code hộ**. Chỉ tay, giải thích, để họ gõ — vì đề bài tính điểm cá nhân và hỏi bất kỳ phần nào.
