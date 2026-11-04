# Skills — hướng dẫn theo loại việc

> Mỗi thư mục là một skill: `SKILL.md` gồm frontmatter `name` + `description` (mô tả **khi nào
> dùng**) và phần thân là quy tắc thực thi. Định dạng tương thích với chuẩn `SKILL.md` đang
> được Claude Code / nhiều agent CLI dùng.
>
> **Đọc skill trước khi viết code**, không phải sau. Khi mâu thuẫn với `WORKFLOW.md` → `WORKFLOW.md` thắng.

## Danh sách

| Skill | Dùng khi | Người phụ trách | Dòng |
|---|---|---|---|
| [`fastapi-endpoint`](fastapi-endpoint/SKILL.md) | Thêm/sửa endpoint, test route | A | ~100 |
| [`sqlalchemy-model`](sqlalchemy-model/SKILL.md) | Thêm bảng/cột, migration, seed | B | ~130 |
| [`pyside6-screen`](pyside6-screen/SKILL.md) | Làm màn hình, form, trạng thái UI | C | ~90 |
| [`ui-design`](ui-design/SKILL.md) | Bố cục, màu, font, chống "AI slop" | C (+ cả nhóm review) | ~150 |
| [`pytest-db`](pytest-db/SKILL.md) | Fixture DB, test API, test hồi quy | A/B | ~120 |
| [`win-installer`](win-installer/SKILL.md) | Build `.exe`, lỗi đóng gói | D | ~130 |
| [`report-export`](report-export/SKILL.md) | Xuất Excel/PDF, in hoá đơn | B/C | ~110 |
| [`security`](security/SKILL.md) | Auth, phân quyền, review trước deploy | Cả nhóm (D review) | ~120 |

## Quy ước viết skill mới

1. Tên: `<động-từ>-<đối-tượng>` hoặc `<lĩnh-vực>` — thống nhất tiếng Anh, không dấu.
2. `description` phải nêu **khi nào dùng**, không chỉ mô tả nội dung (đây là thứ agent dùng để chọn skill).
3. Bắt đầu bằng **bất biến / điều cấm** — thứ hay bị làm sai nhất lên đầu.
4. Có **khuôn mẫu code** copy được, không chỉ mô tả bằng lời.
5. Kết thúc bằng **checklist** tick được.
6. Nêu rõ liên quan tới skill khác nếu có (VD `pyside6-screen` → `ui-design`).
7. Giữ dưới ~150 dòng. Skill dài quá sẽ bị đọc lướt.

## Nguyên tắc: skill mô tả **dự án này**, không phải kiến thức chung

- Đúng đường dẫn thật (`api/routers/`, `gui/theme.py`, `db/schema.sql`).
- Đúng quyết định đã chốt (`DECIMAL(12,0)`, cổng 3307, `data/meta/error`).
- Trích dẫn `WORKFLOW.md` mục nào thay vì lặp lại toàn bộ.

## Nguồn tham khảo khi viết

- Chuẩn `SKILL.md` + ví dụ chính thức: [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official)
- Chống "AI slop" trong thiết kế: [anti-ai-slop rules](https://github.com/freekmurze/dotfiles/blob/fe89482ce432f76e750885c4cdb29f88155c4cb7/config/claude/skills/swiftui-design/references/anti-ai-slop.md), [The Tells](https://labs.iovstudio.kr/papers/ai-design-tells.pdf)

> ⚠️ Kho skill công khai (awesome-skills, claudeskills…) chất lượng rất không đồng đều và phần
> lớn viết cho stack web/JS. Dùng để **đọc ý tưởng**, rồi tự viết bản khớp dự án. Dán nguyên
> code lạ vào bài là vi phạm điều kiện "tự làm" của môn học.
