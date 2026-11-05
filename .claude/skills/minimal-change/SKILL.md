---
name: minimal-change
description: Viết thay đổi nhỏ nhất giải quyết trọn vẹn việc, trước khi code. Dùng cho MỌI việc code (thêm chức năng, sửa bug, refactor, chọn thư viện, review) — đặc biệt khi thấy mình sắp viết class/abstraction/option mới, hoặc sắp `pip install` một thư viện cho vài dòng.
---

# Thay đổi nhỏ nhất

## 0. Ranh giới quyền hạn (đọc trước tiên)

Skill này quyết định **CÁCH làm**, **không** quyết định **LÀM GÌ**.

| Việc | Ai quyết |
|---|---|
| Làm tính năng nào, mở rộng tới đâu | **Issue** (Definition of Ready) — không phải skill này |
| Dùng bao nhiêu dòng code, mấy lớp, lib nào | **Skill này** |
| Bỏ qua validate / test / ảnh chụp / tài liệu | **Không ai được quyết** — xem mục 5 |

Đồ án cần **mở rộng** để đạt mốc 8–9. Skill này không cản việc đó: nó chỉ cản việc
xây một tính năng đã được duyệt bằng 5 lớp abstraction không ai cần.

## 1. Trước khi viết, đọc

1. Đọc code mà thay đổi sẽ chạm tới — không đoán.
2. Liệt kê **mọi nơi** phải sửa: caller, test, fixture, config, export, chỗ khởi tạo.
3. Liệt kê **cái có thể vỡ**: dữ liệu bị mất/lộ, caller ngừng chạy, GUI đang hiển thị field đó.

Đó là **phạm vi**. Tính năng thêm ngoài Issue không phải phạm vi.

## 2. Bậc thang — dừng ở bậc đầu tiên đủ dùng

```
1. Việc này CÓ CẦN tồn tại không?
   → Không cần thì bỏ, và nêu tên nó trong 1 dòng cho người giao việc.
   → Nhưng: nếu Issue yêu cầu, thì nó cần. Không tự bỏ yêu cầu.

2. ĐÃ CÓ trong repo chưa? (helper, service, component, pattern)
   → Dùng đúng như code xung quanh đang dùng.

3. Thư viện chuẩn / tính năng nền tảng đã có?
   → Dùng. Qt có sẵn widget thì không tự vẽ. Python có `unicodedata`,
     `decimal`, `pathlib`, `functools` thì không cài lib.

4. Dependency ĐÃ CÀI?
   → Dùng. (PySide6, requests, openpyxl, reportlab, SQLAlchemy, pydantic)

5. Viết được 1 dòng mà người khác đọc hiểu ngay?
   → 1 dòng. (Một dòng cần giải mã thì không phải "ngắn".)

6. Không thì: code tối thiểu chạy được, đúng kiến trúc đã chốt.
```

## 3. Ví dụ trong dự án này

| ❌ Cách agent thường làm | ✅ Thay đổi nhỏ nhất |
|---|---|
| Tự viết 60 dòng widget chọn ngày | `QDateEdit` — Qt có sẵn |
| `pip install python-slugify` để bỏ dấu tiếng Việt | `unicodedata.normalize("NFD", s)` — stdlib |
| Thêm `ProductRepository` + `ProductMapper` + `ProductFactory` cho 3 endpoint | Router → service → model như đã chốt ở `WORKFLOW.md` mục 4 |
| Thêm 12 biến config "cho sau này" | Chỉ biến đang dùng, trong `.env.example` |
| Tự viết hàm phân trang | Dùng `page`/`page_size` + `PageMeta` đã có |
| Tự format tiền bằng f-string | `#,##0" đ"` — đã có trong skill `report-export` |
| Viết lại `api_client` cho từng màn hình | Một `gui/api_client.py` dùng chung |

## 4. Lười với **giải pháp**, không lười với **thay đổi**

- Sửa **hết** caller, test, fixture mà thay đổi của bạn làm hỏng — không để lại rác.
- Sửa bug: `grep` mọi nơi gọi hàm đó **trước** khi sửa, sửa một lần ở chỗ dùng chung.
- Code bạn di chuyển/gộp lại **giữ nguyên** xử lý lỗi và validate của nó.
- Comment chỉ khi giải thích **vì sao** mà code không tự nói được, 1 dòng.
- Giữ nguyên cấu trúc, layer, quy ước repo đã có. Không tự đổi kiến trúc.
- Hai lựa chọn cùng độ lớn → chọn cái đúng hơn ở trường hợp biên.

## 5. TUYỆT ĐỐI không cắt (dù "cho nhanh")

Các thứ sau **không phải** code thừa — cắt là mất điểm hoặc mất dữ liệu:

| Không cắt | Vì sao |
|---|---|
| Validate ở trust boundary (Pydantic) | Skill `security` |
| Xử lý lỗi chống mất dữ liệu, transaction | Mất đơn hàng = mất điểm |
| Kiểm quyền **ở server** | Ẩn nút không phải bảo mật |
| Test cho logic có nhánh/lặp/parse/tiền/bảo mật | `WORKFLOW.md` mục 11 |
| Ảnh chụp màn hình, `docs/test-cases.md` | GV chấm mốc 8 |
| `CHANGELOG.md`, cập nhật `api-contract.md` | Definition of Done |
| Báo cáo bàn giao 5 mục cho người nhận việc | `WORKFLOW.md` mục 15.4 |

> Nếu thấy mình đang "tối giản" một trong các mục trên → **dừng**, đó không phải tối giản,
> đó là bỏ việc.

## 6. Đánh dấu nợ kỹ thuật: `shortcut:`

Cắt bớt có chủ ý thì phải để lại dấu vết, theo `WORKFLOW.md` mục 7.1:

```python
# shortcut: chưa gộp bàn khác khu vực, nâng cấp khi quán yêu cầu (mốc 8)
```

Kiểm tra định kỳ: `grep -rn "shortcut:" --include=*.py .`

## 7. Kết thúc mỗi việc

Thêm 1–2 dòng vào mục **"Chưa làm / còn lại / rủi ro"** trong báo cáo handoff:

- đã **bỏ qua** gì (feature, option, tối ưu) và vì sao;
- **rủi ro** người nhận cần biết (chỗ chưa kiểm, trường hợp biên chưa xử lý).

## Checklist

- [ ] Đã đọc code bị chạm và liệt kê caller/test bị ảnh hưởng
- [ ] Đã đi hết bậc thang, dừng ở bậc đầu tiên đủ dùng
- [ ] Không thêm dependency mới cho vài dòng
- [ ] Không thêm class/abstraction/option "để sau này"
- [ ] Logic mới có nhánh/lặp/tiền/bảo mật → có test
- [ ] Không cắt mục nào trong bảng mục 5
- [ ] Chỗ cắt có chủ ý → có `shortcut:` kèm điều kiện nâng cấp
- [ ] Báo cáo có dòng "đã bỏ qua / rủi ro"

## Nguồn

Ý tưởng lấy từ [Ponytail](https://github.com/DietrichGebert/ponytail) (MIT) — bậc thang YAGNI.
Bản này đã Việt hoá và **chặn 3 xung đột** với quy chuẩn dự án: phạm vi feature do Issue quyết,
yêu cầu mơ hồ thì **hỏi trước** (không tự lấy bản nhỏ nhất), và không được cắt các mục ở mục 5.
