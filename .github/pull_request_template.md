## Issue và chức năng thực hiện

Refs #

<!-- Nêu kết quả đạt được (các tầng đã chạm: db / api / gui / infra / docs) và lý do nếu tách/gộp. -->

## Kiểm chứng

<!-- Dán lệnh + kết quả thật (`make lint`, `make test`) và link CI. Thêm ảnh chụp vào `docs/screenshots/` nếu xong/đổi màn hình. -->

## Giải thích được

1. Đoạn thay đổi làm gì?
2. Vì sao chọn cách này?
3. Nếu thầy hỏi vì sao không dùng cách khác thì trả lời thế nào?

## Checklist trước khi Squash & Merge (không cần chờ approve — ADR-014)

- [ ] Đúng phạm vi Issue, giữ kiến trúc một chiều `gui → api → db` (`gui/` không chạm DB/models).
- [ ] `make lint && make test` xanh ở local và cả 2 check CI trên GitHub đã xanh.
- [ ] Đã cập nhật tài liệu liên quan (`docs/api-contract.md` / `db/schema.sql` / `CHANGELOG.md` khi đổi hành vi).
- [ ] Đã ghi 1–3 dòng vào `docs/log/<vai>.md` của chính mình (mục 2: việc · mục 3: AI đã hỗ trợ gì).
