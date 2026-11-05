# `tests/` — Kiểm thử

**Owner:** A và B (mỗi người test phần mình) · **Bắt đầu:** cổng G2 · **Trạng thái:** 🟡 khung trống

## Cấu trúc

```
tests/
├── conftest.py      # fixture: engine, db_session (rollback), client, user auth
├── factories.py     # make_product(), make_order()… tránh copy-paste object
├── test_auth.py
├── test_products.py
├── test_orders.py
├── test_reports.py
└── test_gui_smoke.py
```

## KHÔNG đặt

- Test chạy trên DB dev (`cafe_tlu`) — chỉ dùng `cafe_tlu_test`
- Test gọi mạng thật, `time.sleep`, hoặc phụ thuộc thứ tự chạy
- Ảnh chụp, dữ liệu mẫu nặng

## Quy ước

Đọc skill `pytest-db`. Tên test: `test_<hành_vi>_<điều_kiện>_<kết_quả>`.
Mỗi bug fix **bắt buộc** kèm 1 test tái hiện (đỏ trước, xanh sau).
Chạy: `make test` (hoặc `make check` = lint + test).
