# Danh sách ca kiểm thử (test cases)

> Bảng này là **minh chứng cho báo cáo** (mốc 8: "chụp ảnh các bước đầy đủ") và là
> đầu vào cho cổng **G5**. Cập nhật ngay khi làm xong tính năng, đừng dồn tuần cuối.
>
> Quy ước: **C** = C (GUI) viết, **D** = D kiểm chứng lại trên máy sạch.
> Kết quả: `PASS` / `FAIL` / `BLOCKED` (kèm số Issue nếu FAIL).

## 1. Xác thực & phân quyền

| ID | Tiền điều kiện | Bước | Kết quả mong đợi | Người | Kết quả | Ghi chú |
|---|---|---|---|---|---|---|
| TC-AUTH-01 | Có user `admin` | Đăng nhập đúng mật khẩu | Vào được Dashboard, menu đầy đủ | C | BLOCKED | #25: API login + `/me` trả admin 200; chưa xác minh Dashboard/menu hoặc chụp ảnh GUI vì CUA không được phép điều khiển cửa sổ Python. |
| TC-AUTH-02 | Có user `admin` | Đăng nhập sai mật khẩu 3 lần | Báo lỗi rõ ràng, không lộ "sai user hay sai pass" | C | BLOCKED | #25: API trả cùng mã/thông báo 401 cho sai mật khẩu và user không tồn tại; GUI inline đã có unit test, chưa chạy thử 3 lần trên cửa sổ thật. |
| TC-AUTH-03 | Có user `thungan01` role `staff` | Đăng nhập role `staff` | Không thấy menu Quản lý thực đơn / Báo cáo doanh thu | C | BLOCKED | #25: API login + `/me` trả role staff 200; chưa xác minh menu GUI hoặc chụp ảnh vì CUA không được phép điều khiển cửa sổ Python. |
| TC-AUTH-04 | Role `staff` | Gọi trực tiếp API admin bằng token staff | 403 `FORBIDDEN` (chặn ở server) | D | ⬜ | |
| TC-AUTH-05 | Đã đăng nhập | Đóng app, mở lại | Quay về form đăng nhập; token chỉ lưu trong RAM | C | BLOCKED | #25: token chỉ được lưu trong RAM theo thiết kế; chưa đóng/mở lại GUI để xác minh trực tiếp vì CUA không được phép điều khiển cửa sổ Python. |

## 2. Quản lý món ăn / đồ uống (CRUD)

| ID | Tiền điều kiện | Bước | Kết quả mong đợi | Người | Kết quả | Ghi chú |
|---|---|---|---|---|---|---|
| TC-PRD-01 | Role admin | Thêm món mới đủ trường | Lưu thành công, hiện ngay trong danh sách | C | ⬜ | |
| TC-PRD-02 | | Thêm món trùng tên | Báo `PRODUCT_NAME_DUPLICATED`, không tạo bản ghi | C | ⬜ | |
| TC-PRD-03 | | Nhập giá âm hoặc chữ | Chặn ở form, không gửi lên server | C | ⬜ | |
| TC-PRD-04 | | Sửa giá món đang có đơn | Món trong đơn cũ **giữ giá cũ** | D | ⬜ | |
| TC-PRD-05 | | Xoá món | Xoá mềm; món biến khỏi danh sách nhưng hoá đơn cũ vẫn xem được | C | ⬜ | |

## 3. Tìm kiếm & lọc

| ID | Tiền điều kiện | Bước | Kết quả mong đợi | Người | Kết quả | Ghi chú |
|---|---|---|---|---|---|---|
| TC-SRC-01 | 5.000 món | Gõ "trà" vào ô tìm kiếm | Kết quả < 300ms, đúng chuỗi | D | ⬜ | |
| TC-SRC-02 | | Lọc theo danh mục + khoảng giá | Kết quả đúng cả 2 điều kiện | C | ⬜ | |
| TC-SRC-03 | | Tìm chuỗi không tồn tại | Hiện trạng thái "không có kết quả", không bảng trống trơ | C | ⬜ | |

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

## 6. Đóng gói & môi trường

| ID | Tiền điều kiện | Bước | Kết quả mong đợi | Người | Kết quả | Ghi chú |
|---|---|---|---|---|---|---|
| TC-PKG-01 | Máy Windows sạch (chưa có Python/MySQL) | Cài bằng `Setup.exe` | Cài xong, mở được app từ Start Menu | D | ⬜ | |
| TC-PKG-02 | | Gỡ cài đặt | Không còn sót file trong `Program Files` | D | ⬜ | |
| TC-PKG-03 | Có bản mới | Mở app bản cũ | Có thông báo cập nhật | D | ⬜ | |
| TC-PKG-04 | Mất mạng | Mở app | Báo lỗi thân thiện, không treo | C | ⬜ | |
