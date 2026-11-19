# Danh sách ca kiểm thử (test cases)

> Bảng này là **minh chứng cho báo cáo** (mốc 8: "chụp ảnh các bước đầy đủ") và là
> đầu vào cho cổng **G5**. Cập nhật ngay khi làm xong tính năng, đừng dồn tuần cuối.
>
> Quy ước: **C** = C (GUI) viết, **D** = D kiểm chứng lại trên máy sạch.
> Kết quả: `PASS` / `FAIL` / `BLOCKED` (kèm số Issue nếu FAIL).

## G2 — Luồng E2E trên máy thành viên khác

| ID | Bước đã xác nhận | Kết quả | Ghi chú |
|---|---|---|---|
| TC-G2-E2E-01 | Đăng nhập qua GUI | PASS | Chủ dự án xác nhận ngày 19-11-2026: luồng chạy trên máy thành viên khác qua API + MySQL thật. Ảnh toàn cửa sổ vẫn cần nộp; lần miễn ảnh ngày 20-11 đã được thu hồi. |
| TC-G2-E2E-02 | Thêm món qua GUI/API | PASS | Chủ dự án xác nhận cùng lần E2E; ảnh trạng thái món mới trong danh sách còn chờ D kiểm tra và lưu. |
| TC-G2-E2E-03 | Tìm món qua GUI/API | PASS | Chủ dự án xác nhận cùng lần E2E; ảnh kết quả tìm chính xác món test còn chờ D kiểm tra và lưu. Không thay thế TC-SRC-01/02/03. |
| TC-G2-E2E-04 | Sửa món qua GUI/API | PASS | Chủ dự án xác nhận cùng lần E2E; ảnh giá/tên sau sửa còn chờ D kiểm tra và lưu. |
| TC-G2-E2E-05 | Xoá món qua GUI/API | PASS | Chủ dự án xác nhận cùng lần E2E; ảnh kết quả sau xoá còn chờ D kiểm tra và lưu. |

> Nguồn ghi nhận: xác nhận của chủ dự án trên Issue #34 ngày 19-11-2026. Chủ dự án từng miễn ảnh ngày
> 20-11-2026 nhưng sau đó khôi phục yêu cầu ảnh nghiệm thu; D phải kiểm tra ảnh toàn cửa sổ, chiều ngang
> ≥1280px, dữ liệu thật và lưu vào `docs/screenshots/product/`. Các PASS ghi nhận lời xác nhận E2E,
> chưa thay thế việc D kiểm tra và lưu bộ ảnh.

## 1. Xác thực & phân quyền

| ID | Tiền điều kiện | Bước | Kết quả mong đợi | Người | Kết quả | Ghi chú |
|---|---|---|---|---|---|---|
| TC-AUTH-01 | Có user `admin` | Đăng nhập đúng mật khẩu | Vào được Dashboard, menu đầy đủ | C | PASS | E2E 18-11: admin vào Dashboard, `/auth/me` trả 200 và menu đủ 5 mục. Nội dung Tổng quan báo lỗi riêng vì `GET /reports/revenue` trả 404; không thuộc màn đăng nhập. |
| TC-AUTH-02 | Có user `admin` | Đăng nhập sai mật khẩu 3 lần | Báo lỗi rõ ràng, không lộ "sai user hay sai pass" | C | PASS | E2E 18-11: sai mật khẩu 3 lần và user không tồn tại đều hiện cùng lỗi inline `Tên đăng nhập hoặc mật khẩu không đúng`; không có messagebox. Ảnh `docs/screenshots/gui/login-20261118-02.png`. |
| TC-AUTH-03 | Có user `thungan01` role `staff` | Đăng nhập role `staff` | Không thấy menu Quản lý thực đơn / Báo cáo doanh thu | C | PASS | E2E 18-11: `/auth/me` trả 200; staff chỉ thấy Tổng quan, Bán hàng / Order, Quản lý bàn. |
| TC-AUTH-04 | Role `staff` | Gọi trực tiếp API admin bằng token staff | 403 `FORBIDDEN` (chặn ở server) | D | PASS | Kiểm bằng API test có DB fixture: `test_create_category_staff_forbidden`, `test_delete_product_staff_forbidden`; suite local `DB_NAME=cafe_tlu_test make test` đạt 142 passed. |
| TC-AUTH-05 | Đã đăng nhập | Đóng app, mở lại | Quay về form đăng nhập; token chỉ lưu trong RAM | C | PASS | E2E 18-11: sau khi đóng và chạy lại `make gui`, app trở về form trống, không khôi phục phiên cũ. |

## 2. Quản lý món ăn / đồ uống (CRUD)

