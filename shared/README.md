# `shared/` — Dùng chung cho cả api và gui

**Phạm vi:** sửa theo Issue chức năng được giao (`ADR-014`) — dùng chung cho cả `api/` và `gui/`, phải nêu rõ trong PR nếu đổi contract/hằng số chung.

## Đặt gì ở đây

| File | Nội dung |
|---|---|
| `version.py` | `__version__` — **nguồn duy nhất** của số phiên bản (dùng cho app, installer, `/health`) |
| `error_codes.py` | Hằng số mã lỗi `UPPER_SNAKE` — **không đổi mã đã phát hành** |
| `errors.py` | `AppError` + exception handler dùng chung |
| `constants.py` | Hằng số nghiệp vụ (giới hạn trang, trạng thái đơn…) |
| `paths.py` | `resource_path()` — xử lý đường dẫn khi đã đóng gói PyInstaller |

## KHÔNG đặt

- Logic nghiệp vụ (thuộc `api/services/`)
- Code phụ thuộc PySide6 **hoặc** FastAPI — file ở đây phải import được từ cả hai phía

## Quy ước

Chỉ chứa thứ **thuần tuý, không phụ thuộc framework**. Thay đổi ở đây ảnh hưởng cả API và GUI →
phải nêu rõ trong PR và đồng bộ tài liệu `docs/api-contract.md` / GUI liên quan.
