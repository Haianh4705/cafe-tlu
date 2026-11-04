---
name: pytest-db
description: Viết test cho backend CafeTLU — fixture DB, dữ liệu mẫu, test API và service. Dùng khi được giao "viết test cho X", khi sửa bug phải kèm test tái hiện, hoặc khi test hiện tại bẩn dữ liệu / phụ thuộc thứ tự chạy.
---

# Test với cơ sở dữ liệu

## Nguyên tắc

1. **Mỗi test độc lập** — chạy riêng lẻ hay đảo thứ tự đều phải xanh.
2. **Không đụng DB dev.** Test dùng `cafe_tlu_test`, dựng/xoá trong fixture.
3. **Rollback sau mỗi test** — không để dữ liệu rò sang test sau.
4. **Không gọi mạng thật.** Mock HTTP của GUI; API dùng `TestClient` in-process.
5. **Một bug = một test tái hiện** (đỏ trước, xanh sau).
6. Cấm `time.sleep`, cấm phụ thuộc thời gian thực → dùng dữ liệu cố định hoặc `freezegun`.

## `tests/conftest.py` — khuôn mẫu

```python
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from fastapi.testclient import TestClient

from api.main import app
from api.core.db import get_db
from api.models.base import Base
from api.core.security import create_access_token, hash_password
from api.models.user import User, Role


@pytest.fixture(scope="session")
def engine():
    url = "mysql+pymysql://root:test_root@127.0.0.1:3306/cafe_tlu_test?charset=utf8mb4"
    eng = create_engine(url, pool_pre_ping=True)
    Base.metadata.drop_all(eng)
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)


@pytest.fixture
def db_session(engine) -> Session:
    """Bọc mỗi test trong 1 transaction lớn rồi rollback -> DB sạch."""
    connection = engine.connect()
    trans = connection.begin()
    session = sessionmaker(bind=connection, join_transaction_mode="create_savepoint")()
    try:
        yield session
    finally:
        session.close()
        trans.rollback()  # không cần xoá tay từng bảng
        connection.close()


@pytest.fixture
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
```

## Factory dữ liệu (đừng copy-paste object)

```python
# tests/factories.py
def make_product(db: Session, **kw) -> Product:
    defaults = dict(name="Trà đào cam sả", price=35000, unit="ly", category_id=make_category(db).id)
    product = Product(**{**defaults, **kw})
    db.add(product)
    db.flush()
    return product
```

Quy ước tên test: `test_<hành_vi>_<điều_kiện>_<kết_quả>` —
`test_create_product_duplicate_name_returns_409`.

## Ba lớp test

```python
@pytest.mark.unit
def test_calc_total_ignores_cancelled_items(): ...


@pytest.mark.api
def test_login_wrong_password_returns_401(client, seeded_user): ...


@pytest.mark.gui
def test_product_list_shows_empty_state_when_no_data(qtbot, fake_api): ...
```

Chạy: `pytest -m api` · `pytest -m "not gui"` (CI mặc định chạy hết).

## Bắt buộc cho bug fix

```python
def test_cannot_edit_paid_order(client, auth_staff, paid_order):
    r = client.patch(
        f"/api/v1/orders/{paid_order.id}/items/1", json={"quantity": 5}, headers=auth_staff
    )
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "ORDER_ALREADY_PAID"
```

Test này phải **đỏ trước** khi sửa. Nếu nó xanh ngay từ đầu → chưa tái hiện được bug.

## Checklist

- [ ] Test chạy được riêng: `pytest tests/test_x.py::test_y`
- [ ] Không để lại dữ liệu (chạy 2 lần liên tiếp vẫn xanh)
- [ ] Không truy cập DB dev, không gọi mạng thật
- [ ] Không `sleep`, không phụ thuộc thời điểm chạy
- [ ] Có ít nhất: happy path, dữ liệu sai, sai quyền
- [ ] Bug fix có test tái hiện đi kèm
- [ ] `make test` xanh và số test tăng (không giảm)
