# `report/` — Báo cáo bài tập lớn

**Owner:** D biên tập, mỗi người viết chương của mình · **Bắt đầu:** cổng G2 (không đợi hết code)

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

## Phân công & Hạn hoàn thành theo cổng

> Quy ước hạn (khớp `docs/workflow.md` mục 8): tác giả chốt chương trước hạn nộp bài **5 ngày** (cổng G5); D biên tập toàn văn bản trước hạn nộp **3 ngày** (cổng G6).

| File | Nội dung chính | Người phụ trách | Cổng gắn kết | Hạn chốt |
|---|---|---|---|---|
| `00-bia.md` | Bìa, phân công, mục lục, thuật ngữ | D (@Haianh4705) | G2 → G5 | Trước hạn nộp 3 ngày |
| `01-mo-dau.md` | Lý do, mục tiêu, phạm vi, phân vai | D (@Haianh4705) | G2 → G5 | Trước hạn nộp 5 ngày |
| `02-khao-sat.md` | Nghiệp vụ quán café TLU, yêu cầu | C (@MeoCamGuitar), B | G3 → G5 | Trước hạn nộp 5 ngày |
| `03-phan-tich.md` | Use Case, ERD 10 bảng, 3NF, snapshot | B (@trungdunxg) | G2 → G3 → G5 | Trước hạn nộp 5 ngày |
| `04-thiet-ke-api.md` | Kiến trúc API, 23 endpoint, JWT, RBAC | A (@bao20062005dh-creator) | G2 → G3 → G4/G5 | Trước hạn nộp 5 ngày |
| `05-thiet-ke-gui.md` | Palette TLU, PySide6, QThread, 4 màn | C (@MeoCamGuitar) | G2 → G3 → G5 | Trước hạn nộp 5 ngày |
| `06-trien-khai.md` | Docker, CI/CD, bộ cài Windows, deploy | D (@Haianh4705) | G2/G3 → G4 → G5 | Trước hạn nộp 3 ngày |
| `07-ket-qua.md` | Đối chiếu rubric, e2e, test case, máy sạch | D (@Haianh4705) + A/B/C | G3 → G4/G5 | Trước hạn nộp 3 ngày |
| `08-kho-khan.md` | Sự cố thật, tích hợp, kiểm soát AI | Cả nhóm (D biên tập) | G2–G4 → G5 | Trước hạn nộp 5 ngày |
| `09-huong-phat-trien.md` | Nợ kỹ thuật `shortcut:`, QR order, ca làm | A + D | G3/G4 → G5 | Trước hạn nộp 5 ngày |
