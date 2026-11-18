---
name: ui-design
description: Thiết kế giao diện desktop PySide6 cho CafeTLU theo nhận diện Trường Đại học Thăng Long (navy + đỏ logo), chống "AI slop". Dùng khi dựng màn mới, chỉnh màu/font/bố cục, khi rà soát/đánh bóng (polish/redline) màn hình đã viết, hoặc khi giao diện "trông giống đồ AI làm".
---

# Thiết kế UI theo nhận diện TLU

## 0. Hai điều định hình mọi quyết định

- **Nhận diện Trường Đại học Thăng Long:** màu, logo, kiểu chữ lấy từ nhận diện thật của trường (`thanglong.edu.vn` + logo chính thức), không tự bịa palette hay template SaaS.
- **POS cho nhân viên ngồi 6–8 tiếng:** tay ướt, khách đang chờ. Thứ tự ưu tiên: **đọc nhanh → ít bấm nhầm → không mỏi mắt → mới tới "đẹp"**.

## 1. Bảng màu TLU & Bốn luật cứng (The Floor)

| Token | HEX | Vai trò | Độ tương phản |
|---|---|---|---|
| `navy` | `#000066` | **Màu thương hiệu.** Header, sidebar, nút chính, tiêu đề | 17.6:1 trên trắng — **AAA** |
| `navy_strong` | `#050C56` | Nền sidebar / logo tối hơn | 17.2:1 |
| `navy_600` | `#0624A5` | Hover/active của nút navy | 11.6:1 trên trắng — AAA |
| `brand_400` | `#4C7BFE` | **Chỉ** focus ring, viền active, chỉ báo đồ hoạ | 3.77:1 — **không đạt chữ nhỏ** |
| `tint_100` | `#F1F5FF` | Nền hàng đang chọn, vùng nhấn | 16.2:1 với navy — AAA |
| `tint_200` | `#CCDAFF` | Viền nhấn, badge nhạt | 12.6:1 với navy |
| `red` | `#F32409` | **Swoosh logo.** CHỈ dùng cho xoá, huỷ đơn, cảnh báo nặng | 4.14:1 — **chỉ đạt AA-large** |
| `red_text` | `#B42318` | Chữ lỗi nhỏ (< 18px) | Đạt **AA** (≥ 4.5:1) |
| `ink` / `muted` | `#0C0A09` / `#6B7280` | Chữ chính / nhãn phụ, placeholder | 19.8:1 (AAA) / 4.83:1 (AA) |
| `border` / `surface` / `surface_subtle` | `#E7E5E4` / `#FFFFFF` / `#F9FAFB` | Viền bảng / nền chính / header bảng | — |

1. **Không literal color/font ngoài `gui/theme.py`:** mọi màu, font, spacing, radius lấy từ `COLOR`, `FONT`, `SPACE`, `RADIUS`. Cần màu nền nhạt mới cho badge/banner → thêm token vào `gui/theme.py`, cấm viết `#FEF3F2` trực tiếp trong view/widget.
2. **Navy là hành động, đỏ là nguy hiểm:** "Lưu", "Thanh toán", "Thêm món" → `navy`; "Xoá", "Huỷ đơn" → `red`.
3. **`red` (`#F32409`) cấm dùng cho chữ < 18px:** chữ lỗi nhỏ bắt buộc dùng `red_text` (`#B42318`).
4. **`brand_400` (`#4C7BFE`) cấm làm màu chữ:** chỉ dùng cho focus ring, viền active, chỉ báo đồ hoạ.

## 2. Design tokens — `gui/theme.py`

```python
COLOR = {
    "navy": "#000066",
    "navy_strong": "#050C56",
    "navy_600": "#0624A5",
    "brand_400": "#4C7BFE",
    "tint_100": "#F1F5FF",
    "tint_200": "#CCDAFF",
    "red": "#F32409",
    "red_text": "#B42318",
    "ink": "#0C0A09",
    "muted": "#6B7280",
    "border": "#E7E5E4",
    "surface": "#FFFFFF",
    "surface_subtle": "#F9FAFB",
    "success": "#1E7B45",
    "warning": "#A16207",
}
SPACE = {"xs": 4, "sm": 8, "md": 16, "lg": 24, "xl": 32}  # lưới 8pt
RADIUS = {"sm": 6, "md": 10}  # chỉ 2 mức
FONT = {
    "family": "Manrope",
    "fallback": "Be Vietnam Pro",
    "caption": 12,
    "body": 14,
    "label": 14,
    "title": 18,
    "h1": 24,
}
```

