---
name: security
description: Rà soát bảo mật cho CafeTLU — xác thực, phân quyền, secret, dữ liệu, deploy, đóng gói. Dùng khi làm login/phân quyền, khi thêm endpoint ghi dữ liệu, trước khi deploy (cổng G4), trước khi nộp bài (G6), hoặc khi nghi ngờ có lỗ hổng.
---

# Bảo mật

## Mô hình mối đe doạ của dự án này (thực tế, không lý thuyết)

| Mối đe doạ | Xảy ra thế nào | Chặn bằng |
|---|---|---|
| Lộ mật khẩu DB | Commit `.env`, hardcode trong code | `.gitignore` + chỉ đọc từ env + quét trước khi push |
| Nhân viên làm việc ngoài quyền | Sửa giá, xoá đơn, xem doanh thu | RBAC **kiểm ở server**, không chỉ ẩn nút |
| Đoán mật khẩu | `/auth/login` không giới hạn | Rate limit + hash bcrypt |
| SQL injection | Nối chuỗi vào câu SQL | Luôn dùng ORM / bind param |
| Sửa dữ liệu người khác (IDOR) | Đổi `id` trong request | Kiểm quyền trên **từng resource** |
| Token bị lộ trên máy | Lưu token plaintext trong file config | `keyring` của OS, hoặc không lưu |
| Bản cài bị tráo | Auto-update tải file không kiểm tra | HTTPS + checksum; ký số nếu kịp |

## 1. Bí mật & cấu hình

- `.env` **không bao giờ** vào Git. Chỉ `.env.example` với giá trị giả.
- Cấm hardcode: mật khẩu, `JWT_SECRET`, API key, đường dẫn tuyệt đối có tên người dùng.
- `JWT_SECRET` phải là chuỗi **ngẫu nhiên ≥ 32 byte** khi deploy:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

- Nếu lỡ commit secret: báo nhóm trong 5 phút, **đổi secret ngay**, rồi xoá khỏi lịch sử
  (`git filter-repo`) — xoá ở commit mới là **không đủ**.

## 2. Xác thực

- Mật khẩu: **bcrypt cost ≥ 12**. Cấm MD5/SHA1/plaintext.
- Không giới hạn độ dài mật khẩu ở mức thấp (tối thiểu 8, tối đa ≥ 72 — giới hạn của bcrypt).
- Đăng nhập sai: trả thông điệp **giống nhau** cho "sai tài khoản" và "sai mật khẩu".
- Giới hạn thử: 5 lần/phút/IP + khoá tạm sau N lần sai. Ghi `audit_logs` mọi lần thất bại.
- Access token 30 phút; refresh 7 ngày. Logout phải thu hồi được refresh token.
- Trên desktop: **không** lưu mật khẩu; token (nếu lưu) vào `keyring`, không vào `.json` thường.

## 3. Phân quyền (nguồn lỗi số 1 của đồ án sinh viên)

- Kiểm quyền **ở server**, mỗi request. Ẩn menu ở GUI chỉ là trải nghiệm, không phải bảo mật.
- Kiểm quyền trên **từng bản ghi**, không chỉ theo route:
  - Nhân viên A không được sửa đơn của ca khác nếu nghiệp vụ quy định vậy.
  - Luôn kiểm `resource.owner_id == current_user.id` khi áp dụng.
- Nguyên tắc quyền tối thiểu: role nào chỉ có đúng quyền cần.
- Trả `403 FORBIDDEN`, **không** trả `404` giả để "che giấu" (trừ khi cố ý chống dò).

## 4. Đầu vào

- Mọi input qua Pydantic: kiểu, độ dài, khoảng giá trị, enum. Cấm tin client.
- Truy vấn: ORM hoặc `text()` + bind param. **Cấm** f-string/nối chuỗi SQL.
- Upload ảnh món (mốc 8): kiểm **định dạng thật** (magic bytes), giới hạn ≤ 2MB, đổi tên file
  (không dùng tên gốc → chặn path traversal), lưu ngoài thư mục code.
- Không nhận giá tiền từ client ở endpoint thanh toán — **tính lại ở server**.

## 5. Dữ liệu & log

- Log **cấm** chứa: mật khẩu, token, số CCCD/SĐT đầy đủ. Che bớt (`*****1234`).
- Thao tác quan trọng phải vào `audit_logs`: đổi giá, xoá món, sửa quyền, huỷ đơn,
  thanh toán, đăng nhập thất bại.
- `old_value`/`new_value` dạng JSON nhưng **không** chứa trường nhạy cảm.
- Backup: file `.sql.gz` không commit, không chia sẻ qua chat công khai.

## 6. Deploy & đóng gói

- HTTPS bắt buộc; không mở cổng DB ra Internet (chỉ 127.0.0.1 hoặc mạng nội bộ).
- DB user của app **không phải `root`** — cấp đúng quyền trên đúng schema.
- `APP_ENV=prod`: tắt `/docs` công khai nếu không cần, tắt debug, không trả stack trace.
- CORS chỉ cho origin cần thiết (nếu có web/QR order sau này).
- Auto-update: tải qua HTTPS, kiểm tra version + checksum. Không chạy file tải về mà không xác thực.

## 7. Phụ thuộc

```bash
pip-audit                                  # quét CVE trong requirements
grep -rn "eval(\|exec(\|pickle.loads" --include=*.py .
```

- Không thêm thư viện không rõ nguồn chỉ vì "tiện" — mỗi thư viện là một bề mặt tấn công.
- Ghim phiên bản; không dùng `latest` trong production.

## Checklist trước cổng G4 (deploy) và G6 (nộp)

- [ ] `git ls-files | grep -E '(^|/)\.env$|\.pem$|\.key$'` → **rỗng**
- [ ] `JWT_SECRET` sinh ngẫu nhiên, không phải giá trị mặc định trong `.env.example`
- [ ] Mật khẩu trong seed đã đổi cho môi trường thật
- [ ] Mọi route (trừ `/health`, `/auth/login`) có xác thực
- [ ] Có test chứng minh role `staff` bị `403` khi gọi API của `admin`
- [ ] Không có câu SQL nối chuỗi
- [ ] Login có giới hạn số lần thử
- [ ] `audit_logs` ghi được ít nhất 5 loại thao tác quan trọng
- [ ] Log không lộ mật khẩu/token
- [ ] `pip-audit` không còn lỗ hổng mức high/critical
- [ ] DB user của app không phải `root`; cổng 3306 không mở ra ngoài
- [ ] Trang lỗi production không hiện stack trace

## Khi phát hiện lỗ hổng

1. **Không** mở Issue công khai mô tả chi tiết cách khai thác (repo đang public).
2. Báo riêng cho D, ghi mức độ: chặn demo / rò dữ liệu / chỉ là cấu hình.
3. Tạo nhánh `fix/security-...` riêng, không gộp vào PR tính năng.
4. Sau khi sửa: thêm test hồi quy + ghi vào `CHANGELOG.md` mục `Security`.
