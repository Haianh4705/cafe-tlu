"""Test CRUD products + categories (Issue #29), chạy trên MySQL test."""

import pytest

from api.core.security import create_access_token
from api.models.category import Category
from api.models.product import Product
from shared.error_codes import ErrorCode

PRODUCTS_URL = "/api/v1/products"
CATEGORIES_URL = "/api/v1/categories"


def _auth(user) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(user)}"}


def _make_category(db, name: str = "Cà phê") -> Category:
    category = Category(name=name)
    db.add(category)
    db.flush()
    return category


def _make_product(
    db,
    category: Category,
    name: str = "Cà phê sữa",
    price: int = 30000,
    unit: str = "ly",
    is_available: bool = True,
) -> Product:
    product = Product(
        name=name,
        category_id=category.id,
        price=price,
        unit=unit,
        is_available=is_available,
    )
    db.add(product)
    db.flush()
    return product


# ── Categories ──────────────────────────────────────────────────────────────


def test_list_categories_returns_envelope(client, db_session, staff_user) -> None:
    _make_category(db_session, "Trà trái cây")
    _make_category(db_session, "Cà phê")

    response = client.get(CATEGORIES_URL, headers=_auth(staff_user))
    assert response.status_code == 200

    body = response.json()
    assert "meta" in body
    assert [category["name"] for category in body["data"]] == ["Cà phê", "Trà trái cây"]


def test_create_category_admin_returns_201(client, admin_user) -> None:
    response = client.post(
        CATEGORIES_URL,
        json={"name": "Bánh ngọt", "description": "Bánh & ăn vặt"},
        headers=_auth(admin_user),
    )
    assert response.status_code == 201

    data = response.json()["data"]
    assert data["name"] == "Bánh ngọt"
    assert data["is_active"] is True
    assert data["id"] > 0


def test_create_category_duplicate_returns_409(client, db_session, admin_user) -> None:
    _make_category(db_session, "Cà phê")

    response = client.post(CATEGORIES_URL, json={"name": "Cà phê"}, headers=_auth(admin_user))
    assert response.status_code == 409
    assert response.json()["error"]["code"] == ErrorCode.CONFLICT


def test_create_category_staff_forbidden(client, staff_user) -> None:
    response = client.post(CATEGORIES_URL, json={"name": "Cà phê"}, headers=_auth(staff_user))
    assert response.status_code == 403
    assert response.json()["error"]["code"] == ErrorCode.FORBIDDEN


# ── Products: đọc ───────────────────────────────────────────────────────────


def test_list_products_returns_pagination_and_category_name(client, db_session, staff_user) -> None:
    coffee = _make_category(db_session, "Cà phê")
    _make_product(db_session, coffee, name="Cà phê sữa", price=30000)
    _make_product(db_session, coffee, name="Bạc xỉu", price=35000)
    _make_product(db_session, coffee, name="Cà phê đen", price=25000)

    response = client.get(
        PRODUCTS_URL, params={"page": 1, "page_size": 2}, headers=_auth(staff_user)
    )
    assert response.status_code == 200

    body = response.json()
    assert len(body["data"]) == 2
    assert body["meta"] == {"page": 1, "page_size": 2, "total": 3, "total_pages": 2}
    assert body["data"][0]["category"] == "Cà phê"
    assert body["data"][0]["category_id"] == coffee.id


def test_search_and_category_filter(client, db_session, staff_user) -> None:
    coffee = _make_category(db_session, "Cà phê")
    tea = _make_category(db_session, "Trà trái cây")
    _make_product(db_session, coffee, name="Cà phê sữa")
    _make_product(db_session, tea, name="Trà đào cam sả")

    search_response = client.get(PRODUCTS_URL, params={"search": "trà"}, headers=_auth(staff_user))
    assert [item["name"] for item in search_response.json()["data"]] == ["Trà đào cam sả"]

    filter_response = client.get(
        PRODUCTS_URL, params={"category_id": coffee.id}, headers=_auth(staff_user)
    )
    assert [item["name"] for item in filter_response.json()["data"]] == ["Cà phê sữa"]


