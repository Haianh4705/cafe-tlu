# Nhật ký quyết định kỹ thuật (ADR-lite)

> Mỗi quyết định **3–5 dòng**: chọn gì · vì sao · đã cân nhắc gì khác · hệ quả.
> Quyết định đã ở trạng thái **Chấp nhận** thì không mở lại trừ khi có dữ liệu mới.
> Xem `WORKFLOW.md` mục 18.4.

**Trạng thái:** `Đề xuất` → `Chấp nhận` → (tuỳ chọn) `Thay thế bởi ADR-xxx`

---

## ADR-001: Nhóm 4 thành viên

- **Ngày:** 2026-11-04 · **Người quyết định:** cả nhóm · **Trạng thái:** ✅ Chấp nhận
- **Bối cảnh:** đề bài quy định tối đa 2–3 người/đề tài.
- **Quyết định:** làm nhóm 4 người, **đã được GV đồng ý bằng tin nhắn đính kèm khi giao bài**.
- **Hệ quả:** khối lượng chia theo 4 vai (A/B/C/D, xem `WORKFLOW.md` mục 3). Không cần bàn lại.

## ADR-002: Đề tài đã đăng ký

- **Ngày:** 2026-11-04 · **Trạng thái:** ✅ Chấp nhận
- **Quyết định:** đề tài 5 — ứng dụng Desktop quản lý quán café TLU, MySQL.
- **Ghi chú:** mỗi lớp tối đa 2 nhóm/đề tài → đã đăng ký xong, không còn rủi ro trùng.

## ADR-003: Stack kỹ thuật

- **Ngày:** 2026-11-04 · **Trạng thái:** 🟡 Đề xuất (chốt ở buổi sync tuần 1)
- **Quyết định:** Python 3.12 · PySide6 6.8 · FastAPI 0.115 · MySQL 8.0 (Docker) · SQLAlchemy 2.0
- **Vì sao:** PySide6 cho phép giao diện đẹp + biểu đồ (tiêu chí mốc 8); FastAPI tách backend →
  thỏa "khuyến khích gọi API" và tạo được URL deploy cho mốc 9; MySQL theo đúng đề bài.
- **Đã cân nhắc:** Tkinter (nhẹ nhưng khó đẹp, chart kém), Flask (ít tính năng sẵn hơn FastAPI,
  không tự sinh Swagger), PostgreSQL (đề bài ghi MySQL).
- **Hệ quả:** installer nặng thêm ~60MB; cần Qt Designer cho layout; CI phải cài PySide6.

## ADR-004: MySQL chạy bằng Docker, cổng 3307

- **Ngày:** 2026-11-04 · **Trạng thái:** 🟡 Đề xuất
- **Quyết định:** dùng `docker compose` cho MySQL thay vì cài native; map cổng **3307** ở máy host.
- **Vì sao:** 4 máy (macOS + Windows) có môi trường giống nhau 100%; cổng 3307 tránh đụng MySQL
  cài sẵn; `reset-db` xoá sạch dễ dàng.
- **Đã cân nhắc:** MySQL native (khác phiên bản giữa các máy, gỡ cài đặt bẩn), SQLite (đề bài yêu cầu MySQL).
- **Hệ quả:** mọi người **bắt buộc** cài Docker Desktop; không ai được đổi cổng riêng.

## ADR-005: Build bộ cài Windows trên GitHub Actions

- **Ngày:** 2026-11-04 · **Trạng thái:** 🟡 Đề xuất
- **Bối cảnh:** đề bài bắt buộc có bộ cài `.exe`; phần lớn thành viên dùng macOS, không có máy Windows.
- **Quyết định:** build installer trên `windows-latest` của GitHub Actions khi push tag `v*`.
- **Đã cân nhắc:** VM Windows (tốn tài nguyên/bản quyền), mượn máy bạn (không tái lập được),
  bỏ bộ cài (mất điểm bắt buộc).
- **Hệ quả:** đường ống đóng gói phụ thuộc CI → phải build thử từ tuần 1 (cổng G1) để phát hiện sớm;
  đồng thời đây là minh chứng "CI/CD" cho mốc 9.

## ADR-006: Một backend API dùng chung cho GUI và (sau này) QR order

- **Ngày:** 2026-11-04 · **Trạng thái:** 🟡 Đề xuất
- **Quyết định:** GUI **không** kết nối MySQL trực tiếp, mọi truy cập qua REST API.
- **Vì sao:** đổi 1 chỗ áp dụng cho mọi client; kiểm tra phân quyền ở server; mở đường cho
  tính năng QR order ở mốc 10 mà không phải viết lại.
- **Đã cân nhắc:** GUI nối thẳng DB (nhanh hơn lúc đầu, nhưng không deploy được, không có
  REST API để trình diễn, mất điểm phần "gọi API").
- **Hệ quả:** phải chạy 2 tiến trình khi dev (`make up` + `make api` + `make gui`); cần
  `docs/api-contract.md` chốt sớm.

## ADR-007: Giao diện theo nhận diện Trường Đại học Thăng Long

- **Ngày:** 2026-11-05 · **Người quyết định:** C (đề xuất), cả nhóm duyệt · **Trạng thái:** 🟡 Đề xuất
- **Bối cảnh:** app là đồ án của trường; giao diện mặc định (xanh Qt, gradient tím) trông generic.
- **Quyết định:** dùng bảng màu lấy từ `thanglong.edu.vn` + logo chính thức:
  navy `#000066` (hành động) · đỏ logo `#F32409` (chỉ hành động phá huỷ) · tint `#F1F5FF` (hàng chọn).
  Header/sidebar navy, nội dung trắng. Font thay thế **Manrope** (font gốc `thangLongSans` là độc quyền).
- **Đã cân nhắc:** tự chọn palette riêng (mất liên hệ với trường, GV khó thấy "sản phẩm của TLU");
  dùng nguyên website style (web và desktop khác ngữ cảnh: website cần marketing, app cần dày dữ liệu).
- **Hệ quả:** màu/typography chỉ khai báo trong `gui/theme.py`; `red-logo` không dùng cho chữ < 18px
  (chỉ đạt AA-large — 4.14:1); không đóng gói font `thangLongSans` vào app.
  Chi tiết + token: `.claude/skills/ui-design/SKILL.md`.

---

## Mẫu thêm ADR mới

```markdown
## ADR-00X: <tiêu đề ngắn>

- **Ngày:** YYYY-MM-DD · **Người quyết định:** <ai> · **Trạng thái:** Đề xuất / Chấp nhận
- **Bối cảnh:** <vấn đề là gì, ràng buộc nào>
- **Quyết định:** <chọn gì>
- **Đã cân nhắc:** <phương án khác + vì sao loại>
- **Hệ quả:** <cái gì phải làm theo, cái gì hi sinh>
```