## 3. Kiểu chữ & Câu chữ (Microcopy)

- **Kiểu chữ:** **một họ font** `Manrope` (đóng gói `assets/fonts/Manrope[wght].ttf`; dự phòng `Be Vietnam Pro`, `Inter`, `Segoe UI`; cấm nhúng `thangLongSans` độc quyền). Đúng **5 cỡ** ở trên, độ đậm `400–600`/`bold`, **cấm dùng chữ nghiêng (*italic*) để nhấn mạnh**. Phân cấp bằng cỡ và độ đậm (`muted` cho nhãn, `ink` đậm cho giá trị). Tiền tệ `35.000 đ` canh phải (`DECIMAL`), chữ số thẳng cột.
- **Microcopy tiếng Việt:**
  - **Sentence case** (viết hoa đầu câu): cấm `ALL CAPS` cho nhãn nhỏ, tiêu đề cột, badge (`Tổng thanh toán`, không viết `TỔNG THANH TOÁN`).
  - **Không dấu `!`** ở thông báo thao tác bình thường (*"Đã lưu thay đổi"*, không *"Lưu thành công!"*); **không dấu `.` cuối** ở tiêu đề, nhãn, nút bấm, chú thích ngắn 1 cụm từ.
  - Placeholder ngắn gọn, nêu phím tắt nếu có (*"Tìm tên món (Ctrl+F)"*); không đặt câu chào *"Chào mừng quay lại"*.

## 4. Bố cục, Khung lồng nhau & Biểu đồ

```
┌──────────────────────────────────────────────────────┐
│  [Logo TLU]   CafeTLU            [User] [Đăng xuất]  │  navy #000066, cao 56px
├────────────┬─────────────────────────────────────────┤
│  Sidebar   │  Tiêu đề màn hình (24px, navy)          │
│  220px     │  Thanh công cụ: tìm kiếm / lọc / thêm   │
│  navy      │  ─────────────────────────────────────  │
│            │  Bảng dữ liệu / Khung chính (nền trắng) │
└────────────┴─────────────────────────────────────────┘
```

- **Ngân sách chiều ngang ở `1280×720`:** sau Sidebar `220px` và lề còn `~1028px`. Màn nhiều cột (như POS 3 cột) phải cộng tổng `FixedWidth` trước: cột danh sách món chia lưới 2 cột phải còn **≥ 420px** (hẹp hơn thì giảm về 1 cột) — cấm sinh thanh cuộn ngang hoặc cắt chữ.
- **Tối đa 1 lớp khung viền & Bo góc lồng nhau:** không lồng card trong card; bên trong tách nhóm bằng `SPACE` hoặc đường kẻ ngang `1px`. Phần tử con bo góc nằm trong khung `RADIUS["md"]` (`10px`) dùng `RADIUS["sm"]` (`6px`), không bo bằng hoặc lớn hơn khung ngoài.
- **Bảng & Biểu đồ:** dòng cao `36–40px`, hàng chọn nền `tint_100` (viền trái `2px` `navy`), trạng thái có **chữ + màu**. Dashboard dùng **1 màu nhấn `navy`** trên lưới `border`, nhãn trục `muted` `12px`; cấm cầu vồng nhiều màu trong 1 chuỗi, cấm nhồi sparkline/icon trang trí vào thẻ KPI (chỉ nhãn `muted` + số lớn `ink` + dòng đối chiếu phụ).

## 5. Luật QSS trong PySide6 (chặn rò style & mất nút)

- **Cấm `QFrame { ... }` không có `#objectName`:** trong Qt, `QLabel`, `QTableWidget`, `QScrollArea`, `QTextBrowser` đều kế thừa `QFrame`. Viết `card.setStyleSheet("QFrame { border: ...; padding: 24px; }")` sẽ đóng viền và đội padding lên **mọi `QLabel` con**. Bắt buộc gọi `frame.setObjectName("...")` rồi viết `QFrame#tenKhung { ... }`.
- **Padding của container đặt qua `layout.setContentsMargins(...)`**, không đặt `padding` trong QSS của khung chứa.
- **Override `QPushButton` an toàn:** khi ghi đè QSS cục bộ cho nút, phải khai đủ màu nền và màu chữ cho cả thường, `:hover` và `:disabled` để không sinh lỗi "nút tàng hình" trên Windows/macOS.