def test_get_product_detail_and_not_found(client, db_session, staff_user) -> None:
    category = _make_category(db_session, "Cà phê")
    product = _make_product(db_session, category, name="Cà phê sữa")

    found = client.get(f"{PRODUCTS_URL}/{product.id}", headers=_auth(staff_user))
    assert found.status_code == 200
    assert found.json()["data"]["name"] == "Cà phê sữa"

    missing = client.get(f"{PRODUCTS_URL}/999999", headers=_auth(staff_user))
    assert missing.status_code == 404
    assert missing.json()["error"]["code"] == ErrorCode.NOT_FOUND


# ── Products: ghi (admin) ───────────────────────────────────────────────────


def test_create_product_admin_and_duplicate_name(
    client, db_session, admin_user, staff_user
) -> None:
    category = _make_category(db_session, "Cà phê")
    payload = {
        "name": "Trà đào cam sả",
        "category_id": category.id,
        "price": 35000,
        "unit": "ly",
        "is_available": True,
    }

    created = client.post(PRODUCTS_URL, json=payload, headers=_auth(admin_user))
    assert created.status_code == 201
    assert created.json()["data"]["name"] == "Trà đào cam sả"

    duplicated = client.post(PRODUCTS_URL, json=payload, headers=_auth(admin_user))
    assert duplicated.status_code == 409
    assert duplicated.json()["error"]["code"] == ErrorCode.PRODUCT_NAME_DUPLICATED

    forbidden = client.post(PRODUCTS_URL, json=payload, headers=_auth(staff_user))
    assert forbidden.status_code == 403


