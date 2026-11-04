---
name: ui-design
description: Thiết kế giao diện desktop cho CafeTLU sao cho ra sản phẩm thật, không ra "AI slop". Dùng khi bắt đầu một màn hình mới, khi chỉnh bố cục/màu/font, khi giao diện "trông giống đồ AI làm", hoặc khi được hỏi "làm sao cho đẹp".
---

# Thiết kế UI không bị "AI slop"

## Trước tiên: sản phẩm này KHÔNG phải landing page

Đa số skill "chống AI slop" trên mạng viết cho trang marketing, và khuyên hãy "bold, unforgettable,
phá cách". **Sai hoàn toàn với app này.**

Đây là **POS cho nhân viên quán**: một người dùng 6–8 tiếng/ngày, dưới áp lực, tay ướt, khách đang chờ.

Mục tiêu thẩm mỹ, theo thứ tự: **đọc nhanh → ít bấm nhầm → không mỏi mắt → mới tới "đẹp"**.

Đúng đắn ở đây là **kín đáo, đều, có hệ thống** — không phải nổi bật. Giao diện tốt là giao diện
người dùng không phải nghĩ về nó.

## Những dấu hiệu "AI slop" — cấm tuyệt đối

| ❌ Dấu hiệu | Vì sao bị nhận ra ngay | ✅ Làm thay |
|---|---|---|
| Gradient tím–xanh làm nền | Mặc định của mọi công cụ AI | Nền trung tính ấm: `#FAFAF8` / `#F5F3EF` |
| Emoji làm icon chức năng (`🏠`, `❤️`) | Render khác nhau từng máy, không style được | Bộ icon thật: **QtAwesome** (Font Awesome) hoặc `QStyle.StandardPixmap` |
| Card bo góc + viền accent bên trái | Pattern AI phổ biến nhất | Tiêu đề đậm + mô tả nhạt, phân tách bằng khoảng trắng, không cần card |
| Khối "Welcome to [App]" chiếm màn hình | Lãng phí chỗ đắt nhất | Vào thẳng dữ liệu: bảng món, danh sách đơn |
| Xanh dương mặc định ở mọi nút/toggle/link | Nghĩa là "chưa chọn màu gì" | Một accent duy nhất do nhóm chọn, dùng có chủ đích |
| Spacing lộn xộn 7/13/43px | Trông tuỳ tiện, lệch thị giác | Lưới **8pt**: 4 / 8 / 16 / 24 / 32 |
| 3–4 font trộn lẫn, cỡ chữ nhảy loạn | Không có phân cấp | **1 họ font**, thang cỡ cố định |
| Shadow/bo góc/đổ bóng khắp nơi | Tạo "chiều sâu" giả, nặng máy | Chỉ 1 mức elevation cho popup/dialog |
| Icon + chữ + số liệu cùng độ đậm | Không có điểm nhấn thị giác | Đậm cho số/giá trị, nhạt cho nhãn |
| Đường kẻ bảng dày, kẻ ô toàn bộ | Rối, khó đọc | Chỉ kẻ ngang giữa các dòng, hoặc zebra nhạt |

## Design tokens (khai báo trong `gui/theme.py`)

```python
SPACE = {4: 4, 8: 8, 16: 16, 24: 24, 32: 32}
RADIUS = {"sm": 6, "md": 10}  # chỉ 2 mức
FONT_FAMILY = "Be Vietnam Pro"  # hoặc "Inter"; 1 họ duy nhất, hỗ trợ tiếng Việt
FONT_SIZE = {"caption": 12, "body": 14, "label": 14, "title": 18, "h1": 24}
COLOR = {
    "bg": "#FAF9F6",  # nền ấm, không trắng tuyệt đối
    "surface": "#FFFFFF",
    "border": "#E4E1DA",
    "text": "#1F1D1A",
    "muted": "#6B665E",
    "accent": "#B4530A",  # chọn 1 màu thương hiệu (gợi ý: nâu cà phê)
    "success": "#1E7B45",
    "warning": "#A16207",
    "danger": "#B42318",
}
```

- **Chỉ 1 accent.** Nếu mọi thứ đều accent thì không còn gì là accent.
- Màu ngữ nghĩa (success/warning/danger) **chỉ** dùng cho trạng thái, không dùng trang trí.
- Không dùng màu làm phương tiện thông tin duy nhất (người mù màu) → kèm icon hoặc chữ.

## Bố cục cho app dữ liệu dày

- **Bảng là nhân vật chính.** Cột quan trọng bên trái; số canh phải; tiền dùng số, có phân cách nghìn.
- Chiều cao dòng 36–40px (đủ để bấm, đủ dày để thấy nhiều dòng).
- Căn theo lưới: mọi cạnh trái của tiêu đề, nhãn, giá trị phải thẳng hàng dọc.
- Vùng nội dung rộng rãi, viền màn hình tiết chế: **một** khung chính, không lồng 3 lớp card.
- Thanh công cụ tách khỏi nội dung bằng khoảng trắng + 1 đường kẻ nhạt, không bằng khối màu.
- Trạng thái quan trọng (bàn trống/đang phục vụ) hiển thị bằng **chữ + icon + màu**, không chỉ màu.

## Chữ

- Một họ font cho toàn app. Thang 5 cỡ ở trên, không tự thêm cỡ thứ 6.
- Đậm (`600`) cho tiêu đề mục và **con số**; thường (`400`) cho nội dung; nhạt (`muted`) cho nhãn phụ.
- Không viết hoa toàn bộ câu dài; không in nghiêng để nhấn mạnh.
- Tiếng Việt: kiểm tra dấu ở cỡ 12px — nếu bị bẹt, tăng lên 13–14 hoặc đổi font.

## Icon

- Một bộ duy nhất (QtAwesome). Cùng một ý nghĩa dùng cùng một icon ở mọi màn hình.
- Icon luôn đi kèm chữ ở hành động quan trọng; icon-only thì phải có tooltip.
- Không tự vẽ SVG minh hoạ "người đang làm việc" — nhận ra ngay là đồ AI.

## Trạng thái & phản hồi

- Mọi hành động > 0.3s phải có phản hồi (spinner tại chỗ, không phải dialog chặn).
- Thông báo thành công: toast góc dưới, tự tắt. Lỗi: tại chỗ, không tự tắt, có cách khắc phục.
- Rỗng ≠ Lỗi. Rỗng là "chưa có gì + gợi ý tạo", lỗi là "không tải được + thử lại".

## Tự kiểm: giao diện của bạn có phải AI slop?

Trả lời thật 7 câu:

1. Có gradient tím/xanh nào không?
2. Có emoji nào đang làm chức năng không?
3. Spacing có theo lưới 8pt hay là số tuỳ tiện?
4. Nếu đổi tên quán, giao diện có trông y hệt không? (nếu có → thiếu cá tính)
5. Có khối "chào mừng" nào chiếm chỗ của dữ liệu thật không?
6. Mọi card có cùng bo góc + viền accent trái không?
7. Có màn hình nào chỉ có 1 màu nhấn duy nhất lặp lại ở 5 chỗ khác nhau không?

**≥ 3 câu "có" → làm lại bố cục, đừng chỉ đổi màu.**

## Nguồn tham khảo (đã chắt lọc, không copy)

- Anti-AI-Slop Rules — https://github.com/freekmurze/dotfiles (bản SwiftUI)
- Anthropic frontend-design skill — khuyến nghị "bold" **không** áp dụng cho app này
- The Tells — https://labs.iovstudio.kr/papers/ai-design-tells.pdf
