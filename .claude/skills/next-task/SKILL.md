---
name: next-task
description: Trả lời "tôi cần làm gì tiếp?" cho một thành viên. Dùng khi người dùng hỏi "hôm nay tôi làm gì", "việc tiếp theo của tôi", "tôi đang cần làm gì", "task của tôi", hoặc mở phiên mới mà không nói rõ muốn làm gì.
---

# "Tôi cần làm gì?"

Người dùng là **một trong 4 thành viên** (A/B/C/D). Họ không nhớ hết Issue. Nhiệm vụ của bạn:
xác định **việc tiếp theo của đúng người đó**, theo **đúng thứ tự phụ thuộc**, và nói ngắn gọn
họ phải làm gì tiếp.

## Bước 1 — Xác định họ là ai

```bash
make next
```

Lệnh này in ra việc tiếp theo + danh sách còn lại, theo Issue được gán cho tài khoản `gh` đang
đăng nhập. **Đây là nguồn chân lý** — không tự suy đoán từ lịch sử chat.

Nếu `make next` báo thiếu `gh` hoặc chưa đăng nhập: hỏi họ **username GitHub** rồi tra:

```bash
gh issue list --assignee <username> --state open --json number,title,milestone,labels,url
```

Nếu vẫn không có: hỏi họ giữ vai nào (A/B/C/D) rồi xem `docs/plan.md` mục tương ứng.

## Bước 2 — Đọc issue đó

```bash
gh issue view <số> --json title,body,labels,milestone
```

Đọc **hai mục** trong body: `## Việc cần làm` và `## Tiêu chí nghiệm thu`.
Không đọc hết 16 issue — chỉ issue tiếp theo.

## Bước 3 — Trả lời theo đúng khuôn này

```
## Việc tiếp theo: #<số> — <tiêu đề>  (<milestone>)

**Làm gì:** 2–4 gạch đầu dòng, lấy từ mục "Việc cần làm" của issue.
**Xong khi:** 2–3 gạch đầu dòng từ "Tiêu chí nghiệm thu".
**Đọc trước:** skill `<tên>` (.claude/skills/<tên>/SKILL.md) + `minimal-change`.
**Chờ ai / chặn ai:** <nếu issue có phụ thuộc, nêu rõ issue nào phải xong trước,
   và việc này đang chặn ai — tra trong docs/plan.md hoặc docs/workflow.md>
**Lệnh bắt đầu:**
   git switch develop && git pull --ff-only
   git switch -c feature/<scope>-<slug>-<ten>
```

Sau đó **một dòng** về việc kế tiếp, không liệt kê hết.

## Quy tắc

1. **Không tự bịa việc.** Không có việc nào được gán → nói thật, bảo họ hỏi D hoặc nhận issue
   ở cột Ready. Không tự đề xuất tính năng mới.
2. **Không đảo thứ tự.** Nếu việc số 2 phụ thuộc việc số 1 của người khác, nói rõ:
   *"#21 cần #17 của B xong trước"*. Đừng khuyên họ làm sớm rồi sửa lại.
3. **Không code thay họ.** Họ phải tự làm để bảo vệ trước GV (đề bài: copy = 0 điểm).
   Được: giải thích, chỉ file, gợi ý cách làm. Không: viết cả file rồi bảo họ commit.
4. **Nhắc điều kiện xong** ngắn gọn: `make check` xanh · PR cần 1 approval + CI xanh ·
   3 câu "Giải thích được" (`docs/defense.md`).
5. **Không quên ảnh chụp** nếu là việc UI — đó là điểm mốc 8, và dễ bị bỏ nhất.

## Nếu họ hỏi "cổng này tôi làm gì?" (không phải "việc tiếp theo")

Trả lời theo `docs/plan.md` mục của **cổng đang mở**: liệt kê các việc của họ trong cổng đó, theo
sóng, kèm điều kiện ra cổng. Dùng bảng điều khiển cổng (`gh issue list --label tracking`) làm nguồn.
Không quy đổi ra tuần — cổng mở khi đủ điều kiện, không theo lịch.

## Nếu họ hỏi "tôi đang bị chặn thì làm gì?"

Xem `docs/plan.md` mục "Đang chờ người khác thì làm gì" — mỗi tình huống có việc thay thế
không phụ thuộc ai. Không khuyên ngồi chờ.
