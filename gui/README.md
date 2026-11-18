# `gui/` — Giao diện desktop PySide6

**Phạm vi:** sửa theo Issue chức năng được giao (`ADR-014`) — đọc skill `pyside6-screen` + `ui-design` trước khi sửa, giữ kiến trúc `gui → api → db`.

## Cấu trúc

```
gui/
├── main.py          # khởi tạo QApplication, nạp theme, mở cửa sổ chính
├── api_client.py    # LỚP DUY NHẤT gọi HTTP tới api/
├── theme.py         # màu, font, spacing — token từ skill ui-design
├── i18n.py          # TOÀN BỘ chuỗi tiếng Việt
├── views/           # mỗi màn hình 1 file, kế thừa BaseView
└── widgets/         # component dùng lại (bảng, form, dialog xác nhận)
```

## KHÔNG đặt

- `import` từ `api.models`, kết nối MySQL trực tiếp
- Màu/font hardcode trong view (phải qua `theme.py`)
- Chuỗi hiển thị viết thẳng trong view (phải qua `i18n.py`)

## Quy ước

Đọc skill `pyside6-screen` **và** `ui-design` (palette navy TLU). Mọi HTTP chạy trên luồng nền.
Mỗi màn hình đủ 4 trạng thái: loading / empty / error / data. Xong màn hình → chụp ảnh vào
`docs/screenshots/<module>/`. Kiểm tra: `make gui`.
