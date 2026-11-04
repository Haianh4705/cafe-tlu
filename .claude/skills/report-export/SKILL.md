---
name: report-export
description: Xuất báo cáo thống kê ra Excel/PDF trong CafeTLU. Dùng khi làm "xuất Excel", "in hoá đơn", "báo cáo doanh thu ra PDF", khi file xuất ra bị lỗi dấu tiếng Việt, hoặc khi số liệu trên file không khớp màn hình.
---

# Xuất Excel / PDF

## Hai lỗi chết người (chiếm 90% ca hỏng)

1. **PDF lỗi dấu tiếng Việt** — `reportlab` dùng `Helvetica` mặc định **không có** glyph
   tiếng Việt. Chữ "Trà đào cam sả" thành "Tr? ??o cam s?".
2. **Số liệu lệch giữa màn hình và file** — tính toán hai nơi khác nhau.

## Quy tắc: một nguồn số liệu

Số trong file xuất **phải** lấy từ **cùng một hàm service** mà màn hình đang dùng
(`api/services/reports.py`). Cấm tính lại ở tầng export.

```python
# ĐÚNG
rows = report_service.revenue_by_day(db, from_date, to_date)  # dùng chung
export_excel(rows)

# SAI — tính lại lần 2, sẽ lệch
rows = db.query(Order).filter(...).all()
```

## Excel — `openpyxl`

```python
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

wb = Workbook()
ws = wb.active
ws.title = "Doanh thu"

ws["A1"] = "BÁO CÁO DOANH THU THÁNG 11/2026"
ws["A1"].font = Font(name="Arial", size=14, bold=True)

headers = ["Ngày", "Số đơn", "Doanh thu (đ)"]
for i, h in enumerate(headers, 1):
    c = ws.cell(row=3, column=i, value=h)
    c.font = Font(name="Arial", bold=True, color="FFFFFF")
    c.fill = PatternFill("solid", fgColor="B4530A")
    c.alignment = Alignment(horizontal="center", vertical="center")

MONEY = '#,##0" đ"'
for r, row in enumerate(rows, 4):
    ws.cell(row=r, column=1, value=row.date.strftime("%d/%m/%Y"))
    ws.cell(row=r, column=2, value=row.order_count)
    cell = ws.cell(row=r, column=3, value=row.revenue)
    cell.number_format = MONEY  # KHÔNG tự format chuỗi bằng f-string

ws.freeze_panes = "A4"  # giữ tiêu đề khi cuộn
ws.auto_filter.ref = f"A3:C{3 + len(rows)}"
for i in range(1, 4):
    ws.column_dimensions[get_column_letter(i)].width = 18
```

- Tên sheet tiếng Việt **không dấu**, ≤ 31 ký tự.
- Tổng cộng ở dòng cuối, chữ đậm, có đường kẻ trên.
- Không merge ô lung tung — phá auto_filter và copy/paste của người dùng.

## PDF — `reportlab`

```python
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table

# BẮT BUỘC: nhúng font có bộ dấu tiếng Việt
pdfmetrics.registerFont(TTFont("AppSans", "assets/fonts/BeVietnamPro-Regular.ttf"))
pdfmetrics.registerFont(TTFont("AppSans-Bold", "assets/fonts/BeVietnamPro-Bold.ttf"))

doc = SimpleDocTemplate("report.pdf", pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm)
```

- Font dự phòng tốt: `DejaVuSans`, `Noto Sans`, `Roboto` (bản có Latin Extended).
  **Kiểm tra bằng cách render thử** — nhiều file "hỗ trợ Unicode" vẫn thiếu dấu Việt.
- Canh phải cho cột tiền; dùng `Paragraph` cho ô văn bản dài để tự xuống dòng.
- Hoá đơn: bắt buộc có tên quán, mã đơn, thời gian, từng dòng món (SL × đơn giá), tổng,
  giảm giá, khách đã trả, phương thức thanh toán.

## Định dạng tiền & số

- Tiền VNĐ: `35.000 đ` (dấu chấm phân cách nghìn, hậu tố `đ`).
- `DECIMAL` từ DB → `Decimal`; **không** ép sang `float` (mất chính xác, lệch tổng).
- Tuyệt đối không hiển thị `35000.0`.

## Checklist

- [ ] File mở được bằng Excel/Adobe, không cảnh báo hỏng
- [ ] **Dấu tiếng Việt đúng** trong cả PDF và tên sheet
- [ ] Số liệu khớp 100% với màn hình (so tay ít nhất 1 dòng)
- [ ] Tổng dòng cuối = tổng các dòng trên
- [ ] Cột tiền canh phải, đúng định dạng `#,##0" đ"`
- [ ] Tiêu đề đóng băng / lặp lại khi in nhiều trang
- [ ] Tên file có ngày tạo: `doanh-thu-2026-11-04.xlsx`
- [ ] Thời gian xuất file < 3s với 5.000 dòng (nếu chậm: dùng `write_only=True` của openpyxl)