| ID | Tiền điều kiện | Bước | Kết quả mong đợi | Người | Kết quả | Ghi chú |
|---|---|---|---|---|---|---|
| TC-PRD-01 | Role admin | Thêm món mới đủ trường | Lưu thành công, hiện ngay trong danh sách | C | PASS | Chủ dự án xác nhận đã thêm món trong E2E trên máy thành viên khác qua API + MySQL thật (19-11-2026). |
| TC-PRD-02 | | Thêm món trùng tên | Báo `PRODUCT_NAME_DUPLICATED`, không tạo bản ghi | C | PASS | MySQL API test `test_create_product_admin_and_duplicate_name`: tạo lần hai trả 409 `PRODUCT_NAME_DUPLICATED`; suite mục tiêu 12 passed (20-11-2026). |
| TC-PRD-03 | | Nhập giá âm hoặc chữ | Chặn ở form, không gửi lên server | C | PASS | GUI test `test_product_form_rejects_non_positive_price_before_submit`: QSpinBox chặn số âm ở 0, validate báo lỗi và không submit (20-11-2026). |
| TC-PRD-04 | | Sửa giá món đang có đơn | Món trong đơn cũ **giữ giá cũ** | D | PASS | MySQL API test `test_product_price_snapshot_and_order_history_survive_soft_delete`: dòng đơn giữ giá 25.000 sau khi giá món đổi lên 35.000; tổng 50.000 (20-11-2026). |
| TC-PRD-05 | | Xoá món | Xoá mềm; món biến khỏi danh sách nhưng hoá đơn cũ vẫn xem được | D | BLOCKED | Test MySQL xác nhận soft delete, GET đơn cũ giữ tên/giá món và Invoice còn lưu trong DB. GUI hiện chỉ mở ReceiptDialog ngay sau checkout; sau khi đóng không có màn/route để truy xuất và mở lại hoá đơn hoàn tất. Chờ D/chủ dự án chốt “xem được” chỉ yêu cầu dữ liệu còn lưu hay cần thêm hành vi mở lại từ GUI; chưa sửa ngoài phạm vi trước khi chốt. |

## 3. Tìm kiếm & lọc

| ID | Tiền điều kiện | Bước | Kết quả mong đợi | Người | Kết quả | Ghi chú |
|---|---|---|---|---|---|---|
| TC-SRC-01 | 5.000 món | Gõ "trà" vào ô tìm kiếm | Kết quả < 300ms, đúng chuỗi | D | PASS | MySQL test benchmark với 5.000 món (100 khớp): API query 12,2ms, render QTableWidget 20 dòng 4,3ms, tổng 16,5ms; tất cả kết quả đúng chuỗi. Đo in-process, chưa gồm HTTP qua socket/worker và thao tác gõ thật (20-11-2026). |
| TC-SRC-02 | | Lọc theo danh mục + khoảng giá | Kết quả đúng cả 2 điều kiện; giá thoả `min <= price <= max` (khoảng đóng) | C | BLOCKED | Chủ dự án chuyển ca này sang G3 ngày 19-11-2026. GUI/API hiện chưa hỗ trợ lọc khoảng giá; chỉ kiểm ca sau khi feature G3 được triển khai. Không chặn nghiệm thu G2. |
| TC-SRC-03 | | Tìm chuỗi không tồn tại | Hiện trạng thái "không có kết quả", không bảng trống trơ | C | PASS | `test_product_list_view_empty_state_on_search_not_found` xác nhận trạng thái rỗng có thông báo và hành động xoá lọc (MySQL suite mục tiêu, 20-11-2026). |

## 4. Order & thanh toán

| ID | Tiền điều kiện | Bước | Kết quả mong đợi | Người | Kết quả | Ghi chú |
|---|---|---|---|---|---|---|
| TC-ORD-01 | Bàn trống | Tạo đơn 3 món | Đơn lưu DB, tổng tiền đúng | C | ⬜ | Chờ API #22/#29 |
| TC-ORD-02 | | Xoá 1 món khỏi đơn | Tổng tiền tính lại đúng | C | ⬜ | Chờ API #22/#29 |
| TC-ORD-03 | | Thanh toán | Toá hoá đơn, bàn chuyển về `free` | C | ⬜ | Chờ API #22/#29 |
| TC-ORD-04 | Đơn đã thanh toán | Thử sửa đơn | Chặn, báo `ORDER_ALREADY_PAID` | D | ⬜ | |

## 5. Thống kê & báo cáo

| ID | Tiền điều kiện | Bước | Kết quả mong đợi | Người | Kết quả | Ghi chú |
|---|---|---|---|---|---|---|
| TC-RPT-01 | 30 ngày dữ liệu | Mở Dashboard | Doanh thu khớp với tổng hoá đơn tính tay | D | ⬜ | |
| TC-RPT-02 | | Xem top món bán chạy | Sắp xếp đúng giảm dần | D | ⬜ | |
| TC-RPT-03 | | Xuất Excel | File mở được, số liệu khớp màn hình | C | ⬜ | |
| TC-RPT-04 | Có giao dịch hôm qua, không có dòng hôm nay | Mở Dashboard | KPI hôm nay bằng 0; tổng kỳ và biểu đồ vẫn gồm dữ liệu hôm qua | B | ⬜ | GUI fixture test xanh; chờ API #95 để nghiệm thu E2E |
| TC-RPT-05 | Có giao dịch hôm qua và hôm nay | Mở Dashboard | KPI hôm nay khớp dòng ngày quán; tổng kỳ và biểu đồ gồm cả hai ngày | B | ⬜ | GUI fixture test xanh; chờ API #95 để nghiệm thu E2E |

## 6. Đóng gói & môi trường

| ID | Tiền điều kiện | Bước | Kết quả mong đợi | Người | Kết quả | Ghi chú |
|---|---|---|---|---|---|---|
| TC-PKG-01 | Máy Windows sạch (chưa có Python/MySQL) | Cài bằng `Setup.exe` | Cài xong, mở được app từ Start Menu | D | ⬜ | |
| TC-PKG-02 | | Gỡ cài đặt | Không còn sót file trong `Program Files` | D | ⬜ | |
| TC-PKG-03 | Có bản mới | Mở app bản cũ | Có thông báo cập nhật | D | ⬜ | |
| TC-PKG-04 | Mất mạng | Mở app | Báo lỗi thân thiện, không treo | C | ⬜ | |
