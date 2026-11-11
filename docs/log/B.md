# Nhật ký — B (Dữ liệu & Báo cáo)

> Quy tắc + mẫu: [`README.md`](README.md). Cập nhật trong PR đã làm việc, không dồn.
> **Người giữ file:** B — @trungdunxg. Người khác không sửa hộ.

**Vùng:** `db/`, `api/services/reports.py`, seed · **Bắt đầu:** G1 (đường găng — A và C đang chờ)

## 1. Tôi phụ trách gì

- Thiết kế ERD + từ điển dữ liệu + bất biến (`docs/erd.md`) và `db/schema.sql` (#17)
- `db/seed.sql` — 50 món, users, bàn (#18); sinh 120 đơn trải 30 ngày (`scripts/seed_data.py`, #28)
- Query thống kê doanh thu + top món + xuất Excel/PDF (`api/services/reports.py`, #31)
- Kiểm dữ liệu mẫu không tự mâu thuẫn (test/smoke, `tests/test_reports.py`)

## 2. Việc đã làm

| Ngày | Issue | PR / commit | File chính | Làm gì (1 câu) | Vì sao cách đó (1 câu) |
|---|---|---|---|---|---|
| 2026-11-11 | #17, #18 | `feature/db-erd-schema-trungdung` | `docs/erd.md`, `db/schema.sql`, `db/seed.sql` | Thiết kế ERD 9 bảng 3NF, viết DDL chuẩn InnoDB/utf8mb4 và nạp 51 món mẫu | Chuẩn hóa 3NF chống dị thường dữ liệu, DECIMAL(12,0) tránh sai số tiền tệ, snapshot giá trong đơn |
| 2026-11-11 | #28, #31 | `feature/db-erd-schema-trungdung` | `scripts/seed_data.py`, `api/services/reports.py`, `tests/test_reports.py` | Sinh 120 đơn 30 ngày, viết ReportService và xuất Excel/PDF | Một nguồn chân lý số liệu, tính toán hoàn toàn bằng SQL GROUP BY, font Unicode cho PDF |

## 3. AI đã làm gì

| Ngày | Công cụ | AI làm gì | Tôi sửa / kiểm chứng gì |
|---|---|---|---|
| 2026-11-11 | Antigravity (Google DeepMind) | Soạn thảo khung Mermaid ERD, tạo danh mục menu 51 món và viết khung ReportService | Rà soát kiểu dữ liệu DECIMAL tiền tệ, kiểm tra ràng buộc ON DELETE, đối soát khớp tổng tiền hoá đơn và kiểm thử hàm xuất file |

## 4. Câu hỏi thầy hay hỏi (vùng B)

> Lấy từ [`defense.md`](../defense.md) mục B.

| # | Câu hỏi | Trả lời ngắn (2–4 câu) | Chỉ vào |
|---|---|---|---|
| 1 | Vì sao chia bảng như vậy? Sao không gộp bớt? | Thiết kế chia 9 bảng đạt chuẩn 3NF để tránh dị thường cập nhật và dư thừa dữ liệu. Tách `categories` khỏi `products` (quan hệ 1-n) và tách `order_items` làm bảng trung gian cho quan hệ n-n giữa `orders` và `products`. Tách riêng `invoices` để bảo đảm tính bất biến của hóa đơn tài chính. | `docs/erd.md:3.1` |
| 2 | Giá món đổi sau khi bán — hoá đơn cũ hiển thị giá nào? | Bảng `order_items` lưu cột snapshot `unit_price` tại đúng thời điểm khách gọi món. Khi quán sửa giá món trong bảng `products`, toàn bộ đơn hàng và hóa đơn phát sinh trước đó vẫn hiển thị đúng giá cũ đã bán. | `db/schema.sql:order_items` |
| 3 | Vì sao tiền là `DECIMAL` không `FLOAT`? | `FLOAT` và `DOUBLE` lưu trữ dưới dạng dấu phẩy động nhị phân (chuẩn IEEE 754), gây sai số làm tròn khi thực hiện các phép cộng dồn doanh thu lớn. `DECIMAL(12,0)` lưu trữ số học chính xác tuyệt đối theo hệ cơ số 10, phù hợp chuẩn tiền tệ VNĐ không có số lẻ. | `db/schema.sql:products` |
| 4 | Index đặt ở đâu, vì sao? | Đặt `INDEX` trên các cột khóa ngoại (`category_id`, `order_id`, `cashier_id`) để tối ưu tốc độ `JOIN`; trên cột tìm kiếm (`products.name`); và trên các cột mốc thời gian (`orders.created_at`, `invoices.paid_at`) để lọc báo cáo doanh thu nhanh hơn. | `db/schema.sql` |
| 5 | Viết query doanh thu theo ngày. | `SELECT DATE(created_at) AS order_date, COUNT(id) AS total_orders, SUM(total_amount) AS revenue FROM orders WHERE status = 'completed' AND is_deleted = 0 GROUP BY DATE(created_at) ORDER BY order_date ASC;` | `api/services/reports.py:27` |
| 6 | Xoá món: xoá cứng hay mềm, vì sao? | Xóa mềm bằng cờ `is_deleted = 1`. Nếu xóa cứng (`DELETE FROM products`), các đơn hàng cũ liên kết khóa ngoại với món đó sẽ bị lỗi ràng buộc toàn vẹn tham chiếu hoặc làm sai lệch lịch sử báo cáo tài chính. | `WORKFLOW.md:8.3`, `db/schema.sql` |
| 7 | Từng khoá ngoại đặt `ON DELETE` gì, vì sao? | `order_items -> orders` đặt `CASCADE` vì chi tiết đơn không thể tồn tại độc lập nếu đơn bị xóa. Ngược lại, `products -> categories` và `orders -> tables` đặt `RESTRICT` để ngăn việc xóa nhầm danh mục/bàn đang có liên kết dữ liệu thực tế. | `db/schema.sql` |
| 8 | Dữ liệu mẫu có tự mâu thuẫn không? Kiểm bằng cách nào? | Dữ liệu mẫu hoàn toàn nhất quán: tổng tiền `orders.total_amount` khớp chính xác tổng `order_items.subtotal`. Tất cả câu lệnh `INSERT` đều dùng `ON DUPLICATE KEY UPDATE` bảo đảm tính idempotent khi chạy lại. | `scripts/seed_data.py`, `db/seed.sql` |
| 9 | N+1 query là gì? Bài có bị không? | N+1 query xảy ra khi truy vấn 1 danh sách N bản ghi cha rồi vòng lặp phát sinh thêm N câu query để lấy thông tin bảng con. Bài khắc phục bằng cách dùng `JOIN` trực tiếp trong SQL báo cáo và cấu hình eager loading (`selectinload` / `joinedload`) trong SQLAlchemy ORM. | `api/services/reports.py` |
| 10 | Số trên báo cáo lấy từ đâu, có thể lệch màn hình không? | Số liệu báo cáo trên giao diện GUI và trong file xuất Excel/PDF đều gọi qua chung một hàm `ReportService.revenue_by_day` trong `api/services/reports.py`, hoàn toàn không thể lệch số liệu. | `api/services/reports.py`, skill `report-export` |

## 5. Chưa làm / chưa hiểu

- [x] `db/schema.sql` + `db/seed.sql` đã hoàn thành và mở mount trong `docker-compose.yml` (hoàn thành bàn giao G1 cho A và D).
- [x] `scripts/seed_data.py`: Sinh ~120 đơn hàng mẫu trải dài 30 ngày (Issue #28) và đã nạp vào `db/seed.sql`.
- [x] `api/services/reports.py`: Triển khai các hàm truy vấn thống kê (doanh thu theo ngày, top món, theo danh mục) và module xuất Excel/PDF (Issue #31).
- [x] `tests/test_reports.py`: Kiểm thử logic thống kê và định dạng file xuất.
- [ ] Tuần 5-6 (G4): Tối ưu hóa chỉ mục (Index) khi đo kiểm tải và viết kịch bản sao lưu định kỳ `scripts/backup_db.sh`.
- [ ] Tuần 7-8: Viết chương CSDL trong báo cáo BTL `report/03-phan-tich.md`.

## 6. Nhật ký theo cổng

| Cổng | Ngày | Đã xong gì | Còn thiếu gì |
|---|---|---|---|
| G1 | 2026-11-11 | ERD hoàn chỉnh (`docs/erd.md`), DDL (`db/schema.sql`), Seed 51 món, 5 users, 12 bàn (`db/seed.sql`), 120 đơn trải 30 ngày (`scripts/seed_data.py`), ReportService (`api/services/reports.py`) | Chờ A tạo models SQLAlchemy và D kiểm thử `make reset-db` trên container |
| G2 | 2026-11-11 | 120 đơn hàng mẫu 30 ngày, ReportService và xuất Excel/PDF sẵn sàng | A nối API endpoints reports, C nối màn hình báo cáo |
| G3 | | | |
