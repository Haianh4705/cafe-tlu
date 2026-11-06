---
name: fastapi-endpoint
description: Thêm hoặc sửa một endpoint FastAPI trong dự án CafeTLU (api/). Dùng khi được giao việc kiểu "thêm API X", "làm chức năng backend Y", "sửa endpoint Z", hoặc khi phải viết test cho một route.
---

# Thêm endpoint FastAPI

## Trước khi viết dòng nào

1. Đọc `docs/api-contract.md` — endpoint đó đã có trong bảng chưa? Nếu có, **làm đúng như bảng**.
2. Đọc mục mô tả liên quan trong `docs/erd.md` để biết bảng/cột (do B thiết kế — nếu còn khung thì hỏi B) được dùng.
3. Kiểm tra `shared/error_codes.py` — đã có mã lỗi cần dùng chưa?
4. Nếu endpoint chưa có trong hợp đồng: thêm dòng vào `docs/api-contract.md` **trong cùng PR**,
   và báo nhóm (C cần biết để gọi).

## Kiến trúc bắt buộc

```
api/routers/<resource>.py   → chỉ: validate (Pydantic) + gọi service + trả response
api/services/<resource>.py  → toàn bộ nghiệp vụ, transaction, kiểm quyền
api/models/<resource>.py    → SQLAlchemy, không chứa logic
api/schemas/<resource>.py   → Pydantic request/response
```

**Cấm:**
- SQL/câu query trong router.
- Gọi service này từ service khác theo vòng tròn.
- Trả thẳng ORM object ra ngoài (phải qua Pydantic schema).
- `except Exception: pass`.
- `print()` — dùng `logger`.

## Khuôn mẫu

```python
# api/routers/products.py
router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=ProductListResponse)
def list_products(
    search: str | None = None,
    category_id: int | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "staff")),
) -> ProductListResponse:
    items, total = product_service.list_products(
        db, search=search, category_id=category_id, page=page, page_size=page_size
    )
    return ProductListResponse(
        data=[ProductOut.model_validate(i) for i in items],
        meta=PageMeta(page=page, page_size=page_size, total=total),
    )
```

```python
# api/services/products.py
def create_product(db: Session, payload: ProductCreate) -> Product:
    if db.scalar(select(Product).where(Product.name == payload.name, Product.is_deleted == 0)):
        raise AppError(ErrorCode.PRODUCT_NAME_DUPLICATED, "Tên món đã tồn tại")
    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()  # hoặc để transaction ở tầng dependency
    db.refresh(product)
    return product
```

## Quy tắc phân quyền

- Mọi route (trừ `/health`, `/auth/login`) phải có `Depends(get_current_user)`.
- Kiểm quyền **ở server** bằng `require_role(...)`. Ẩn nút ở GUI chỉ là UX.
- Sai quyền → `403 FORBIDDEN`, thiếu token → `401 UNAUTHENTICATED`.

## Test kèm theo (bắt buộc)

Mỗi endpoint mới cần **ít nhất 3 test**: happy path, dữ liệu sai (422), sai quyền (403/401).
Xem skill `pytest-db` để viết fixture.

```python
def test_create_product_duplicate_name_returns_409(client, auth_admin, sample_product):
    r = client.post(
        "/api/v1/products",
        json={
            "name": sample_product.name,
            "price": 30000,
            "category_id": sample_product.category_id,
        },
        headers=auth_admin,
    )
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "PRODUCT_NAME_DUPLICATED"
```

## Checklist trước khi mở PR

- [ ] Endpoint có trong `docs/api-contract.md`, trạng thái đã đánh dấu
- [ ] Router không chứa SQL; logic nằm ở service
- [ ] Response đúng envelope `data` / `meta`
- [ ] Lỗi dùng `AppError` + mã trong `shared/error_codes.py`, message tiếng Việt
- [ ] Có `Depends` xác thực + kiểm quyền
- [ ] Phân trang cho endpoint danh sách (mặc định 20, tối đa 100)
- [ ] ≥ 3 test, `make test` xanh
- [ ] Swagger `/docs` hiển thị đúng
