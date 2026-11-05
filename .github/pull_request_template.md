<!-- Template PR — bám theo WORKFLOW.md mục 18.2. Không xoá các mục có sẵn. -->

## Liên kết

Closes #

## Đã làm gì

<!-- 1–3 gạch đầu dòng, nói KẾT QUẢ không phải quá trình -->

-
-

## Giải thích được (bắt buộc — xem `docs/defense.md`)

> Không viết được 3 câu này = chưa hiểu bài, đừng mở PR.

1. **Đoạn code này làm gì:** <!-- 1 câu, không dùng "xử lý"/"quản lý" chung chung -->
2. **Vì sao chọn cách này thay vì cách khác:** <!-- 1 câu, nêu trade-off -->
3. **Nếu thầy hỏi "sao không dùng X?" thì trả lời:** <!-- 1 câu -->

## Cách kiểm chứng

<!-- Dán kết quả THẬT. Không viết "em đã test rồi". -->

| Lệnh / bước | Kết quả |
|---|---|
| `make lint` | |
| `make test` | |
| Thủ công | |

## Ảnh chụp màn hình

<!-- Bắt buộc nếu có thay đổi giao diện. Lưu vào docs/screenshots/<module>/ -->

| Trước | Sau |
|---|---|
| | |

## Ghi chú cho reviewer

<!-- Chỗ nào bạn muốn được soi kỹ, chỗ nào bạn còn phân vân -->

-

## Checklist tác giả (bắt buộc tick đủ)

- [ ] Đúng phạm vi Issue, không kèm thay đổi ngoài lề
- [ ] Tuân thủ ranh giới kiến trúc (WORKFLOW.md mục 4): GUI không gọi DB, router không chứa logic
- [ ] Có test cho hành vi mới, hoặc ghi rõ lý do không có
- [ ] Không có secret / `print()` debug / code comment-out
- [ ] Đã cập nhật `docs/api-contract.md` / `docs/erd.md` nếu có đổi
- [ ] Đã thêm 1 dòng vào `CHANGELOG.md` mục `Unreleased`
- [ ] PR < 400 dòng diff

## Checklist reviewer (người review tick)

- [ ] Logic đúng tiêu chí nghiệm thu
- [ ] Trường hợp biên: rỗng, trùng, số âm, quá dài, mất kết nối
- [ ] Phân quyền được kiểm ở server, không chỉ ẩn nút
- [ ] Test có ý nghĩa, không phải test hình thức
- [ ] Không N+1 query; cột lọc mới có index
- [ ] Tên biến/hàm rõ nghĩa, thông báo lỗi thân thiện
