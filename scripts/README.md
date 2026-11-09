# `scripts/` — Script tiện ích

**Owner:** D · **Bắt đầu:** cổng G1 (build script) / G3 (smoke test) · **Trạng thái:** 🟡 khung trống

## Đặt gì ở đây

| File | Việc |
|---|---|
| `next_task.sh` | In việc tiếp theo của bạn từ Issue được gán (`make next`). Không cần cài gì thêm ngoài `gh` |
| `smoke_test.py` | Chạy luồng chính end-to-end: login → tạo đơn → thanh toán → xem báo cáo. Không có test nào đỏ thì chạy cái này trước khi demo |
| `seed_data.py` | Sinh ~120 đơn trải 30 ngày để biểu đồ có dữ liệu (B dùng) |
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
