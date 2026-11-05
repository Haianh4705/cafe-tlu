# `assets/` — Tài nguyên tĩnh

**Owner:** C · **Bắt đầu:** cổng G1 · **Trạng thái:** 🟡 khung trống

## Đặt gì ở đây

```
assets/
├── brand/      # logo TLU (logo-tlu.png) — tải từ thanglong.edu.vn/logos/standard.png
├── fonts/      # font nhúng vào app (Manrope / Be Vietnam Pro) — có giấy phép
├── products/   # ảnh món, đặt tên slug: tra-dao-cam-sa.jpg
└── icons/      # icon riêng nếu QtAwesome không có
```

## KHÔNG đặt

- Ảnh chụp màn hình của báo cáo (→ `docs/screenshots/`)
- File > 2MB (ảnh món nên nén ≤ 300KB, JPEG chất lượng 80)
- Font có bản quyền không rõ nguồn gốc (font `thangLongSans` của trường **không** được đóng gói)

## Quy ước

Mọi đường dẫn tới `assets/` khi đã đóng gói **phải** đi qua `shared/paths.py::resource_path()`,
nếu không app sẽ không tìm thấy file trên máy người dùng.
Logo: không đổi màu, không bóp méo (skill `ui-design` mục 5).
