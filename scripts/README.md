# `scripts/` — Script tiện ích

**Phạm vi:** sửa theo Issue chức năng được giao (`ADR-014`) — giữ kiến trúc `gui → api → db`, mỗi script có docstring 2 dòng ở đầu.

## Đặt gì ở đây

| File | Việc |
|---|---|
| `next_task.sh` | In việc tiếp theo của bạn từ Issue được gán (`make next`). Không cần cài gì thêm ngoài `gh` |
| `smoke_test.py` | Smoke test cục bộ bàn → thêm/sửa món → thanh toán; phần báo cáo chờ #95/#96 |
| `seed_data.py` | Sinh ~120 đơn trải 30 ngày để biểu đồ có dữ liệu |
| `build_installer.sh` | Gọi PyInstaller + Inno Setup (CI cũng dùng) |
| `make_icon.py` | Sinh lại `installer/app.ico` từ palette TLU (Pillow) |
| `backup_db.sh` | Backup `.sql.gz` ra ngoài repo (G4) |

## KHÔNG đặt

- Logic nghiệp vụ dùng lại trong app (nếu cần dùng lại → đưa vào `api/services/`)
- Script một lần rồi xoá — nếu đáng giữ thì để đây, không thì đừng commit
- File chứa mật khẩu thật

## Quy ước

Mỗi script có docstring 2 dòng ở đầu: **dùng để làm gì** + **chạy thế nào**.
Phải chạy được từ thư mục gốc repo: `python scripts/smoke_test.py`.

## Smoke test bàn → gọi món → thanh toán (#97)

Phiên bản hiện tại chỉ kiểm `/health`, đăng nhập, bàn trống, thêm/sửa món, tổng tiền server,
checkout và bàn trở về trống. Phần báo cáo chờ #95; nghiệm thu toàn luồng và bộ cài chờ #95/#96.
Script chỉ nhận API local và yêu cầu xác nhận DB dùng tên kết thúc `_test` để tránh ghi vào DB dev.

Chuẩn bị API local trỏ tới một DB test dùng một lần, có schema, tài khoản staff, bàn trống và món còn hàng.
Đặt các biến sau trong terminal trước khi chạy; không lưu mật khẩu vào repo:

```bash
export CAFE_TLU_SMOKE_API_URL=http://127.0.0.1:8000/api/v1
export CAFE_TLU_SMOKE_USER=staff_test
export CAFE_TLU_SMOKE_PASSWORD='mật-khẩu-test'
export CAFE_TLU_SMOKE_TABLE_ID=1
export CAFE_TLU_SMOKE_PRODUCT_ID=1
export CAFE_TLU_SMOKE_DB_NAME=cafe_tlu_test
export CAFE_TLU_SMOKE_ALLOW_WRITES=1
python scripts/smoke_test.py
```

Script tạo đơn và thanh toán thật trên DB test đã xác nhận; nếu lỗi giữa chừng sau khi tạo đơn,
nó in mã đơn để dọn DB test trước khi chạy lại. Không trỏ API tới dữ liệu của quán.
