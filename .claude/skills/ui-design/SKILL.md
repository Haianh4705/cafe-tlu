---
name: ui-design
description: Thiết kế giao diện desktop cho CafeTLU theo nhận diện thương hiệu Trường Đại học Thăng Long (navy + đỏ logo), tránh "AI slop". Dùng khi bắt đầu màn hình mới, khi chỉnh màu/font/bố cục, khi giao diện "trông giống đồ AI làm", hoặc khi được hỏi "làm sao cho đẹp".
---

# Thiết kế UI theo nhận diện TLU

## 0. Hai điều định hình mọi quyết định

**Thứ nhất — đây là app của Trường Đại học Thăng Long.** Nhìn vào phải nhận ra TLU, không phải
một template SaaS. Màu, logo, kiểu chữ lấy từ nhận diện thật của trường
(`thanglong.edu.vn` + file logo chính thức), không tự bịa palette.

**Thứ hai — đây là POS cho nhân viên quán**, không phải landing page. Người dùng ngồi 6–8 tiếng,
tay ướt, khách đang chờ. Thứ tự ưu tiên: **đọc nhanh → ít bấm nhầm → không mỏi mắt → mới tới "đẹp"**.

Nhiều skill "chống AI slop" trên mạng khuyên hãy *bold, unforgettable, phá cách*. **Sai ngữ cảnh.**
Đúng đắn ở đây là kín đáo, đều, có hệ thống — nhưng **đúng chất TLU**.

## 1. Bảng màu TLU

Nguồn: token CSS của `thanglong.edu.vn` (OKLCH, đã quy đổi sang HEX) + màu lấy trực tiếp từ file logo.

| Token | HEX | Vai trò | Độ tương phản |
|---|---|---|---|
| `navy` | `#000066` | **Màu thương hiệu.** Header, sidebar, nút chính, tiêu đề màn hình | 17.6:1 trên trắng — **AAA** |
| `navy-strong` | `#050C56` | Màu navy của logo, dùng khi cần nền tối hơn | 17.2:1 |
| `navy-600` | `#0624A5` | Hover/active của nút navy | 11.6:1 trên trắng — AAA |
| `brand-400` | `#4C7BFE` | **Chỉ** focus ring, viền trạng thái active, chỉ báo | 3.77:1 — đạt cho **đồ hoạ, không đạt cho chữ nhỏ** |
| `tint-100` | `#F1F5FF` | Nền hàng đang chọn, nền vùng nhấn | 16.2:1 với navy — AAA |
| `tint-200` | `#CCDAFF` | Viền nhấn, badge nhạt | 12.6:1 với navy |
| `red-logo` | `#F32409` | **Màu swoosh trong logo.** CHỈ dùng cho: xoá, huỷ đơn, lỗi, cảnh báo nặng | 4.14:1 — **chỉ đạt AA-large** |
| `ink` | `#0C0A09` | Chữ nội dung chính | 19.8:1 — AAA |
| `muted` | `#6B7280` | Nhãn phụ, mô tả, placeholder | 4.83:1 — AA |
| `border` | `#E7E5E4` | Đường kẻ, viền bảng | — |
| `surface` | `#FFFFFF` | Nền nội dung | — |

### Ba luật cứng về màu

1. **Navy là màu hành động, đỏ là màu nguy hiểm.** Nút "Lưu", "Thanh toán", "Thêm món" → **navy**.
   Nút "Xoá", "Huỷ đơn" → **đỏ logo**. Tuyệt đối không dùng đỏ cho nút chính — vừa sai ngữ nghĩa,
   vừa chỉ đạt AA-large.
2. **`red-logo` không dùng cho chữ nhỏ hơn 18px.** 4.14:1 chỉ đạt chuẩn cho chữ lớn/đậm hoặc icon.
   Nếu cần chữ đỏ nhỏ (ví dụ thông báo lỗi dưới ô nhập), dùng `#B42318` (đậm hơn, đạt AA).
3. **`brand-400` không dùng làm màu chữ.** Chỉ viền/ring/đồ hoạ.

## 2. Design tokens — copy vào `gui/theme.py`

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

## 3. Kiểu chữ

- Trường dùng font **`thangLongSans`** (độc quyền, không có trên Google Fonts, **không được đóng gói
  vào app**). Bản thay thế gần nhất và có dấu tiếng Việt tốt: **Manrope**, dự phòng
  **Be Vietnam Pro** rồi **Inter**.
- **Một họ font** cho toàn app. Thang 5 cỡ ở trên, không tự thêm cỡ thứ 6.
- Nhãn (label) chữ thường `muted`; **giá trị và con số** đậm `ink` — phân cấp bằng độ đậm,
  không bằng màu.
- Số tiền: `35.000 đ`, canh phải, dùng `DECIMAL` chứ không `float`.

## 4. Bố cục chuẩn của app

