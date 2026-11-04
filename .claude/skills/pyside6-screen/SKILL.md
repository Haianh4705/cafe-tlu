---
name: pyside6-screen
description: Tạo hoặc sửa một màn hình PySide6 trong gui/ của CafeTLU. Dùng khi được giao "làm màn hình X", "thêm form", "sửa giao diện", hoặc khi UI bị treo, lệch theme, thiếu trạng thái rỗng/lỗi.
---

# Màn hình PySide6

## Bất biến kiến trúc

- `gui/` **không** import `api.models`, **không** kết nối DB. Mọi dữ liệu qua `gui/api_client.py`.
- Màu / font / spacing **chỉ** khai báo trong `gui/theme.py`. Cấm `setStyleSheet("color:#ff0000")` trong view.
- Chuỗi hiển thị **chỉ** trong `gui/i18n.py`.
- Mọi lời gọi HTTP chạy trên **luồng nền** — cấm gọi đồng bộ trên luồng UI.

## Cấu trúc màn hình

```python
# gui/views/product_list_view.py
class ProductListView(BaseView):
    def load(self) -> None:  # gọi khi mở màn hình
        self._set_state("loading")
        self._worker = ApiWorker(self.api.get_products, search=self._search_text)
        self._worker.succeeded.connect(self._on_data)
        self._worker.failed.connect(self._on_error)
        self._worker.start()

    def refresh(self) -> None: ...  # F5
    def on_close(self) -> None: ...  # huỷ worker đang chạy
```

## 4 trạng thái bắt buộc

Mỗi màn hình phải có đủ, không được bỏ trạng thái nào:

| Trạng thái | Hiển thị |
|---|---|
| `loading` | Skeleton hoặc spinner + chặn thao tác lặp |
| `empty` | Câu giải thích + hành động gợi ý ("Chưa có món nào — Thêm món") |
| `error` | Thông điệp từ `error.code` + nút "Thử lại" |
| `data` | Nội dung thật |

## Validate trước khi gửi

- Bắt buộc nhập, độ dài, giá > 0, không trùng tên (nếu trùng do server trả về thì hiển thị
  lỗi ngay tại trường, không bật messagebox).
- Thao tác phá huỷ (xoá, huỷ đơn) **phải** có hộp thoại xác nhận, nêu rõ đối tượng.
- Không disable nút "Lưu" mà không nói lý do — nếu disable, phải có gợi ý.

## Phím tắt & khả dụng

- `Ctrl+F` tìm kiếm · `F5` refresh · `Ctrl+S` lưu · `Esc` đóng dialog · `Enter` submit form.
- Bảng: double-click để sửa, `Delete` để xoá (có xác nhận).
- Focus ring phải nhìn thấy rõ; thứ tự Tab hợp lý.

## Sau khi xong

- Chụp ảnh màn hình → `docs/screenshots/<module>/<mô-tả>-<YYYYMMDD>-01.png`.
- Test resize 1280×720, 1600×900, full HD: không tràn, không cắt chữ, cột bảng co giãn hợp lý.
- Cập nhật dòng tương ứng trong `docs/test-cases.md`.

## Checklist

- [ ] Kế thừa `BaseView`, có `load/refresh/on_close`
- [ ] Chỉ dùng token trong `theme.py`, không hardcode màu/font
- [ ] Chuỗi qua `i18n.py`, tiếng Việt có dấu hiển thị đúng
- [ ] Đủ 4 trạng thái
- [ ] HTTP trên worker, UI không treo khi chờ
- [ ] Có validate + xác nhận thao tác phá huỷ
- [ ] Có ảnh chụp + test case đã điền
- [ ] Đã test 3 kích thước cửa sổ

## Liên quan

Thiết kế thẩm mỹ (màu, chữ, khoảng cách, chống "AI slop"): đọc skill **`ui-design`** trước khi bắt đầu bố cục.
