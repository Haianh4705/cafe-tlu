# Thiết lập GitHub — làm một lần, ~30 phút

> ✅ **TRẠNG THÁI: ĐÃ HOÀN TẤT (2026-11-05).** Repo đã có branch protection, CI, nhãn, milestone,
> 4 collaborator. Tài liệu này giữ lại để **tra cứu** khi cần dựng lại hoặc giải thích với GV —
> **đừng chạy lại từ đầu**, chỉ chạy phần còn thiếu.
>
> Người thực hiện: **D**. Thứ tự bắt buộc: bước 3 (chờ CI xanh một lần) phải xong **trước** bước 4
> (bật protection), nếu không PR sẽ không bao giờ merge được.

## 0. Chuẩn bị

```bash
gh --version          # chưa có: brew install gh   (Windows: winget install GitHub.cli)
gh auth login         # chọn HTTPS, đăng nhập bằng trình duyệt
```

## 1. Đẩy repo lên GitHub

```bash
cd cafe-tlu
git log --oneline        # repo đã có commit khởi tạo hạ tầng rồi
git status               # KIỂM TRA: không có .env, không có .venv, không có file >5MB
gh repo create cafe-tlu --private --source=. --remote=origin --push
```

> Nếu `git log` báo chưa có commit nào (repo mới tinh), chạy trước:
> `git add . && git commit -m "chore: khởi tạo hạ tầng dự án"`

Tạo nhánh tích hợp:

```bash
git switch -c develop
git push -u origin develop
```

## 2. Điền username thật vào CODEOWNERS

Mở `.github/CODEOWNERS`, thay 4 chỗ `@TODO-*`:

| Placeholder | Username thật |
|---|---|
| `@TODO-backend-a` | |
| `@TODO-data-b` | |
| `@TODO-gui-c` | |
| `@TODO-infra-d` | |

Commit qua PR (đây là bài tập đầu tiên về quy trình):

```bash
git switch -c chore/real-codeowners-d
git add .github/CODEOWNERS
git commit -m "chore(ci): điền username thật vào CODEOWNERS"
git push -u origin HEAD
gh pr create --base develop --fill
```

## 3. Chờ CI chạy ít nhất một lần

```bash
gh run list --limit 5
gh run watch            # phải thấy 2 job "Lint & format" và "Test" xanh
```

> ⚠️ Nếu CI đỏ ở bước này, dừng lại và sửa trước khi bật bảo vệ nhánh.

## 4. Bật branch protection cho `main` và `develop`

```bash
for BR in main develop; do
  echo "→ Bảo vệ nhánh $BR"
  gh api --method PUT "repos/{owner}/{repo}/branches/$BR/protection" --input - <<'JSON'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["Lint & format", "Test"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true,
    "require_last_push_approval": false
  },
  "restrictions": null,
  "required_linear_history": true,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": true
}
JSON
done
```

Kiểm tra lại:

```bash
gh api "repos/{owner}/{repo}/branches/main/protection" --jq '.required_pull_request_reviews, .required_status_checks.contexts'
```

**Ghi chú quan trọng:**

- `contexts` **phải khớp chính xác** với `name:` của job trong `.github/workflows/ci.yml`
  (`Lint & format`, `Test`). Đổi tên job → phải cập nhật lại protection.
- `required_linear_history: true` buộc dùng **Squash merge** (đúng WORKFLOW mục 5.6).

Bật thêm trong giao diện (2 bước, không có CLI ổn định):

- Settings → General → Pull Requests → ✅ **Automatically delete head branches**
- Settings → Actions → General → Workflow permissions → chọn **Read repository contents**
  (và ✅ Allow GitHub Actions to create and approve pull requests — cần cho Dependabot)

### 4b. Nếu tài khoản đang dùng là bản Free

> ✅ **Trạng thái hiện tại: ĐÃ XỬ LÝ.** Repo đã chuyển sang **public** nên branch protection
> bật được bình thường (đã áp dụng cho `main` và `develop` ngày 2026-11-04).
> Phần dưới giữ lại để tham khảo nếu sau này chuyển repo về private.

GitHub **chặn branch protection và rulesets với repo private trên tài khoản Free**:

```
Upgrade to GitHub Pro or make this repository public to enable this feature. (HTTP 403)
```

Ba cách xử lý, chọn một:

