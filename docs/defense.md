# Bảo vệ bài — hiểu cái mình đã viết

> Mục đích: **không ai merge được đoạn code mà mình không giải thích được.**
> Đề bài ghi rõ: *"Sinh viên phải tự làm… Nếu bị phát hiện copy → 0 điểm."* Giảng viên có thể
> hỏi **bất kỳ phần nào**, kể cả phần của người khác.

## Ba luật

1. **Không merge PR mà mình không giải thích được.** Kể cả khi CI xanh.
2. **Mỗi PR phải có mục "Giải thích được"** — 3 câu, viết trong template PR.
3. **Thứ 6, 15 phút hỏi chéo:** mỗi người bị hỏi 2 câu về vùng **của người khác**
   (A bị hỏi về GUI, C bị hỏi về DB…). Không trả lời được → ghi vào sổ "chưa trả lời được".

## Cách dùng hằng ngày (3 phút/PR)

Trước khi bấm "Create pull request", tự trả lời:

| Câu | Ghi vào PR |
|---|---|
| Đoạn code này làm gì? | 1 câu, không dùng từ "xử lý", "quản lý" chung chung |
| Vì sao chọn cách này, không phải cách khác? | 1 câu, nêu **trade-off** |
| Nếu thầy hỏi "sao không dùng X?" | 1 câu, so sánh với phương án bị loại |

Nếu không viết được 3 câu này → **chưa hiểu bài**, đừng mở PR.

---

## Ngân hàng câu hỏi

> Cột "chỉ vào" = mở file nào để trả lời. **Trả lời bằng cách chỉ vào code**, không nói lý thuyết.

### Chung — ai cũng có thể bị hỏi

| # | Câu hỏi | Chỉ vào |
|---|---|---|
| 1 | Bài toán thực tế là gì, ai dùng, dùng khi nào? | `report/01-mo-dau.md` |
| 2 | Vẽ kiến trúc tổng thể. Vì sao GUI không nối thẳng MySQL? | `WORKFLOW.md` mục 4, `docs/decisions.md` ADR-006 |
| 3 | Từ lúc bấm "Thanh toán" đến khi ghi vào DB, dữ liệu đi qua những đâu? | `gui/api_client.py` → `api/routers/` → `api/services/` → `api/models/` |
| 4 | Nếu 20 nhân viên dùng cùng lúc thì sao? | Pool connection, transaction, index |
| 5 | Hai thu ngân cùng thanh toán một bàn thì sao? | Kiểm trạng thái trong transaction |
| 6 | Mật khẩu lưu thế nào? Sao không lưu thẳng? | `api/core/security.py`, bcrypt cost |
| 7 | Điểm yếu của bài là gì? Làm lại thì làm gì khác? | `report/08-kho-khan.md`, `grep shortcut:` |
| 8 | **Phần nào em tự làm?** | Lịch sử commit + PR của chính mình |

### A — Backend / API

| # | Câu hỏi | Chỉ vào |
|---|---|---|
| 1 | JWT là gì? Token chứa gì? Hết hạn thì xử lý sao? | `api/core/security.py` |
| 2 | Phân quyền kiểm ở đâu? Em sửa request gửi lên thì có qua mặt được không? | `require_role` + test 403 |
| 3 | Vì sao router không viết SQL? | `api/routers/` vs `api/services/` |
| 4 | Tạo đơn mà lỗi giữa chừng thì dữ liệu ra sao? | transaction trong service |
| 5 | `Depends(get_db)` hoạt động thế nào? | `api/core/db.py` |
| 6 | Vì sao bọc `data`/`meta`/`error`? | `WORKFLOW.md` mục 9.3 |
| 7 | Lỗi 500 client nhận gì? Sao không trả stack trace? | exception handler |
| 8 | 401 khác 403 ở đâu? | `shared/error_codes.py` |
| 9 | Làm sao chống SQL injection? | ORM / bind param, không nối chuỗi |
| 10 | Đoạn `Depends(require_role(...))` chạy khi nào? | FastAPI dependency graph |

### B — Dữ liệu & báo cáo

| # | Câu hỏi | Chỉ vào |
|---|---|---|
| 1 | Vì sao 9 bảng, sao không gộp bớt? | `docs/erd.md`, chuẩn hoá |
| 2 | Vì sao `order_items` lưu `unit_price` riêng? | Giá tại thời điểm bán |
| 3 | Vì sao tiền là `DECIMAL` không `FLOAT`? | sai số nhị phân |
| 4 | Index đặt ở đâu, vì sao? | `db/schema.sql`, `EXPLAIN` |
| 5 | Viết query doanh thu theo ngày. | `api/services/reports.py` |
| 6 | Vì sao `is_deleted` thay vì `DELETE`? | `WORKFLOW.md` mục 8.3 |
| 7 | `ON DELETE RESTRICT` để làm gì? | FK trong `schema.sql` |
| 8 | Seed 120 đơn, tổng tiền có khớp không? Kiểm thế nào? | `scripts/seed_data.py`, test |
| 9 | N+1 query là gì? Bài em có bị không? | `selectinload`/`joinedload` |
| 10 | Số trên báo cáo lấy từ đâu, có thể lệch màn hình không? | cùng 1 hàm service |

