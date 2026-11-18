# `infra/` — Triển khai

**Phạm vi:** sửa theo Issue chức năng được giao (`ADR-014`) — đọc skill `win-installer` + `security` trước khi sửa, giữ kiến trúc `gui → api → db`.

## Đặt gì ở đây

| File | Việc |
|---|---|
| `Dockerfile` | Đóng gói backend FastAPI (image chạy trên server) |
| `docker-compose.prod.yml` | Compose cho môi trường thật: api + mysql + nginx, không map cổng DB ra ngoài |
| `deploy.md` | Hướng dẫn deploy **step-by-step** (GV và cả nhóm đọc được) |
| `nginx.conf` | Reverse proxy + HTTPS (nếu dùng VPS) |
| `.env.prod.example` | Mẫu biến môi trường production — **giá trị giả**, không commit `.env` thật |

## KHÔNG đặt

- `docker-compose.yml` của dev (đã ở thư mục gốc)
- Mật khẩu, key, chứng chỉ TLS thật
- Backup database

## Quy ước

Đọc skill `win-installer` + `security` (mục Deploy). Trước khi deploy:
`pip-audit` sạch, `JWT_SECRET` sinh mới, DB user **không phải root**, cổng 3306 không mở ra ngoài.
Mỗi bước deploy phải chụp ảnh → `docs/screenshots/deploy/`.
