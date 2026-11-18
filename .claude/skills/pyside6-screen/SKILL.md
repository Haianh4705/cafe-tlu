---
name: pyside6-screen
description: Tạo hoặc sửa một màn hình PySide6 trong gui/ của CafeTLU. Dùng khi được giao "làm màn hình X", "thêm form", "sửa giao diện", hoặc khi UI bị treo, lệch theme, rò QSS, mất nút, thiếu trạng thái rỗng/lỗi.
---

# Màn hình PySide6

## Bất biến kiến trúc

- `gui/` **không** import `api.*`, **không** kết nối DB. Mọi dữ liệu qua `gui/api_client.py`.
- Màu / font / spacing / radius **chỉ** khai báo trong `gui/theme.py`. Cấm hardcode `#hex` hay `setStyleSheet("color:#ff0000")` trong view/widget.
- Chuỗi hiển thị **chỉ** trong `gui/i18n.py` qua hàm `t()`.
- Mọi lời gọi HTTP chạy trên **luồng nền** (`self.start_worker(...)`) — **kể cả `logout` và `delete`**; cấm gọi HTTP đồng bộ trên luồng UI.
- Mọi `QFrame` có `setStyleSheet` bắt buộc đặt `setObjectName(...)` và viết `QFrame#tenKhung` (tránh rò viền/padding xuống `QLabel` con).

## Cấu trúc màn hình

```python
# gui/views/product_list_view.py
class ProductListView(BaseView):
    def load(self) -> None:  # gọi khi mở màn hình
        self._set_state(self.STATE_LOADING)
        self.start_worker(
            self.api.get_products,
            on_success=self._on_data,
            on_error=self._on_error,
            search=self._search_text,
        )

    def refresh(self) -> None: ...  # F5
    def on_close(self) -> None: ...  # BaseView tự dừng các worker đang chạy
```

## 4 trạng thái bắt buộc & Giữ bộ lọc

| Trạng thái | Hiển thị |
|---|---|
| `loading` | Spinner/progress + chặn thao tác lặp |
| `empty` | Câu giải thích + hành động gợi ý (`Chưa có món nào` / `Xoá bộ lọc`) |
| `error` | Thông điệp từ `ApiClientError.message` + nút `Thử lại` |
| `data` | Nội dung thật |

- **Phân biệt DB rỗng và lọc/tìm kiếm rỗng:** khi tìm không khớp, **không** được ẩn mất thanh tìm kiếm/bộ lọc (đặt thanh lọc ngoài khung `empty` hoặc có nút *"Xoá bộ lọc"* ngay trong `empty`).
- Khi xoá dòng cuối cùng ở `page > 1`, tự lùi về trang hợp lệ gần nhất để không kẹt ở trang trống.

## Form Dialog & Xử lý lỗi ghi

- Validate tại chỗ trước khi gửi: bắt buộc nhập, độ dài, giá > 0.
- **Không đóng dialog trước khi API xác nhận thành công.** Khi bấm Lưu → khoá nút submit (`Đang lưu...`) + chạy `ApiWorker`: thành công mới `accept()` và tải lại bảng; thất bại (`409`, mất mạng…) thì mở lại nút, hiện `ApiClientError.message` inline ngay trên form (không bật `QMessageBox`) và **giữ nguyên dữ liệu người dùng vừa nhập**.
- Riêng `logout`: dù API hoặc mạng lỗi vẫn **phải** xoá token cục bộ và đưa về màn Đăng nhập.
- Thao tác phá huỷ (xoá, huỷ đơn) **phải** có hộp thoại xác nhận, nêu rõ đối tượng; không disable nút `Lưu` mà không có gợi ý lý do.

## Phím tắt & khả dụng

- `Ctrl+F` tìm kiếm · `F5` refresh · `Ctrl+S` lưu · `Esc` đóng dialog · `Enter` submit form.
- Bảng: double-click để sửa, `Delete` để xoá (có xác nhận); focus ring rõ ràng, thứ tự Tab hợp lý.

## Kiểm chứng tự động trước khi mở PR (Floor Check)

1. Chạy lệnh kiểm tự động token màu và `QFrame#objectName` trên các file vừa sửa (hoặc toàn `gui/`):

```bash
.venv/bin/python -c '
import ast, pathlib, re, sys
paths = [pathlib.Path(a) for a in sys.argv[1:]] or sorted(pathlib.Path("gui").rglob("*.py"))
bad = []
for p in paths:
    txt = p.read_text(encoding="utf-8")
    tree = ast.parse(txt)
    doc_end = (
        tree.body[0].end_lineno
        if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Constant)
        else 0
    )
    for i, line in enumerate(txt.splitlines(), 1):
        if i <= doc_end or line.lstrip().startswith("#"):
            continue
        if p.name != "theme.py":
            for m in re.finditer(r"#[0-9A-Fa-f]{6}\b", line):
                bad.append(f"{p}:{i}: hardcode màu {m.group()}")
        if re.search(r"QFrame\s*\{", line):
            bad.append(f"{p}:{i}: QFrame thiếu #objectName")
print("\n".join(bad) or "Floor QSS OK"); sys.exit(bool(bad))
' gui/views/<file_vừa_sửa>.py
```

2. Test resize ở `1280×720`, `1600×900`, `1920×1080`: không tràn ngang (`horizontalScrollBar().maximum() == 0` với lưới/vùng chính), không cắt chữ, cột bảng co giãn hợp lý.
3. Chụp ảnh màn hình → `docs/screenshots/<module>/<mô-tả>-<YYYYMMDD>-01.png` (chỉ khi hoàn thiện/đổi màn hình) và cập nhật `docs/test-cases.md`.

## Checklist

- [ ] Kế thừa `BaseView`, có `load` / `refresh` / `on_close`
- [ ] Chỉ dùng token trong `gui/theme.py`, mọi `QFrame` có style đều đặt `#objectName`, pass Floor QSS
- [ ] Chuỗi qua `gui/i18n.py`, đúng microcopy tiếng Việt
- [ ] Đủ 4 trạng thái; tìm kiếm rỗng giữ được bộ lọc; xoá món cuối trang lùi trang hợp lệ
- [ ] Mọi HTTP (`logout`, `delete`, lưu form) chạy qua `start_worker`; lỗi ghi giữ nguyên input trên form
- [ ] Có validate + xác nhận thao tác phá huỷ; khi đánh bóng UI còn nguyên nút/signal cũ (`kept`)
- [ ] Đã test 3 kích thước (`1280×720` không tràn ngang), chụp ảnh (nếu đổi màn hình) và điền test case

## Liên quan

Thiết kế thẩm mỹ, nhận diện TLU, luật QSS và quy trình Polish Pass: đọc skill **`ui-design`** trước khi bắt đầu bố cục.