### C — Giao diện

| # | Câu hỏi | Chỉ vào |
|---|---|---|
| 1 | Vì sao PySide6, không Tkinter? | `docs/decisions.md` ADR-003 |
| 2 | Gọi API mất 2 giây thì UI thế nào? Vì sao không treo? | worker/QThread trong `gui/` |
| 3 | Màn hình có 4 trạng thái — kể tên và vì sao cần? | skill `pyside6-screen` mục 4 trạng thái |
| 4 | Palette lấy ở đâu? Vì sao navy? | `gui/theme.py` + `docs/decisions.md` ADR-007 |
| 5 | Spacing theo lưới nào, vì sao? | `gui/theme.py`, skill `ui-design` |
| 6 | `api_client` để làm gì? Sao không gọi `requests` rải rác? | 1 điểm sửa, dễ test |
| 7 | API trả 500 thì GUI hiển thị gì? | nhánh `error` + `error.code` |
| 8 | Tiếng Việt: font gì, vì sao không dùng font mặc định? | `gui/theme.py`, `assets/fonts/` |
| 9 | Signal/slot là gì? Ví dụ trong bài? | kết nối worker → view |
| 10 | Resize 1280 vs full HD em xử lý sao? | layout/`QSizePolicy` |

### D — Hạ tầng, QA, đóng gói

| # | Câu hỏi | Chỉ vào |
|---|---|---|
| 1 | Docker là gì? Vì sao dùng cho MySQL? | `docker-compose.yml` |
| 2 | Vì sao cổng 3307 không 3306? | `docs/decisions.md` ADR-004 |
| 3 | `hiddenimports` để làm gì? | `installer/cafetlu.spec` |
| 4 | Vì sao `--onedir` không `--onefile`? | thời gian khởi động, antivirus |
| 5 | App đọc ảnh thế nào khi đã đóng gói? | `shared/paths.py::resource_path` |
| 6 | CI làm gì? Mấy job? Khi nào chạy? | `.github/workflows/ci.yml` |
| 7 | Làm sao build `.exe` khi cả nhóm dùng macOS? | `release.yml`, `windows-latest` |
| 8 | Đã chạy bao nhiêu test case, pass bao nhiêu? | `docs/test-cases.md` |
| 9 | Làm sao chắc app chạy trên máy người khác? | test trên máy sạch, `TC-PKG-01` |
| 10 | Deploy thế nào, bảo mật ra sao? | `infra/deploy.md`, skill `security` |

### Câu hỏi bẫy (hay gặp nhất)

| Câu hỏi | Cách trả lời đúng |
|---|---|
| "Sao không dùng [công nghệ phổ biến]?" | Nêu **trade-off**, không phủ nhận: *"Dùng được, nhưng nhóm chọn X vì… đổi lại phải chấp nhận…"* |
| "Chỗ này em copy ở đâu?" | Mở commit + PR, chỉ phần mình viết, giải thích từng dòng |
| "Thầy tắt API thì app thế nào?" | Mô tả đúng hành vi: báo lỗi kết nối, không treo, có nút thử lại |
| "Dòng này làm gì?" (trỏ ngẫu nhiên) | Phải đọc được code của chính mình — đây là lý do không dùng code mình không hiểu |
| "Em làm phần nào?" | Nói thật + chỉ file. Không nhận phần người khác, không đùn đẩy |
| "Nếu dữ liệu 1 triệu đơn?" | Nêu index + phân trang + query đã tối ưu, và chỗ chưa tối ưu (`shortcut:`) |

---

## Quy trình 15 phút thứ 6 (hỏi chéo)

1. Mỗi người **demo phần mình** chạy thật trên `develop` (3 phút) — `WORKFLOW.md` mục 16.2.
2. Mỗi người bị hỏi **2 câu ngẫu nhiên** từ vùng của người khác.
3. Không trả lời được → **ghi vào sổ "chưa trả lời được"**, không bị phạt, nhưng phải trả lời được vào thứ 6 sau.
4. Ghi lại 1 câu hay nhất vào `report/08-kho-khan.md` (dùng cho báo cáo).

> Nếu ai cũng trả lời trôi chảy → tăng độ khó: hỏi câu bẫy, hoặc trỏ vào dòng code bất kỳ.

## Sổ "chưa trả lời được"

| Ngày | Người | Câu hỏi | Đã trả lời lại? |
|---|---|---|---|
| | | | |

## Checklist trước khi nộp / trước buổi bảo vệ

- [ ] Mỗi người đã trả lời được **≥ 80%** câu trong ngân hàng của **vùng mình**
- [ ] Mỗi người trả lời được **≥ 5 câu** ở vùng của người khác
- [ ] Mọi PR đã merge đều có mục "Giải thích được" 3 câu
- [ ] Không còn dòng nào trong sổ "chưa trả lời được" chưa trả lời lại
- [ ] `grep -rn "shortcut:" --include=*.py .` → mỗi dòng đều giải thích được vì sao cắt
- [ ] Demo chạy được trên **máy không phải máy mình**
- [ ] Mỗi người có thể trình bày toàn bộ hệ thống trong **5 phút**