## 6. Logo & nhận diện

- File logo chính thức đặt tại `assets/brand/logo-tlu.png` (nền trắng hoặc navy); tối thiểu cao 24px (biểu tượng) / 32px (đầy đủ), khoảng trống quanh logo ≥ chiều cao chữ "T".
- **Không** đổi màu, bóp méo tỉ lệ, thêm shadow/bo góc hay dùng làm watermark mờ sau bảng dữ liệu. Ghi rõ trong About/README: *"Đồ án học phần Python — không phải sản phẩm chính thức của TLU"*.

## 7. Cấm — dấu hiệu "AI slop"

| ❌ | Vì sao | ✅ |
|---|---|---|
| Gradient tím–xanh, bóng phát sáng | Mặc định AI | Nền `surface` trắng, header navy đặc |
| Emoji làm icon chức năng | Render lệch giữa OS | `QtAwesome` hoặc `QStyle.StandardPixmap`, màu navy |
| `QFrame { ... }` trần hoặc card lồng card | Viền/padding rò xuống `QLabel` | `QFrame#objectName` + tối đa 1 lớp khung |
| `ALL CAPS` nhãn nhỏ, dấu `!` tràn lan | Khó đọc dấu tiếng Việt, văn mẫu | Sentence case, câu phẳng không `!` |
| Biểu đồ cầu vồng, KPI nhồi mini-chart | Nhiễu mắt khi trực quầy 6–8h | 1 màu nhấn `navy`, thẻ KPI chỉ số + nhãn |
| Spacing tuỳ tiện (`7/13/43px`), trộn nhiều font | Lệch lưới | Lưới 8pt (`4/8/16/24/32`), 1 họ font 5 cỡ |

## 8. Đánh bóng màn hình có sẵn (Polish Pass — G3→G4)

1. **Audit trước, chưa sửa code:** mở/chụp màn ở `1280×720`, liệt kê lỗi kèm `file:dòng`. Màn đã đúng bố cục chỉ sửa điểm lỗi (*Polish mode*), không đập lại layout.
2. **Khoá phần tử giữ nguyên (`kept`):** liệt kê các nút, ô nhập, phím tắt, signal đang có; sửa xong không được mất hay vô hiệu hoá nhầm mục nào.
3. **Đi 5 lượt theo thứ tự:** `Khoảng cách & căn cột (8pt)` → `Selector QSS (#objectName) & token màu` → `Kiểu chữ & câu chữ (i18n)` → `Bo góc, bảng & biểu đồ` → `Kiểm tràn ở 1280×720`.

## 9. Tự kiểm trước khi báo xong

1. Đủ chất TLU (`navy`, logo, `Manrope`) và **0** gradient tím, emoji icon, khối "Chào mừng"?
2. Nút chính `navy`, hành động phá huỷ `red`; không có `#hex` viết tay ngoài `gui/theme.py`?
3. Không có `QFrame {` thiếu `#objectName` hay container đặt `padding` trong QSS?
4. Chữ lỗi nhỏ dùng `red_text`, không `ALL CAPS` nhãn nhỏ, không italic, không `!` thừa?
5. Mở ở `1280×720` không tràn ngang, không cắt chữ, còn nguyên đủ nút/signal (`kept`)?

## 10. Nguồn

- Nhận diện TLU: <https://thanglong.edu.vn/vi> (`--color-brand-*`, `/logos/standard.png`) và WCAG 2.1 AA.
- Chống AI slop: [anti-ai-slop rules](https://github.com/freekmurze/dotfiles/blob/fe89482ce432f76e750885c4cdb29f88155c4cb7/config/claude/skills/swiftui-design/references/anti-ai-slop.md), [The Tells](https://labs.iovstudio.kr/papers/ai-design-tells.pdf).
- Quy trình Polish Pass theo lượt & micro-craft cho app/dashboard chuyển thể từ [unslop](https://github.com/heydamir/unslop) của Damir Sokolovsky (`@heydamir`, CC BY 4.0).
- Cơ chế luật cứng (Floor) & bảo toàn phần tử (`kept`) tham khảo từ [Hallmark](https://github.com/nutlope/hallmark) của Together AI (MIT).
