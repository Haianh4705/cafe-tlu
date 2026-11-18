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

- **Ngày:** 2026-11-04 · **Trạng thái:** 🟡 Đề xuất (chốt ở buổi sync đầu tiên)
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
- **Hệ quả:** đường ống đóng gói phụ thuộc CI → phải build thử ngay G1 để phát hiện sớm;
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

## ADR-008: Áp dụng tối giản có kiểm soát (lấy cảm hứng từ Ponytail)

- **Ngày:** 2026-11-05 · **Người quyết định:** D · **Trạng thái:** 🟡 Đề xuất
- **Bối cảnh:** lỗi phổ biến của đồ án dùng AI là **xây quá mức** — widget tự vẽ thay vì dùng Qt có sẵn,
  abstraction "để sau này", cài thư viện cho vài dòng. Hậu quả: vỡ lúc tích hợp, không kịp sửa.
- **Quyết định:** thêm skill `minimal-change` (bậc thang YAGNI, Việt hoá) + quy ước comment
  `shortcut: <giới hạn>, <khi nào nâng cấp>`; reviewer phải **đọc cả vùng code bị chạm, không chỉ diff**.
- **Đã cân nhắc:** cài nguyên [Ponytail](https://github.com/DietrichGebert/ponytail) (bật "lazy senior dev"
  cho mọi session → ăn vào phần báo cáo/tài liệu mà GV chấm); không làm gì (giữ nguyên lỗi xây quá mức).
- **Hệ quả:** skill quyết **cách làm**, không quyết **làm gì** — phạm vi vẫn do Issue/Definition of Ready.
  Yêu cầu mơ hồ vẫn phải **hỏi trước** (WORKFLOW mục 9), không tự lấy bản nhỏ nhất.
  Không được cắt: validate, xử lý lỗi, kiểm quyền server, test, ảnh chụp, CHANGELOG, báo cáo handoff.

---

## ADR-009: Phân công vai trò A/B/C/D

