# `report/` — Báo cáo bài tập lớn

**Owner:** D biên tập, mỗi người viết chương của mình · **Bắt đầu:** tuần 4 (không đợi hết code)

## Cấu trúc

```
report/
├── 00-bia.md
├── 01-mo-dau.md              # mục tiêu, phạm vi, phân công
├── 02-khao-sat.md            # khảo sát quán café TLU
├── 03-phan-tich.md           # use case, ERD (B)
├── 04-thiet-ke-api.md        # endpoint, bảo mật (A)
├── 05-thiet-ke-gui.md        # wireframe, palette TLU (C)
├── 06-trien-khai.md          # cài đặt, kiểm thử, đóng gói, deploy (D)
├── 07-ket-qua.md             # ảnh chụp + số liệu thật
├── 08-kho-khan.md            # vấn đề gặp phải và cách giải  ← ăn điểm
├── 09-huong-phat-trien.md    # mốc 8–9: mở rộng tiếp
└── assets/                   # ảnh nhúng riêng của báo cáo
```

## KHÔNG đặt

- Bản `.docx`/`.pdf` cuối cùng (nộp riêng; nếu cần lưu thì để ở Release/Tag, không làm nặng repo)
- Ảnh chụp trùng với `docs/screenshots/` — nhúng link, đừng copy
- Nội dung copy từ tài liệu nước ngoài không trích nguồn

## Quy ước

Mỗi chương 2–5 trang, có mở đầu và tổng kết ngắn. Mọi khẳng định phải có **minh chứng**:
ảnh chụp, số liệu đo được, hoặc link file trong repo. Mục `08-kho-khan.md` là phần dễ ăn điểm
nhất — ghi lại cả những lỗi đã sửa trong quá trình làm (xem `CHANGELOG.md` để nhớ lại).
