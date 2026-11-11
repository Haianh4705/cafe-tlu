# Nhật ký — C (Giao diện / UX)

> Quy tắc + mẫu: [`README.md`](README.md). Cập nhật trong PR đã làm việc, không dồn.
> **Người giữ file:** C — @MeoCamGuitar. Người khác không sửa hộ.

**Vùng:** `gui/`, `assets/` · **Bắt đầu:** G1

## 1. Tôi phụ trách gì

- Khung GUI + theme TLU + `BaseView` (#23), `api_client` + i18n (#24), màn Đăng nhập (#25)
- Màn Danh sách món (#30), màn Order tại bàn + thanh toán + in hoá đơn (#49 = PR #44)
- 4 trạng thái màn hình (loading / rỗng / lỗi / có dữ liệu), ảnh chụp vào `docs/screenshots/<module>/`
- Ghi `docs/test-cases.md` các ca vùng GUI — **chỉ đánh `PASS` khi chạy end-to-end với API + MySQL thật**

## 2. Việc đã làm

| Ngày | Issue | PR / commit | File chính | Làm gì (1 câu) | Vì sao cách đó (1 câu) |
|---|---|---|---|---|---|
| | | | | | |

## 3. AI đã làm gì

| Ngày | Công cụ | AI làm gì | Tôi sửa / kiểm chứng gì |
|---|---|---|---|
| | | | |

## 4. Câu hỏi thầy hay hỏi (vùng C)

> Lấy từ [`defense.md`](../defense.md) mục C.

| # | Câu hỏi | Trả lời ngắn (2–4 câu) | Chỉ vào |
|---|---|---|---|
| 1 | Vì sao PySide6, không Tkinter? | | `docs/decisions.md` ADR-003 |
| 2 | Gọi API mất 2 giây thì UI thế nào? Sao không treo? | | worker/QThread trong `gui/` |
| 3 | Màn hình có 4 trạng thái — kể tên và vì sao cần? | | skill `pyside6-screen` mục 4 |
| 4 | Palette lấy ở đâu? Vì sao navy? | | `gui/theme.py` + ADR-007 |
| 5 | `api_client` để làm gì? Sao không gọi `requests` rải rác? | | `gui/api_client.py` |
| 6 | API trả 500 thì GUI hiển thị gì? | | nhánh `error.code` |
| 7 | Tiếng Việt: font gì, vì sao không dùng font mặc định? | | `gui/theme.py`, `assets/fonts/` |
| 8 | Signal/slot là gì? Ví dụ trong bài? | | kết nối worker → view |
| 9 | Resize 1280 vs full HD xử lý sao? | | layout/`QSizePolicy` |

## 5. Chưa làm / chưa hiểu

- [ ] PR #44 (màn Order) còn phải sửa theo review: body PR trống, TC-ORD-01/03 đang `PASS` sai
      (chưa có API/DB), test lọc món chỉ assert ô nhập
- [ ] Màn hình chưa nối API thật — đang dùng mock, nên chưa ca nào được tính `PASS`
- [ ] _(ghi những chỗ mình chưa giải thích được)_

## 6. Nhật ký theo cổng

| Cổng | Ngày | Đã xong gì | Còn thiếu gì |
|---|---|---|---|
| G1 | | | |
| G2 | | | |
| G3 | | | |
