# `docs/log/` — Nhật ký cá nhân (bắt buộc, mỗi người một file)

> Mục đích: khi giảng viên hỏi **"phần này em làm gì, AI làm gì, vì sao làm thế?"**, mỗi người mở
> đúng một file và trả lời được trong 30 giây — kèm commit, PR, lệnh đã chạy.
>
> Đây **không phải** báo cáo nộp bài (báo cáo ở `report/`). Đây là **sổ bằng chứng** của riêng bạn.

## 1. Ai giữ file nào

| File | Người giữ | Vùng |
|---|---|---|
| [`A.md`](A.md) | A — @bao20062005dh-creator | `api/`, `shared/` |
| [`B.md`](B.md) | B — @trungdunxg | `db/`, `api/services/reports.py` |
| [`C.md`](C.md) | C — @MeoCamGuitar | `gui/`, `assets/` |
| [`D.md`](D.md) | D — @Haianh4705 | `infra/`, `installer/`, `.github/`, `docs/`, `report/` |

**Luật:** chỉ **người đó** (hoặc AI làm việc cho người đó) được sửa file của mình. Người khác muốn
nhắc → comment trong PR/Issue, không sửa hộ. `D.md` đã điền sẵn làm **mẫu** — xem trước rồi làm theo.

## 2. Sáu mục bắt buộc trong mỗi file

| Mục | Trả lời câu hỏi nào của giảng viên | Độ dài |
|---|---|---|
| 1. Tôi phụ trách gì | "Em làm phần nào?" | 3–5 gạch đầu dòng |
| 2. Việc đã làm | "Đưa bằng chứng" | 1 dòng / PR |
| 3. AI đã làm gì | "Code này ai viết? Copy ở đâu?" | 1 dòng / phiên |
| 4. Câu hỏi thầy hay hỏi | "Giải thích dòng này" | 5–8 câu |
| 5. Chưa làm / chưa hiểu | "Điểm yếu của bài?" | danh sách ngắn |
| 6. Nhật ký theo cổng | "Tiến độ tới đâu?" | 1 dòng / cổng |

## 3. Năm quy tắc ghi

1. **Ghi trong cùng PR** đã làm việc đó — 1–3 dòng, không để dồn. PR không có dòng log = PR chưa
   xong (xem `WORKFLOW.md` mục 6.2).
2. **Mỗi dòng phải kiểm chứng được:** commit hash hoặc số PR, file chính, lệnh đã chạy. Không viết
   "đã hoàn thành", "chạy ổn".
3. **Ghi cả AI, không giấu:** dùng công cụ nào, AI làm phần nào, **mình sửa lại gì**, **mình kiểm
   chứng bằng gì**. Giấu rồi bị phát hiện = rủi ro 0 điểm; ghi rõ = minh bạch và được điểm quy trình.
4. **Ghi cả phần chưa hiểu.** Mục 5 là danh sách ôn tập của bạn — càng thật càng tốt, không ai trừ
   điểm vì còn phải học.
5. **Không bịa số.** Chưa có số liệu thì ghi `chưa có`, đừng điền cho đẹp.

## 4. Khi nào cập nhật

| Thời điểm | Việc | Thời gian |
|---|---|---|
| Mỗi PR merge | Thêm 1 dòng vào mục 2 + mục 3 (nếu có AI) | 3–5 phút |
| Trước mỗi cổng (G1…G6) | Rà mục 2, làm mới mục 4, cập nhật mục 6 | 15 phút |
| Trước buổi bảo vệ | Đọc to mục 4 một lần, xoá câu trả lời không chỉ được vào code | 20 phút |

## 5. Mẫu copy nhanh

```markdown
| Ngày | Issue | PR / commit | File chính | Làm gì (1 câu) | Vì sao cách đó (1 câu) |
|---|---|---|---|---|---|
| 2026-11-20 | #29 | #51 / `a1b2c3d` | api/routers/products.py | thêm GET /products lọc + phân trang | lọc ở SQL để không kéo 5k dòng về Python |

| Ngày | Công cụ | AI làm gì | Tôi sửa / kiểm chứng gì |
|---|---|---|---|
| 2026-11-20 | DSH (agent) | viết nháp endpoint + 4 test | sửa điều kiện lọc giá, chạy `make test` 19 passed, tự giải thích được từng dòng |

| # | Câu hỏi | Trả lời ngắn | Chỉ vào |
|---|---|---|---|
| 1 | Vì sao router không viết SQL? | router chỉ validate + gọi service; SQL nằm ở service để test được và đổi DB không sửa router | `api/routers/products.py:12` |
```

## 6. Liên quan

- [`docs/defense.md`](../defense.md) — ngân hàng câu hỏi theo vùng + sổ "chưa trả lời được".
- [`docs/defense-D.md`](../defense-D.md) — bản ôn chi tiết của D (ví dụ về độ sâu nên có).
- `WORKFLOW.md` mục 6.2 (Definition of Done), 12.5 (nhật ký), 15.7 (AI ghi hộ), 16.2 (nhịp cập nhật).