| Cách | Ưu điểm | Nhược điểm |
|---|---|---|
| **1. Bật GitHub Student Developer Pack** (khuyến nghị) | Miễn phí, có **Pro** trong suốt thời gian còn là sinh viên → branch protection hoạt động đầy đủ | Cần xác minh bằng email trường (1–3 ngày) |
| **2. Chuyển repo sang public** | Có protection ngay, đúng tinh thần "portfolio khi đi phỏng vấn" | **Rủi ro bị nhóm khác copy** → đề bài ghi copy = 0 điểm. Chỉ nên public **sau khi đã nộp** |
| **3. Không bật protection** | Không làm gì cả | Không có hàng rào server-side; chỉ còn hook local + ý thức |

Cách 1: https://education.github.com/pack → "Get your Student Developer Pack" → xác minh
bằng email `@tlu.edu.vn` → bật lại 2 lần chạy lệnh ở mục 4.

Nếu tạm thời dùng cách 3, nhóm vẫn còn **một lớp bảo vệ phía máy**: hook
`no-commit-to-branch` trong `.pre-commit-config.yaml` sẽ **chặn commit trực tiếp**
lên `main`/`develop` ở cả 4 máy (sau khi chạy `make install`).

> Ngoại lệ hợp lệ duy nhất để bỏ qua hook: merge phát hành.
> Dùng `git commit --no-verify` và ghi rõ lý do trong PR.

## 5. Tạo nhãn (labels)

```bash
gh label create api     -c 1D76DB -d "Backend / API — A"        || true
gh label create gui     -c 5319E7 -d "Giao diện desktop — C"    || true
gh label create db      -c 006B75 -d "CSDL / migration — B"     || true
gh label create report  -c 0E8A16 -d "Thống kê / báo cáo — B"   || true
gh label create infra   -c FBCA04 -d "Docker / CI / deploy — D" || true
gh label create docs    -c C2E0C6 -d "Tài liệu — D"             || true
gh label create bug     -c D73A4A -d "Lỗi"                      || true
gh label create blocked -c 000000 -d "Đang bị chặn"             || true
gh label create quick   -c EDEDED -d "Việc dưới 30 phút"        || true
gh label create triage  -c D4C5F9 -d "Mới tạo, chưa phân loại"  || true
```

## 6. Tạo milestone theo tuần

```bash
for i in 1 2 3 4 5 6 7 8; do
  gh api "repos/{owner}/{repo}/milestones" -f "title=W$i" -f "description=Tuần $i" >/dev/null \
    && echo "✅ W$i"
done
```

## 7. Tạo Project board

```bash
gh project create --owner "@me" --title "CafeTLU" --format json
gh project link <NUMBER> --owner "@me"
```

Sau đó trong giao diện Projects:

- Đổi view thành **Board**
- Thêm cột: `Backlog` · `Ready` · `In progress` · `In review` · `Done`
- Settings → **Workflow**: bật "Item closed → Done", "PR merged → Done"
- Settings → **Limits**: đặt **WIP = 2** cho cột `In progress` (WORKFLOW mục 16.4)

## 8. Mời thành viên

```bash
gh api -X PUT "repos/{owner}/{repo}/collaborators/<username>" -f permission=push
```

Gửi kèm link để 3 bạn đọc ngay khi nhận lời mời: `WORKFLOW.md` → `AGENTS.md` → `docs/decisions.md`.

## 9. Kiểm tra lần cuối

- [ ] `main` và `develop` đều bị chặn push trực tiếp
- [ ] PR vào `develop` bắt buộc 1 approval + CI xanh
- [ ] CI xanh ít nhất 1 lần (2 job)
- [ ] `CODEOWNERS` đã điền username thật
- [ ] 9 nhãn + 8 milestone đã có
- [ ] Board có 5 cột, WIP = 2
- [ ] 4 người đều đã nhận lời mời (và đã push được 1 nhánh thử)
- [ ] Dependabot đã bật (Settings → Code security)

## 10. Bài kiểm tra quy trình (làm cho cả nhóm xem)

```bash
git switch develop && git pull
git switch -c chore/test-workflow-<tên>
echo "- [x] Kiểm tra quy trình" >> CHANGELOG.md
git add CHANGELOG.md
git commit -m "chore(docs): kiểm tra quy trình PR"
git push -u origin HEAD
gh pr create --base develop --fill
```

Kỳ vọng: PR **không merge được** cho tới khi có 1 approval + CI xanh. Đó là bằng chứng
hàng rào hoạt động.
