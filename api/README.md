# `api/` — Backend FastAPI

**Owner:** A · **Bắt đầu:** cổng G1 · **Trạng thái:** 🟡 khung trống, chờ code

## Cấu trúc (tạo dần khi code)

```
api/
├── main.py          # tạo app, mount router, exception handler
├── core/            # config, db (engine + get_db), security (JWT, require_role)
├── routers/         # MỎNG: validate + gọi service + trả response
├── services/        # toàn bộ nghiệp vụ, transaction
├── models/          # SQLAlchemy (B review mọi thay đổi)
└── schemas/         # Pydantic request/response
```

## KHÔNG đặt

- Câu SQL hoặc business logic trong `routers/`
- Truy cập DB trực tiếp từ `gui/` (không được import chéo)
- Code GUI, script build

## Quy ước

Đọc skill `fastapi-endpoint`. Response luôn theo envelope `data` / `meta` / `error.code`
(`WORKFLOW.md` mục 9.3). Mã lỗi khai báo ở `shared/error_codes.py`.
Mỗi endpoint mới ≥ 3 test. Kiểm tra: `make api` → <http://127.0.0.1:8000/docs>.
