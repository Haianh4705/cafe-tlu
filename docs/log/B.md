# Nhật ký — B (Dữ liệu & Báo cáo)

> Quy tắc + mẫu: [`README.md`](README.md). Cập nhật trong PR đã làm việc, không dồn.
> **Người giữ file:** B — @trungdunxg. Người khác không sửa hộ.

**Vùng:** `db/`, `api/services/reports.py`, seed · **Bắt đầu:** G1 (đường găng — A và C đang chờ)

## 1. Tôi phụ trách gì

- Thiết kế ERD + từ điển dữ liệu + bất biến (`docs/erd.md`) và `db/schema.sql` (#17)
- `db/seed.sql` — 50 món, users, bàn (#18); sinh 120 đơn trải 30 ngày (#28)
- Query thống kê doanh thu + top món (`api/services/reports.py`, #31)
- Kiểm dữ liệu mẫu không tự mâu thuẫn (test/smoke)

## 2. Việc đã làm

| Ngày | Issue | PR / commit | File chính | Làm gì (1 câu) | Vì sao cách đó (1 câu) |
|---|---|---|---|---|---|
| | | | | | |

## 3. AI đã làm gì

| Ngày | Công cụ | AI làm gì | Tôi sửa / kiểm chứng gì |
|---|---|---|---|
| | | | |

## 4. Câu hỏi thầy hay hỏi (vùng B)

> Lấy từ [`defense.md`](../defense.md) mục B.

| # | Câu hỏi | Trả lời ngắn (2–4 câu) | Chỉ vào |
|---|---|---|---|
| 1 | Vì sao chia bảng như vậy? Sao không gộp bớt? | | `docs/erd.md` — **em tự viết** |
| 2 | Giá món đổi sau khi bán — hoá đơn cũ hiển thị giá nào? | | cột giá trong bảng chi tiết đơn |
| 3 | Vì sao tiền là `DECIMAL` không `FLOAT`? | | `db/schema.sql` |
| 4 | Index đặt ở đâu, vì sao? | | `db/schema.sql`, `EXPLAIN` |
| 5 | Viết query doanh thu theo ngày. | | `api/services/reports.py` |
| 6 | Xoá món: xoá cứng hay mềm, vì sao? | | `WORKFLOW.md` mục 8.3 |
| 7 | Từng khoá ngoại đặt `ON DELETE` gì, vì sao? | | FK trong `schema.sql` |
| 8 | Dữ liệu mẫu có tự mâu thuẫn không? Kiểm bằng cách nào? | | test / script seed |
| 9 | N+1 query là gì? Bài có bị không? | | `selectinload`/`joinedload` |

## 5. Chưa làm / chưa hiểu

- [ ] `db/schema.sql` + `db/seed.sql` chưa có → chặn A (#21) và C; `make up` cũng chưa tự nạp
      schema (2 dòng mount trong `docker-compose.yml` đang comment)
- [ ] _(ghi những chỗ mình chưa giải thích được)_

## 6. Nhật ký theo cổng

| Cổng | Ngày | Đã xong gì | Còn thiếu gì |
|---|---|---|---|
| G1 | | | |
| G2 | | | |
| G3 | | | |
