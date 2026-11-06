# Thiết kế dữ liệu (ERD) — B tự thiết kế

> **Trạng thái: ⬜ CHƯA THIẾT KẾ.** File này chỉ là **khung**. B (Data & Reports) điền toàn bộ
> phần thiết kế **trước khi** làm `db/schema.sql` (issue #17).
>
> Nhóm đã **cố ý bỏ bản ERD viết sẵn** — để người làm dữ liệu tự thiết kế, hiểu và bảo vệ được
> trước giảng viên. Không có đáp án ở đây, cũng không có ở đâu khác trong repo.

## 0. Vì sao B phải tự thiết kế

- Câu hỏi bảo vệ luôn là: *"vì sao em chia bảng như vậy?"*, *"sao không gộp thành một bảng?"*,
  *"cột này sao nằm ở bảng kia?"* — chỉ trả lời được nếu **chính mình thiết kế**.
- Đề bài: **copy = 0 điểm**. Bản thiết kế do người khác viết là thứ đầu tiên bị phát hiện khi hỏi.
- Thiết kế sai thì sửa rất đắt sau khi A đã viết models và C đã làm GUI → **chốt sớm, chốt kỹ**.

## 1. Phạm vi dữ liệu bắt buộc (từ đề bài + hợp đồng API)

App phải quản lý được tối thiểu:

| Nhóm | Nội dung nghiệp vụ |
|---|---|
| Người dùng | Tài khoản nhân viên, vai trò (phân quyền cơ bản) |
| Thực đơn | Món ăn/uống, danh mục, giá, trạng thái còn bán |
| Bàn | Bàn/khu vực, trạng thái bàn |
| Bán hàng | Đơn tại bàn, chi tiết món trong đơn, ghi chú, trạng thái pha chế |
| Thanh toán | Hoá đơn, giảm giá, phương thức, thời điểm |
| Truy vết | Nhật ký thao tác quan trọng (ai sửa gì, khi nào) |

`docs/api-contract.md` đã chốt **các trường app phải trả về** cho GUI. Đó là **yêu cầu**;
schema của B phải phục vụ được những trường đó (có thể có thêm cột nội bộ).

## 2. Quy ước kỹ thuật — bắt buộc

Chi tiết đầy đủ ở `WORKFLOW.md` **mục 8**. Tóm tắt không thể bỏ:

| Mục | Giá trị |
|---|---|
| Engine / charset | `InnoDB` · `utf8mb4` · `utf8mb4_unicode_ci` |
| Khoá chính | `id BIGINT UNSIGNED AUTO_INCREMENT` |
| Khoá ngoại | `<bảng_số_ít>_id`, khai báo `ON DELETE` **có chủ đích** |
| Tiền | `DECIMAL(12,0)` — **cấm** `FLOAT`/`DOUBLE` |
| Boolean | `is_*` / `has_*`, `TINYINT(1)` |
| Thời gian | `created_at`, `updated_at` ở mọi bảng nghiệp vụ |
| Index | `idx_<bảng>_<cột>`; unique `uq_<bảng>_<cột>` |
| Xoá | Dữ liệu quan trọng **xoá mềm**, không xoá cứng |

## 3. Khung để B điền

### 3.1 Sơ đồ

```mermaid
erDiagram
    %% TODO (B): vẽ các bảng + quan hệ. Ví dụ cú pháp:
    %% users ||--o{ orders : "tạo"
    %% users { bigint id PK
    %%         varchar username UK }
```

> Không quen Mermaid? Dùng <https://dbdiagram.io>, xuất ảnh →
> `docs/screenshots/db/erd-<YYYYMMDD>.png` → nhúng vào đây.

### 3.2 Từ điển dữ liệu

Điền cho **từng bảng**, đủ mọi cột:

| Cột | Kiểu | Ràng buộc | Mô tả |
|---|---|---|---|
| _(ví dụ)_ `id` | BIGINT UNSIGNED | PK | |

### 3.3 Bất biến dữ liệu

Những điều **luôn phải đúng**, tầng service chịu trách nhiệm bảo đảm. Gợi ý để tự trả lời:

- Tổng tiền của đơn được tính từ đâu? Nếu sửa/xoá một dòng món thì tổng cập nhật thế nào?
- Giá món đổi sau khi bán — hoá đơn cũ hiển thị giá nào?
- Hoá đơn có được sửa sau khi thanh toán không?
- Trạng thái bàn lấy từ đâu (bảng bàn hay suy ra từ đơn đang mở)?
- Xoá mềm một món thì dữ liệu cũ hiển thị ra sao?

### 3.4 Kế hoạch dữ liệu mẫu (`db/seed.sql`)

| Bảng | Số dòng dự kiến | Ghi chú |
|---|---|---|
| | | Phải đủ để biểu đồ doanh thu 30 ngày có ý nghĩa |

## 4. B phải tự trả lời trước khi chốt

1. Chia bao nhiêu bảng? Vì sao **không** gộp bớt (hoặc vì sao gộp)?
2. Mỗi quan hệ là 1-n hay n-n? Có bảng trung gian không?
3. Cột nào có thể suy ra từ cột khác? (nếu suy được thì có nên lưu không — trade-off)
4. `ON DELETE` cho từng khoá ngoại: RESTRICT, CASCADE hay SET NULL? Vì sao?
5. Index nào cần cho các truy vấn báo cáo ở `docs/api-contract.md`?
6. Trạng thái dùng `VARCHAR` hay bảng tra cứu? Vì sao?

## 5. Deliverable — điều kiện để A bắt đầu

- [ ] Sơ đồ ERD (mermaid hoặc ảnh) đã vẽ
- [ ] Từ điển dữ liệu đủ **mọi** bảng và cột
- [ ] Bất biến dữ liệu + quy tắc xoá đã ghi
- [ ] Kế hoạch `seed.sql` (số dòng mỗi bảng)
- [ ] PR vào `develop`, **A review và approve** (vì A sẽ viết models dựa trên đây)
- [ ] Đã trả lời được 6 câu ở mục 4 (tự kiểm, không cần viết ra hết)

> Sau khi chốt, đổi dòng "Trạng thái" ở đầu file thành **✅ Đã chốt v1 (ngày …)**.
> Từ đó, mọi thay đổi cấu trúc phải mở PR riêng và báo nhóm (`WORKFLOW.md` mục 8.1).
