# Lộ trình theo cổng — làm gì, giao theo thứ tự nào

> Bổ trợ cho [`docs/workflow.md`](workflow.md) (luồng làm chức năng từ Issue đến `develop`) và
> `WORKFLOW.md` mục 16.3 (điều kiện cổng). File này trả lời: **việc gì mở khoá cổng, Issue nào đang
> mở, và giao theo thứ tự phụ thuộc nào.**
>
> Không chia theo tuần. Cổng mở khi **đủ điều kiện**, không phải khi hết lịch — nhóm chạy nhanh
> thì qua cổng sớm, chậm thì cổng dời lại nhưng thứ tự phụ thuộc không đổi.
>
> Xem tiến độ và người phụ trách thực tế ở [milestone GitHub](https://github.com/Haianh4705/cafe-tlu/milestones).
>
> **Thành viên nhóm (giao việc theo chức năng — ADR-014):** A = [@bao20062005dh-creator](https://github.com/bao20062005dh-creator) ·
> B = [@trungdunxg](https://github.com/trungdunxg) ·
> C = [@MeoCamGuitar](https://github.com/MeoCamGuitar) ·
> D = [@Haianh4705](https://github.com/Haianh4705)

## 0. Không biết làm gì thì hỏi

```bash
make next                     # xem Issue tiếp theo được gán cho bạn
```

Hoặc mở AI agent trong repo và hỏi: *"Đọc AGENTS.md và skill next-task, cho tôi biết việc tiếp
theo của tôi."* — agent chạy `make next`, đọc Issue và trả lời: làm gì · xong khi nào · skill
nào phải đọc · đang chờ Issue nào.

## 0.1 Sáu nguyên tắc giao việc theo chức năng (ADR-014)

1. **Giao theo chức năng, không khoá cứng thư mục.** Một Issue chức năng có thể chạm trọn gói
   `db/` + `api/` + `gui/` + `tests/` để chạy end-to-end, miễn giữ kiến trúc `gui → api → db`.
2. **Đường găng và phụ thuộc trước.** Việc mở khoá cho chức năng sau (như migrate DB `#78`, nút
   đăng xuất `#79`, API `/tables` + `/orders` `#93`) được ưu tiên gán trước.
3. **Mỗi người tối đa 2 Issue đang làm** (WIP limit). Xong Issue cũ mới nhận Issue mới.
4. **Giao kèm 3 thứ trên Issue:** kết quả + tiêu chí nghiệm thu, skill cần đọc theo các tầng chạm
   tới (`.claude/skills/…`), và Issue phụ thuộc.
5. **Bỏ bắt buộc approve — tác giả tự Squash & merge** khi CI xanh và đủ checklist + 3 câu bảo vệ +
   nhật ký cá nhân (`WORKFLOW.md` mục 3.2).
6. **Làm Issue nào, ghi nhật ký vào `docs/log/<vai>.md` của chính mình** — 1–3 dòng/PR, ghi cả phần
   AI hỗ trợ. File trống ở thời điểm cổng = cổng chưa xanh (`WORKFLOW.md` mục 12.5).

## 1. Toàn cảnh

| Cổng | Mục tiêu | Điều kiện ra cổng | Đường găng chính |
|---|---|---|---|
| **G1 — Nền móng** | Dữ liệu + khung 2 đầu chạy được | 3/3 máy A/C/D `make doctor` xanh (ADR-012) · CI xanh · installer cài được · DB có 51 món · Swagger mở được | `#17` → `#21` → `#22` → `#25` |
| **G2 — Lát cắt dọc** | Login → CRUD món chạy end-to-end | Chạy trên máy người khác · `staff` bị 403 · ≥ 12 endpoint có test | `#29`, `#30`, `#78`, `#79`, `#81`–`#85` |
| **G3 — MVP** | Đủ 6 yêu cầu đề bài | Order + hoá đơn + thống kê + báo cáo chạy · installer từ CI cài trên máy sạch | `#93` → `#94` · `#95` · `#96` → `#97` |
| **G4 — Deploy** | Backend công khai, phát hành tự động | URL công khai · tag → CI build `.exe` · `pip-audit` sạch | `#89` → `#98` · `#99` · `#100` |
| **G5 — QA** | Hồi quy + báo cáo | Test case pass ≥ 95% · báo cáo ≥ 80% · có video demo | `#101` → `#102` → `#103` |
| **G6 — Đóng băng** | Chốt và nộp | Trước hạn 3 ngày · chỉ nhận `hotfix` · cả nhóm trình bày được | cả nhóm |

Giữa **G3 và G4** có một chặng không phải cổng: **đánh bóng UI + tối ưu query** (mục 5).
Chặng này chen vào được bất cứ lúc nào G3 đã xong, trước khi bắt đầu G4.

---

## 2. G1 — Nền móng

**Mục tiêu:** mỗi người chạy được hệ thống trên máy mình; DB có 50 món; Swagger mở được.
**Ra cổng khi:** 3/3 máy **A, C, D** `make doctor` xanh (máy B không tính — ADR-012; phần DB kiểm bằng `db/verify_seed.sql`) · CI xanh · **có bản cài cài được** trên Windows sạch.

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

> Các hạng mục dưới đây đều đã có Issue trên GitHub để D gán linh hoạt cho thành viên theo chức năng (không khoá cứng theo vai thư mục). Giao diện `OrderView`/`DashboardView` đã có khung từ #44, #70 — cần hoàn thiện nối API thật, sửa bug phát sinh và nghiệm thu.

| # | Chức năng / Đầu việc | Issue | Tầng chạm | Phụ thuộc | Trạng thái / Gán |
|---|---|---|---|---|---|
| 1 | Quản lý bàn & gọi món tại bàn end-to-end (`GET /tables`, CRUD `orders` + nối `OrderView`) | #93 | `api`, `gui` | #29 ✅ | Gán theo Issue |
| 2 | Tải đầy đủ món đang bán trong màn Order (không cắt ở 20 món trang đầu) | #87 | `gui` | #93 / #70 ✅ | Đang gán C |
| 3 | Thanh toán đơn hàng & xuất/in hoá đơn PDF (`POST /orders/{id}/checkout` + `ReceiptDialog`) | #94 | `api`, `gui`, `report` | #93 | Gán theo Issue |
| 4 | Báo cáo doanh thu, Top món & xuất Excel/PDF (`GET /reports/*` + nối `DashboardView`) | #95 | `api`, `gui`, `report` | #28 ✅, #31 ✅ | Gán theo Issue |
| 5 | Hiện đúng KPI hôm nay khi không có giao dịch | #88 | `gui` | #70 ✅, #95 | Đang gán C |
| 6 | Nhật ký thao tác quản trị (ghi `audit_logs` + `GET /audit-logs`) | #96 | `api`, `db` | #29 ✅, #94 | Gán theo Issue |
| 7 | Kịch bản `scripts/smoke_test.py`, điền `TC-ORD`/`TC-RPT`, ảnh chụp & kiểm bộ cài MVP | #97 | `infra`, `docs` | #93, #94, #95, #96 | Gán theo Issue |

> **Rủi ro lớn nhất của G3:** transaction của `checkout` (#94). Bắt buộc giữ các bất biến đã ghi ở mục 3.3 của `docs/erd.md` (1 bàn tối đa 1 đơn mở, lưu snapshot `unit_price`, cập nhật `orders.status` + `invoices` + `tables.status` trong 1 transaction).

**Ra cổng G3 = MVP.** Từ đây **không thêm tính năng mới** trừ khi đã xong hết việc tối ưu.

---

## 5. Giữa G3 và G4 — Đánh bóng

**Mục tiêu:** mốc 8 nằm ở đây — "giao diện đẹp, tối ưu, báo cáo viết tốt". Chặng này mở ngay khi
G3 xong, không cần chờ cổng nào.

| # | Việc | Hình thức thực hiện |
|---|---|---|
| 1 | Rà toàn bộ UI theo skill `ui-design` (spacing 8pt, 4 trạng thái, phím tắt, toast) | Mở Issue `[gui]` nếu cần sửa |
| 2 | UI review 30 phút cả nhóm, chốt danh sách sửa | Họp nhóm + ghi Issue |
| 3 | Vá các `shortcut:` còn rẻ (`grep -rn "shortcut:" --include=*.py .`) | Mở Issue cho phần muốn nâng cấp |
| 4 | Đo hiệu năng: 5.000 món / 5.000 đơn — chỗ nào chậm | Kiểm chứng + Issue `[perf]` |
| 5 | Viết dần nội dung các chương báo cáo (`report/`) từ code và số liệu thật | Qua #102 |

---

## 6. G4 — Deploy

**Mục tiêu:** backend có URL công khai · tag → CI tự build `.exe` · `pip-audit` sạch · các việc hạ tầng/bảo mật hoàn tất.

| # | Chức năng / Đầu việc | Issue | Tầng chạm | Phụ thuộc |
|---|---|---|---|---|
| 1 | `make doctor` chạy chuẩn trên Windows không cần override `SHELL`/`PY` | #76 | `infra` | – (đang gán D) |
| 2 | Chặn publish bộ cài trên Release workflow khi kiểm tra Windows thất bại | #80 | `infra` | #26 ✅ (đang gán D) |
| 3 | Củng cố vòng đời phiên (`/auth/refresh` khi khoá tài khoản) & dữ liệu phản hồi xác thực | #86 | `api` | #22 ✅ (đang gán A) |
| 4 | Nối `docker-compose.prod.yml` với MySQL & nâng cấp schema bằng Alembic | #89 | `infra`, `db` | #78 (đang gán D) |
| 5 | Triển khai Backend lên URL công khai, cấu hình `API_BASE_URL` cho GUI & kiểm `pip-audit` | #98 | `infra`, `gui`, `docs` | #89 |
| 6 | Màn giới thiệu (About) & kiểm tra cập nhật phiên bản từ GitHub Releases | #99 | `gui`, `infra` | #26 ✅ |
| 7 | Kịch bản sao lưu MySQL (`scripts/backup_db.sh`) & rate-limit `/auth/login` + rà `security` | #100 | `api`, `db`, `infra` | #86, #89 |

---

## 7. G5 — QA & báo cáo

**Ra cổng khi:** test case pass ≥ 95% · báo cáo đủ 80% · có video demo.

| # | Chức năng / Đầu việc | Issue | Tầng chạm | Phụ thuộc |
|---|---|---|---|---|
| 1 | Kiểm thử hồi quy toàn bộ `docs/test-cases.md` (≥95% PASS) + bộ ảnh chụp màn hình | #101 | `docs`, `gui` | G3 (#97) + G4 |
| 2 | Sửa các lỗi `[bug]` chặn demo phát hiện trong quá trình QA | (tạo Issue `[bug]` theo ca FAIL) | tuỳ lỗi | #101 |
| 3 | Hoàn thiện Báo cáo BTL 10 chương (`report/00..09`) từ dữ liệu thật và xuất PDF | #102 | `docs` | #32 + #101 |
| 4 | Quay Video Demo 3–5 phút & diễn tập bảo vệ chéo (`docs/defense.md` + `docs/log/*.md`) | #103 | `docs` | #101 + #102 |

---

## 8. G6 — Đóng băng

**Ra cổng khi:** trước hạn nộp 3 ngày · không merge gì trừ `hotfix` · mọi người trình bày được
toàn hệ thống.

| # | Việc | Phụ trách |
|---|---|---|
| 1 | **Đóng băng code** — chỉ nhận `hotfix` | D điều phối, cả nhóm tuân thủ |
| 2 | Chạy demo trên **máy khác** (máy bạn, máy lab) | Cả nhóm / người được giao kiểm tra |
| 3 | Trả lời lại toàn bộ sổ "chưa trả lời được" (`docs/defense.md`) | Cả nhóm |
| 4 | Hỏi chéo lần cuối: mỗi người 5 câu ngẫu nhiên bất kỳ phần nào | Cả nhóm |
| 5 | Nộp: installer `.exe` + source + báo cáo PDF + video demo | D tổng hợp nộp |

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

## 10. Đang chờ hoặc bị phụ thuộc thì làm gì

Không ngồi chờ. Khi Issue hiện tại đang đợi phần phụ thuộc:

| Tình huống | Việc làm tiếp |
|---|---|
| Chưa có bảng/cột DB cần cho chức năng | Nếu thuộc phạm vi Issue được giao: tạo migration Alembic mới + cập nhật `db/schema.sql` theo `WORKFLOW.md` mục 8 |
| Chưa có endpoint cần nối GUI | Nếu thuộc Issue chức năng trọn gói: tự code luôn endpoint theo `docs/api-contract.md`; nếu tách riêng: dựng GUI với `MOCK_*` / viết test trước |
| Đã xong hết Issue đang giữ | Chạy `gh issue list --state open --assignee ""` hoặc nhắn D nhận thêm Issue chức năng chưa gán |
| Bị lỗi môi trường / CI | Xem mục Xử lý sự cố ở `README.md`, hoặc tag D ngay trong Issue |

## 11. D làm gì (vai trò điều phối + tham gia xử lý chức năng)

| Việc | Nhịp |
|---|---|
| Tạo Issue chức năng rõ ràng và gán cho thành viên phù hợp (hoặc tự nhận xử lý khi cần mở khoá đường găng) | khi lập sóng / mở cổng |
| Cập nhật bảng điều khiển cổng (Issue `G1`/`G2`) và rà Issue thiếu assignee / quá hạn | mỗi ngày |
| Hỗ trợ gỡ chặn môi trường (`make doctor`, Docker, CI, MySQL) | khi được gọi |
| Tổng hợp kiểm chứng, biên tập báo cáo & video demo | các mốc G3–G6 |
| Kiểm `docs/log/<vai>.md` của cả nhóm trước mỗi cổng (file trống = cổng chưa xanh) | trước mỗi cổng |

> Dù D hỗ trợ gỡ chặn hay làm trực tiếp Issue chức năng nào, **mọi code trong PR** đều phải kèm 3 câu giải thích và ghi nhật ký rõ ràng để cả nhóm hiểu và bảo vệ được trước GV.
