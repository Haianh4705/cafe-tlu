#!/usr/bin/env bash
# Việc tiếp theo của bạn, lấy từ Issue được gán trên GitHub.
#
#   make next
#
# Thứ tự = milestone (W1 trước W2…) rồi tới số Issue. Issue được tạo theo đúng
# thứ tự phụ thuộc nên số nhỏ hơn = làm trước (xem docs/plan.md).
set -uo pipefail

line() { printf '%s\n' "──────────────────────────────────────────────────────────────"; }

if ! command -v gh >/dev/null 2>&1; then
  cat <<'EOF'
❌ Chưa có GitHub CLI (gh).

   macOS  : brew install gh
   Windows: winget install GitHub.cli

   Chưa cài được cũng không sao — mở trực tiếp trên GitHub:
   • Bảng điều khiển tuần : issue "W<n> — Bảng điều khiển tuần <n>"
   • Việc của bạn         : github.com/Haianh4705/cafe-tlu/issues?q=assignee:@me
EOF
  exit 1
fi

if ! login=$(gh api user --jq .login 2>/dev/null); then
  printf '❌ gh chưa đăng nhập. Chạy: gh auth login\n'
  exit 1
fi

# Cho phép xem việc của người khác: bash scripts/next_task.sh <username>
who=${1:-$login}

rows=$(gh issue list --assignee "$who" --state open --limit 50 \
  --json number,title,milestone,labels,url \
  --jq '
    def skill:
      if . == "api" then "fastapi-endpoint"
      elif . == "db" then "sqlalchemy-model"
      elif . == "gui" then "pyside6-screen + ui-design"
      elif . == "infra" then "win-installer"
      elif . == "report" then "report-export"
      else "—" end;
    sort_by([ (.milestone.title // "Z9"), .number ])
    | .[]
    | select((.labels[0].name // "") != "tracking")
    | (.labels[0].name // "") as $label
    | [ (.milestone.title // "—"), (.number | tostring), $label,
        .title, .url, ($label | skill) ]
    | @tsv' 2>/dev/null)

if [ -z "$rows" ]; then
  line
  printf '🎉 @%s không còn việc nào được gán.\n\n' "$who"
  printf 'Hỏi D để nhận việc tiếp, hoặc tự nhận một Issue đang mở:\n'
  printf '  gh issue list --state open --limit 20\n'
  line
  exit 0
fi

first=$(printf '%s\n' "$rows" | head -1)
rest=$(printf '%s\n' "$rows" | tail -n +2)

printf '\n'
line
printf 'VIỆC TIẾP THEO CỦA @%s\n' "$who"
line
printf '%s\n' "$first" | awk -F'\t' '{
  printf "  #%s  [%s]  %s\n", $2, $1, $4
  printf "  Nhãn           : %s\n", $3
  printf "  Skill phải đọc : %s\n", $6
  printf "  Mở issue       : %s\n", $5
}'

if [ -n "$rest" ]; then
  printf '\n'
  line
  printf 'CÒN LẠI (làm theo đúng thứ tự này)\n'
  line
  printf '%s\n' "$rest" | awk -F'\t' '{
    printf "  %d.  #%s  [%s]  %s\n", NR + 1, $2, $1, $4
  }'
fi

cat <<'EOF'

──────────────────────────────────────────────────────────────
TRƯỚC KHI CODE
  1. Đọc issue: mục "Việc cần làm" + "Tiêu chí nghiệm thu"
  2. Đọc skill ghi ở trên  (.claude/skills/<tên>/SKILL.md)
  3. Đọc skill `minimal-change` (áp cho mọi việc)
  4. git switch develop && git pull --ff-only
     git switch -c feature/<scope>-<slug>-<tên>

KHI XONG
  make check → PR vào develop → cần 1 approval + CI xanh
  Điền mục "Giải thích được" 3 câu trong PR (docs/defense.md)
  Ghi 1–3 dòng vào docs/log/<vai>.md  (việc đã làm + AI đã hỗ trợ gì)
──────────────────────────────────────────────────────────────
EOF