def test_create_product_invalid_payload_returns_422(client, db_session, admin_user) -> None:
    category = _make_category(db_session, "Cà phê")

    response = client.post(
        PRODUCTS_URL,
        json={"name": "", "category_id": category.id, "price": -1},
        headers=_auth(admin_user),
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == ErrorCode.VALIDATION_ERROR


def test_update_product_admin_and_duplicate_name(
    client, db_session, admin_user, staff_user
) -> None:
    category = _make_category(db_session, "Cà phê")
    product = _make_product(db_session, category, name="Cà phê sữa")
    other = _make_product(db_session, category, name="Bạc xỉu")

    updated = client.patch(
        f"{PRODUCTS_URL}/{product.id}",
        json={"price": 45000, "unit": "cốc"},
        headers=_auth(admin_user),
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["price"] == 45000
    assert updated.json()["data"]["unit"] == "cốc"

    duplicated = client.patch(
        f"{PRODUCTS_URL}/{product.id}",
        json={"name": other.name},
        headers=_auth(admin_user),
    )
    assert duplicated.status_code == 409
    assert duplicated.json()["error"]["code"] == ErrorCode.PRODUCT_NAME_DUPLICATED

    forbidden = client.patch(
        f"{PRODUCTS_URL}/{product.id}", json={"price": 1000}, headers=_auth(staff_user)
    )
    assert forbidden.status_code == 403


def test_delete_product_soft_deletes_and_frees_name(
    client, db_session, admin_user, staff_user
) -> None:
    category = _make_category(db_session, "Cà phê")
    product = _make_product(db_session, category, name="Trà đào")

    deleted = client.delete(f"{PRODUCTS_URL}/{product.id}", headers=_auth(admin_user))
    assert deleted.status_code == 204
    assert deleted.content == b""
    assert db_session.get(Product, product.id).deleted_at is not None

    list_response = client.get(PRODUCTS_URL, headers=_auth(staff_user))
    assert list_response.json()["data"] == []

    detail_response = client.get(f"{PRODUCTS_URL}/{product.id}", headers=_auth(staff_user))
    assert detail_response.status_code == 404

    recreated = client.post(
        PRODUCTS_URL,
        json={"name": "Trà đào", "category_id": category.id, "price": 35000},
        headers=_auth(admin_user),
    )
    assert recreated.status_code == 201


def test_delete_product_staff_forbidden(client, db_session, staff_user) -> None:
    category = _make_category(db_session, "Cà phê")
    product = _make_product(db_session, category)

    response = client.delete(f"{PRODUCTS_URL}/{product.id}", headers=_auth(staff_user))
    assert response.status_code == 403
    assert response.json()["error"]["code"] == ErrorCode.FORBIDDEN


def test_list_products_requires_authentication(client) -> None:
    response = client.get(PRODUCTS_URL)
    assert response.status_code == 401
    assert response.json()["error"]["code"] == ErrorCode.UNAUTHENTICATED


def test_patch_omitted_fields_preserves_existing_values(client, db_session, admin_user) -> None:
    category = _make_category(db_session, "Cà phê")
    product = _make_product(
        db_session,
        category,
        name="Bạc xỉu",
        price=42000,
        unit="ly",
        is_available=False,
    )
    product.image_url = "https://example.test/bac-xiu.png"
    db_session.flush()

    response = client.patch(
        f"{PRODUCTS_URL}/{product.id}",
        json={"unit": "cốc"},
        headers=_auth(admin_user),
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["name"] == "Bạc xỉu"
    assert data["category_id"] == category.id
    assert data["price"] == 42000
    assert data["unit"] == "cốc"
    assert data["image_url"] == "https://example.test/bac-xiu.png"
    assert data["is_available"] is False


@pytest.mark.parametrize("field", ["name", "category_id", "price", "unit", "is_available"])
def test_patch_null_non_nullable_field_returns_422_without_mutation(
    client, db_session, admin_user, field: str
) -> None:
    category = _make_category(db_session, "Cà phê")
    product = _make_product(db_session, category, name="Bạc xỉu", price=42000)

    response = client.patch(
        f"{PRODUCTS_URL}/{product.id}",
        json={field: None},
        headers=_auth(admin_user),
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == ErrorCode.VALIDATION_ERROR
    db_session.refresh(product)
    assert product.name == "Bạc xỉu"
    assert product.category_id == category.id
    assert product.price == 42000
    assert product.unit == "ly"
    assert product.is_available is True


def test_patch_image_url_null_removes_existing_image(client, db_session, admin_user) -> None:
    category = _make_category(db_session, "Cà phê")
    product = _make_product(db_session, category, name="Bạc xỉu")
    product.image_url = "https://example.test/bac-xiu.png"
    db_session.flush()

    response = client.patch(
        f"{PRODUCTS_URL}/{product.id}", json={"image_url": None}, headers=_auth(admin_user)
    )

    assert response.status_code == 200
    assert response.json()["data"]["image_url"] is None
    db_session.refresh(product)
    assert product.image_url is None


def test_product_price_above_decimal_limit_returns_422_for_create_and_patch(
    client, db_session, admin_user
) -> None:
    category = _make_category(db_session, "Cà phê")
    product = _make_product(db_session, category, name="Bạc xỉu", price=42000)
    over_limit = 1_000_000_000_000

    created = client.post(
        PRODUCTS_URL,
        json={"name": "Món giá quá lớn", "category_id": category.id, "price": over_limit},
        headers=_auth(admin_user),
    )
    updated = client.patch(
        f"{PRODUCTS_URL}/{product.id}",
        json={"price": over_limit},
        headers=_auth(admin_user),
    )

    assert created.status_code == 422
    assert created.json()["error"]["code"] == ErrorCode.VALIDATION_ERROR
    assert updated.status_code == 422
    assert updated.json()["error"]["code"] == ErrorCode.VALIDATION_ERROR
    db_session.refresh(product)
    assert product.price == 42000
    assert db_session.query(Product).filter_by(name="Món giá quá lớn").first() is None


def test_duplicate_product_name_returns_409_without_mutation(
    client, db_session, admin_user
) -> None:
    category = _make_category(db_session, "Cà phê")
    product = _make_product(db_session, category, name="Bạc xỉu", price=42000)
    other = _make_product(db_session, category, name="Cà phê sữa", price=30000)

    response = client.patch(
        f"{PRODUCTS_URL}/{product.id}",
        json={"name": other.name},
        headers=_auth(admin_user),
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == ErrorCode.PRODUCT_NAME_DUPLICATED
    db_session.refresh(product)
    assert product.name == "Bạc xỉu"
