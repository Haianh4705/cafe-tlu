# Đóng góp cho dự án

> Đây là **bản rút gọn cho người mới**. Quy chuẩn đầy đủ và có hiệu lực là
> **[`WORKFLOW.md`](WORKFLOW.md)** — khi hai file khác nhau, `WORKFLOW.md` thắng.

## Đọc gì trước (theo thứ tự, ~15 phút)

1. [`README.md`](README.md) — cài và chạy trong 4 lệnh
2. [`WORKFLOW.md`](WORKFLOW.md) mục 0 (TL;DR) + mục 4 (ranh giới sở hữu)
3. [`docs/decisions.md`](docs/decisions.md) — những gì đã chốt, không mở lại
4. [`docs/api-contract.md`](docs/api-contract.md) + [`docs/erd.md`](docs/erd.md)
   (ERD **do B thiết kế** — có thể còn là khung khi bạn mới vào)

## Cài đặt

```bash
make install     # venv + thư viện + pre-commit hook + .env
make up          # MySQL trong Docker
make doctor      # phải thấy Python 3.12+ và MySQL sẵn sàng
```

## Vòng lặp làm việc (1 việc)

```bash
# 1. Có Issue trên GitHub đã đạt Definition of Ready
git switch develop && git pull --ff-only
git switch -c feature/<scope>-<mô-tả>-<tên>

# 2. Code + test
make check                       # lint + test phải xanh

# 3. Commit
git add <path-cụ-thể>
git commit -m "feat(order): thêm chức năng gộp bàn"

# 4. PR
git push -u origin HEAD
gh pr create --base develop --fill
```

Sau đó: gán reviewer là **owner vùng bị sửa**, chờ **1 approval + CI xanh**, merge
bằng **Squash**.

## Năm điều dễ sai nhất

| ❌ Sai | ✅ Đúng |
|---|---|
| Commit thẳng lên `develop` | Luôn qua PR (hook `no-commit-to-branch` sẽ chặn) |
| `git add .` | `git add <file>` cụ thể, xem `git status` trước |
| Sửa test cho pass | Sửa code; test sai thì nói rõ lý do trong PR |
| GUI gọi thẳng MySQL | GUI → `api_client.py` → REST API |
| Để ảnh chụp/báo cáo tới tuần cuối | Chụp và lưu **ngay khi xong việc** |

## Commit message

`<loại>(<scope>): <mô tả>`

- Loại: `feat` `fix` `refactor` `test` `docs` `chore` `perf` `style`
- Scope: `db` `api` `auth` `order` `product` `report` `gui` `infra` `ci` `installer` `docs` `deps`
- Ví dụ: `fix(auth): sửa lỗi token hết hạn không chuyển về màn đăng nhập`

## Cần giúp?

- Bị chặn **> 2 giờ** → báo trong standup hoặc tag owner vùng đó trong Issue.
- Không rõ nghiệp vụ → hỏi trong Issue, đừng tự đoán rồi code.

## Nếu bạn dùng AI

Đọc [`AGENTS.md`](AGENTS.md). Tóm tắt: AI được phép đọc mọi file, tạo nhánh, sửa file
trong vùng được giao, chạy test; **phải hỏi** khi đổi schema/API/dependency; **bị cấm**
push thẳng `main`/`develop`, commit `.env`, sửa test cho pass.