- **Ngày:** 2026-11-06 · **Người quyết định:** cả nhóm · **Trạng thái:** 🔄 Chấp nhận một phần (quy tắc khoá vùng thư mục và bắt buộc 1 approval được thay thế bởi [ADR-014](#adr-014-giao-thành-viên-theo-chức-năng-qua-issuepr-và-bỏ-bắt-buộc-approve))
- **Bối cảnh:** nhóm 4 người, ban đầu thử chia theo **tầng kiến trúc** để bốn người code song song.
- **Quyết định ban đầu:** A (`api/`, `shared/`), B (`db/`, `api/services/reports.py`), C (`gui/`, `assets/`), D (`infra/`, `installer/`, `.github/`, `docs/`, `report/`).
- **Hệ quả cập nhật (2026-11-18):** khi bước vào G2/G3 và có thành viên vắng/lệch tiến độ, việc khoá cứng thư mục + bắt buộc 1 approval làm nghẽn toàn bộ luồng. Nhóm giữ danh nghĩa vai A/B/C/D cho nhật ký cá nhân (`docs/log/<vai>.md`) và thế mạnh tham khảo, còn phân công thực tế chuyển sang **giao theo chức năng trên Issue** và **bỏ bắt buộc approve** theo **ADR-014**.

---

## ADR-010: Nhật ký cá nhân + AI (`docs/log/<vai>.md`)

- **Ngày:** 2026-11-11 · **Người quyết định:** D · **Trạng thái:** ✅ Chấp nhận
- **Bối cảnh:** đề bài **copy = 0 điểm**, GV hỏi bất kỳ phần nào và hay hỏi "AI viết bao nhiêu". Nhóm
  dùng AI cho hầu hết việc, nhưng bằng chứng nằm rải rác trong chat, commit message và trí nhớ — đến
  lúc bảo vệ thì không dựng lại được.
- **Quyết định:** mỗi người giữ **một** file `docs/log/<vai>.md` (A/B/C/D) gồm 6 mục: phụ trách gì ·
  việc đã làm (kèm commit/PR) · AI đã làm gì và mình sửa/kiểm chứng gì · câu hỏi GV hay hỏi · phần
  chưa hiểu · nhật ký theo cổng. Cập nhật **trong PR**, 3–5 phút; file trống ở thời điểm cổng = cổng
  chưa xanh.
- **Đã cân nhắc:** chỉ dựa vào `git log` + PR (không ghi được "AI làm gì", "vì sao chọn cách khác");
  một file chung cho cả nhóm (conflict liên tục, dễ ghi hộ); bắt viết báo cáo ngay từ G1 (nặng, viết
  trước khi có dữ liệu).
- **Hệ quả:** thêm 5 phút/PR và 15 phút trước mỗi cổng. Đổi lại: mỗi người có sẵn đề cương ôn + bằng
  chứng khi bị hỏi; GV thấy rõ phần nào do AI hỗ trợ. **Không** dùng nhật ký để thay báo cáo.

---

## ADR-011: `/health` là ngoại lệ duy nhất của envelope mục 9.3

- **Ngày:** 2026-11-17 · **Người quyết định:** D · **Trạng thái:** ✅ Chấp nhận
- **Bối cảnh:** `WORKFLOW.md` §9.3 bắt mọi response phải bọc `data`/`meta`/`error`. Nhưng `/health` bị
  đọc bởi ba thứ **không phải GUI**: `healthcheck` của Docker Compose, `make doctor`, và probe sau khi
  cài trên Windows. Cả ba đều chỉ cần biết "sống/chết", phải parse được bằng `curl`/`jq`/Python một
  dòng. Bọc envelope khiến mỗi nơi phải biết thêm một tầng định dạng, và khi DB chết thì chính
  endpoint dùng để chẩn đoán lại trả về cấu trúc khác — `make doctor` báo sai.
- **Quyết định:** `/health` và bí danh `/api/v1/health` trả **phẳng**
  `{"status": "ok|degraded", "version": "<shared/version.py>", "database": "ok|error"}`; HTTP 200 khi
  DB thông, 503 khi DB lỗi. **Không** dùng envelope kể cả ở nhánh 503. Đây là ngoại lệ **duy nhất**;
  mọi endpoint khác giữ nguyên §9.3.
- **Đã cân nhắc:** (a) ép `/health` theo envelope cho "sạch quy chuẩn" → mọi consumer phải sửa, và
  healthcheck của Docker phải viết script riêng; (b) tách `/health` ra thành endpoint ngoài `/api/v1`
  và không tính là API → vẫn phải ghi ở đâu đó, dễ sinh endpoint thứ hai lách luật; (c) để mỗi service
  tự chọn → không thống nhất được, đúng thứ §9.3 sinh ra để chặn.
- **Hệ quả:** §9.3 có thêm mục "Ngoại lệ" ghi rõ ca này. Test `tests/test_api_health.py` phải khẳng
  định trả phẳng **và** đúng 200/503. Ai thêm endpoint kiểu `/health` thứ hai phải mở ADR mới. Bộ cài
  và `make doctor` được phép đọc thẳng `status`/`database` mà không qua `gui/api_client.py`.

---

## ADR-012: `make doctor` bắt buộc trên máy A, C, D — không tính máy B vào cổng G1

- **Ngày:** 2026-11-18 · **Người quyết định:** D (@Haianh4705) · **Trạng thái:** ⚠️ Thay thế một phần bởi ADR-015
- **Bối cảnh:** điều kiện ra G1 ghi "4/4 máy `make doctor` xanh". Nhưng B chỉ làm `db/` +
  `api/services/reports.py` — phần của B kiểm chứng được bằng `db/verify_seed.sql` (21 phép kiểm
  PASS/FAIL) trên **bất kỳ** máy nào có Docker, không cần môi trường riêng của B. B vắng từ 11-11,
  nên điều kiện 4/4 biến một cổng kỹ thuật thành phụ thuộc vào một người không có mặt.
- **Quyết định:** `make doctor` phải xanh trên **3/3 máy A, C, D**. Máy B **không** nằm trong điều
  kiện ra G1; nếu B chạy được thì ghi nhận, không chặn.
- **Đã cân nhắc:** giữ 4/4 → G1 kẹt vô thời hạn mà không thêm thông tin (B không chạy `api/`/`gui/`);
  bỏ hẳn điều kiện doctor → mất bằng chứng "môi trường giống nhau", ba lỗi môi trường đã gặp
  (Docker CLI không có trong PATH, MySQL `running` nhưng chưa nhận truy vấn, cổng 3307 bị chiếm)
  sẽ quay lại.
- **Hệ quả:** `README.md` (bảng cổng), `docs/plan.md`, `docs/defense-D.md`, `WORKFLOW.md` §16.3 ghi
  "3/3 (A, C, D)". `make doctor` vẫn **bắt buộc** với ai chạm `api/`, `gui/`, `installer/`, `.github/`
  trước khi mở PR — quy tắc này không đổi.

---

## ADR-013: Lưu refresh token trong bảng `refresh_tokens` (thu hồi được khi logout)

- **Ngày:** 2026-11-18 · **Người quyết định:** D (@Haianh4705), theo đề xuất của A · **Trạng thái:** Chấp nhận
- **Bối cảnh:** hợp đồng API có `POST /auth/refresh` (#3) và `POST /auth/logout` — "Thu hồi token" (#4),
  `.claude/skills/security/SKILL.md` §2 ghi *"Logout phải thu hồi được refresh token"*, `WORKFLOW.md`
  §547 ghi refresh 7 ngày. Nhưng ERD v1 (9 bảng) **không có** chỗ lưu trạng thái phiên, nên nếu chỉ dùng
  JWT tự chứa thì logout không rút lại được gì. B vắng từ 11-11 → D làm phần schema thay B (như #55).
- **Quyết định:** thêm bảng thứ 10 `refresh_tokens` (`token_hash` SHA-256 UNIQUE, `expires_at`, `revoked_at`,
  `replaced_by_id` cho rotation, `user_agent`, `created_at`; FK `users` CASCADE, FK tự thân SET NULL;
  2 `CHECK` chặn `expires_at`/`revoked_at` phi lý). **Chỉ lưu hash**, không lưu token thô. Seed không tạo token.
- **Đã cân nhắc:** *không lưu DB* (logout chỉ xoá phía client) → trái luật security + trái hợp đồng #4, token
  lộ dùng được tới 7 ngày; *denylist trong RAM* → mất khi restart, không kiểm chứng được; *chỉ lưu denylist
  token đã thu hồi* → vẫn 1 bảng nhưng logic tra cứu khó hơn mà lợi ích không đáng (bảng này rất nhỏ).
- **Hệ quả:** ERD thành **10 bảng** (`docs/erd.md` + từ điển + bất biến §3.3 mục 6); A thêm
  `api/models/refresh_token.py` trong #22 và dùng bảng này cho `/auth/refresh` + `/auth/logout`;
  `db/verify_seed.sql` có thêm 2 phép kiểm (bảng tồn tại, rỗng sau seed); `report/03` cập nhật số bảng.

---

## ADR-014: Giao thành viên theo chức năng qua Issue/PR và bỏ bắt buộc approve

- **Ngày:** 2026-11-18 · **Người quyết định:** D (@Haianh4705) · **Trạng thái:** ✅ Chấp nhận
- **Bối cảnh:** quy trình cũ (ADR-009) khoá cứng thư mục theo vai A/B/C/D (`> 10 dòng` ngoài vùng
  phải hỏi) và bắt buộc PR phải chờ ≥ 1–2 approval của owner khác trước khi merge. Thực tế ở G1–G2,
  khi thành viên bận hoặc vắng (B vắng từ 11-11), các PR sửa lỗi hoặc nối xuyên tầng (`db/` → `api/`
  → `gui/`) bị kẹt hàng chờ duyệt dù CI đã xanh, trong khi nhiều chức năng G3–G5 cần một người làm
  trọn vẹn end-to-end mới nhanh khớp hợp đồng.
- **Quyết định:**
  1. **Giao thành viên theo chức năng cần làm:** mở khoá ranh giới thư mục cứng. Công việc được chia
     theo từng chức năng trên GitHub Issue; người nhận Issue chức năng được sửa trọn gói `db/` +
     `api/` + `gui/` + `shared/` + `tests/` + `docs/` để chức năng chạy end-to-end, **nhưng bắt
     buộc giữ nguyên kiến trúc một chiều `gui → api → db`** (ADR-006).
  2. **Bỏ bắt buộc approve:** cấu hình GitHub Branch Protection trên `develop` và `main` với
     `required_approving_review_count = 0` và không bật Code Owner review; tác giả **được tự Squash
     & Merge** ngay khi CI xanh (`Lint & format`, `Test` với `strict: true`) và hoàn thành đủ
     checklist (test, 3 câu bảo vệ, nhật ký cá nhân `docs/log/<vai>.md`), rồi nghiệm thu trên
     `develop` và đóng Issue.
  3. **100% chức năng đi qua Issue & PR:** bật `enforce_admins: true` và giữ `required_pull_request_reviews`
     trên cả `develop` và `main` để cấm tuyệt đối push trực tiếp (kể cả admin).
- **Đã cân nhắc:** giữ nguyên 1 approval + để D dùng `--admin` lách khi kẹt (tạo lỗ hổng quy trình
  như đã nêu ở `docs/defense-D.md`, dễ làm thành viên lệ thuộc D bấm giúp); giữ khoá thư mục và tách
  mọi chức năng nhỏ thành 3 PR rời A/B/C (chậm tích hợp, dễ lệch schema DTO giữa GUI và API).
- **Hệ quả:** `WORKFLOW.md` v2.0, `AGENTS.md`, `CONTRIBUTING.md`, `README.md`, `docs/workflow.md`,
  `docs/plan.md`, `scripts/next_task.sh`, `.github/*` và README các thư mục con đồng bộ theo hướng dẫn
  theo tầng kỹ thuật thay vì khoá quyền sở hữu. Review đồng đội vẫn được khuyến khích ở thay đổi
  lớn nhưng không chặn merge.

---

## ADR-015: Cổng G1 chỉ yêu cầu `make doctor` trên máy A và D

- **Ngày:** 2026-11-18 · **Người quyết định:** D (@Haianh4705) · **Trạng thái:** ✅ Chấp nhận
- **Bối cảnh:** Issue #33 đang chờ kết quả `make doctor` của C dù A và D đã có output xanh; D xác nhận C không cần chạy lệnh này để hoàn tất G1.
- **Quyết định:** điều kiện môi trường của G1 là `make doctor` xanh trên A và D; C được miễn riêng ở cổng G1, B tiếp tục không tính theo ADR-012.
- **Đã cân nhắc:** giữ yêu cầu A/C/D sẽ chặn G1 dù chủ dự án đã chọn A và D làm hai máy nghiệm thu; bỏ toàn bộ `make doctor` sẽ mất kiểm tra môi trường.
- **Hệ quả:** cập nhật `README.md`, `docs/plan.md`, `docs/workflow.md`, `docs/defense-D.md`, `WORKFLOW.md` §16.3 và Issue #33; quy tắc `make doctor` trước PR của ADR-012 vẫn giữ nguyên.

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