```
┌──────────────────────────────────────────────────────┐
│  [Logo TLU]   CafeTLU            [User] [Đăng xuất]  │  navy #000066, cao 56px
├────────────┬─────────────────────────────────────────┤
│  Sidebar   │  Tiêu đề màn hình (24px, navy)          │
│  navy      │  Thanh công cụ: tìm kiếm / lọc / thêm   │
│  #000066   │  ─────────────────────────────────────  │
│            │  Bảng dữ liệu (nền trắng)               │
└────────────┴─────────────────────────────────────────┘
```

- **Header và sidebar màu navy, nội dung màu trắng.** Tương phản mạnh, đúng nhận diện, và mắt
  nhân viên luôn biết đâu là "vùng làm việc".
- Hàng đang chọn: nền `tint_100`, viền trái 2px `navy` — không đổi màu chữ.
- Vùng nội dung: **một** khung chính, không lồng 3 lớp card.
- Chiều cao dòng bảng 36–40px; kẻ ngang nhạt giữa các dòng, không kẻ ô toàn bộ.
- Trạng thái bàn/món: **chữ + icon + màu**, không chỉ màu (người mù màu vẫn phải đọc được).

## 5. Logo & nhận diện

- Dùng file logo chính thức của trường, đặt tại `assets/brand/logo-tlu.png`
  (tải từ `thanglong.edu.vn/logos/standard.png`), nền **trắng hoặc navy**.
- **Không** đổi màu, không bóp méo tỉ lệ, không thêm hiệu ứng/shadow/bo góc cho logo.
- Giữ khoảng trống quanh logo ≥ chiều cao chữ "T" trong biểu tượng.
- Kích thước tối thiểu: cao 24px (chỉ biểu tượng), 32px (logo đầy đủ).
- Không dùng logo làm nền mờ (watermark) phía sau bảng dữ liệu.
- Đây là đồ án học tập: **không** ngụ ý app là sản phẩm chính thức của trường. Ghi rõ trong
  About/README: "Đồ án học phần Python — không phải sản phẩm chính thức của TLU".

## 6. Cấm — dấu hiệu "AI slop"

| ❌ | Vì sao | ✅ |
|---|---|---|
| Gradient tím–xanh làm nền | Mặc định của mọi công cụ AI | Nền `surface` trắng, header navy đặc |
| Emoji làm icon chức năng | Render khác nhau, không style được | **QtAwesome** hoặc `QStyle.StandardPixmap`, màu navy |
| Card bo góc + viền accent trái | Pattern AI phổ biến nhất | Tiêu đề đậm + nhãn nhạt, phân tách bằng khoảng trắng |
| Khối "Welcome to CafeTLU" chiếm màn hình | Lãng phí chỗ đắt nhất | Vào thẳng dữ liệu: bảng món, danh sách đơn |
| Xanh dương mặc định của Qt ở mọi nút | Nghĩa là "chưa chọn màu gì" | Navy `#000066` theo token |
| Đỏ cho nút "Lưu" | Sai ngữ nghĩa + chỉ đạt AA-large | Đỏ **chỉ** cho hành động phá huỷ |
| Spacing 7/13/43px tuỳ tiện | Lệch thị giác | Lưới 8pt: 4/8/16/24/32 |
| 3–4 font trộn lẫn | Không có phân cấp | 1 họ font, 5 cỡ |
| Icon tự vẽ "người đang làm việc" | Nhận ra ngay là đồ AI | Icon bộ chuẩn, hoặc không dùng ảnh minh hoạ |

## 7. Tự kiểm trước khi báo xong

1. Nhìn vào có nhận ra **TLU** không? (navy + logo + kiểu chữ)
2. Có gradient tím/xanh, emoji làm icon, hay khối "chào mừng" nào không?
3. Nút chính có dùng **navy** không? Có chỗ nào dùng đỏ cho hành động không phá huỷ không?
4. Chữ đỏ có nhỏ hơn 18px không? (nếu có → đổi `#B42318`)
5. Khoảng cách có theo lưới 8pt? Có cỡ chữ nào ngoài thang 5 cỡ?
6. Đổi tên quán đi, giao diện còn trông "của trường" không?
7. Chụp ảnh ở 1280×720 — có chỗ nào chữ bị cắt, cột bị tràn?

**≥ 3 câu trả lời "không ổn" → làm lại bố cục, đừng chỉ đổi màu.**

## 8. Nguồn

- Nhận diện TLU: <https://thanglong.edu.vn/vi> — token CSS `--color-brand-*` (OKLCH → HEX)
  và file logo chính thức `/logos/standard.png`
- Chống AI slop: [anti-ai-slop rules](https://github.com/freekmurze/dotfiles/blob/fe89482ce432f76e750885c4cdb29f88155c4cb7/config/claude/skills/swiftui-design/references/anti-ai-slop.md),
  [The Tells](https://labs.iovstudio.kr/papers/ai-design-tells.pdf)
- Ngưỡng tương phản: WCAG 2.1 AA (4.5:1 cho chữ thường, 3:1 cho chữ lớn/đồ hoạ)
