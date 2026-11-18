"""Test API public Kiosk (#112): GET /public/menu và POST /public/orders trên MySQL test."""

import re
from datetime import datetime

from sqlalchemy import select

from api.models.audit_log import AuditLog
from api.models.category import Category
from api.models.order import Order
from api.models.product import Product
from api.models.table import CafeTable
from shared.error_codes import ErrorCode

PUBLIC_MENU_URL = "/api/v1/public/menu"
PUBLIC_ORDERS_URL = "/api/v1/public/orders"


def _seed_kiosk_catalog(db) -> tuple[Category, Category, CafeTable, CafeTable, list[Product]]:
    cat_active = Category(name="Cà phê Kiosk", is_active=True)
    cat_inactive = Category(name="Danh mục ẩn Kiosk", is_active=False)
    db.add_all([cat_active, cat_inactive])
    db.flush()

    tbl_free = CafeTable(
        table_number="Bàn K01",
        area="Sảnh Kiosk",
        seating_capacity=4,
        status="available",
        is_active=True,
    )
    tbl_hidden = CafeTable(
        table_number="Bàn K99",
        area="Kho",
        seating_capacity=2,
        status="available",
        is_active=False,
    )
    db.add_all([tbl_free, tbl_hidden])
    db.flush()

    p_coffee = Product(
        name="Bạc xỉu Kiosk",
        category_id=cat_active.id,
        price=30000,
        unit="ly",
        is_available=True,
    )
    p_cake = Product(
        name="Croissant Kiosk",
        category_id=cat_active.id,
        price=45000,
        unit="cái",
        is_available=True,
    )
    p_soldout = Product(
        name="Matcha Tạm Hết",
        category_id=cat_active.id,
        price=40000,
        unit="ly",
        is_available=False,
    )
    p_deleted = Product(
        name="Món Đã Xoá",
        category_id=cat_active.id,
        price=25000,
        unit="ly",
        is_available=True,
        deleted_at=datetime.now(),
    )
    p_hidden_cat = Product(
        name="Món Danh Mục Ẩn",
        category_id=cat_inactive.id,
        price=35000,
        unit="ly",
        is_available=True,
    )
    products = [p_coffee, p_cake, p_soldout, p_deleted, p_hidden_cat]
    db.add_all(products)
    db.flush()
    return cat_active, cat_inactive, tbl_free, tbl_hidden, products


def test_get_public_menu_no_auth_filters_deleted_and_inactive(client, db_session) -> None:
    """GET /public/menu không cần token, lọc category/bàn inactive & món deleted, giữ món tạm hết."""
    _seed_kiosk_catalog(db_session)

    response = client.get(PUBLIC_MENU_URL)
    assert response.status_code == 200

    body = response.json()
    assert "meta" in body
    data = body["data"]

    cat_names = [c["name"] for c in data["categories"]]
    assert "Cà phê Kiosk" in cat_names
    assert "Danh mục ẩn Kiosk" not in cat_names

    table_numbers = [t["table_number"] for t in data["tables"]]
    assert "Bàn K01" in table_numbers
    assert "Bàn K99" not in table_numbers

    prod_by_name = {p["name"]: p for p in data["products"]}
    assert "Bạc xỉu Kiosk" in prod_by_name
    assert prod_by_name["Matcha Tạm Hết"]["is_available"] is False
    assert "Món Đã Xoá" not in prod_by_name
    assert "Món Danh Mục Ẩn" not in prod_by_name


def test_create_public_order_201_server_side_total_and_audit_log(
    client, db_session, staff_user
) -> None:
    """POST /public/orders tự tính tiền ở server, đổi bàn sang occupied và ghi AuditLog."""
    _ = staff_user
    _, _, tbl_free, _, products = _seed_kiosk_catalog(db_session)
    p_coffee, p_cake = products[0], products[1]

    response = client.post(
        PUBLIC_ORDERS_URL,
        json={
            "table_id": tbl_free.id,
            "notes": "Mang ra nhanh giúp mình",
            "items": [
                {"product_id": p_coffee.id, "quantity": 2, "notes": "50% đường", "price": 1},
                {"product_id": p_cake.id, "quantity": 1},
            ],
        },
    )
    assert response.status_code == 201

    data = response.json()["data"]
    today = datetime.now().strftime("%Y%m%d")
    assert re.fullmatch(rf"ORD-{today}-\d{{3}}", data["order_code"])
    assert data["table_id"] == tbl_free.id
    assert data["table_number"] == "Bàn K01"
    assert data["status"] == "pending"
    assert data["total_amount"] == 105000
    assert data["qr_payload"] == f"CAFETLU|VIETQR|{data['order_code']}|105000"
    assert len(data["items"]) == 2

    db_session.expire_all()
    table_db = db_session.get(CafeTable, tbl_free.id)
    assert table_db is not None
    assert table_db.status == "occupied"

    order_db = db_session.get(Order, data["id"])
    assert order_db is not None
    assert int(order_db.total_amount) == 105000

    audit = db_session.scalar(
        select(AuditLog).where(
            AuditLog.action == "CREATE_PUBLIC_ORDER",
            AuditLog.entity_id == data["id"],
        )
    )
    assert audit is not None
    assert audit.entity_type == "orders"
    assert audit.details is not None
    assert audit.details["order_code"] == data["order_code"]


def test_create_public_order_rejects_occupied_table_409(client, db_session, staff_user) -> None:
    """Bàn đã occupied phải trả 409 CONFLICT để tránh đặt trùng bàn."""
    _ = staff_user
    _, _, tbl_free, _, products = _seed_kiosk_catalog(db_session)
    p_coffee = products[0]

    first = client.post(
        PUBLIC_ORDERS_URL,
        json={"table_id": tbl_free.id, "items": [{"product_id": p_coffee.id, "quantity": 1}]},
    )
    assert first.status_code == 201

    second = client.post(
        PUBLIC_ORDERS_URL,
        json={"table_id": tbl_free.id, "items": [{"product_id": p_coffee.id, "quantity": 1}]},
    )
    assert second.status_code == 409
    assert second.json()["error"]["code"] == ErrorCode.CONFLICT


def test_create_public_order_rejects_unavailable_product_409(
    client, db_session, staff_user
) -> None:
    """Món đang tạm hết (is_available=False) phải trả 409 INSUFFICIENT_STOCK."""
    _ = staff_user
    _, _, tbl_free, _, products = _seed_kiosk_catalog(db_session)
    p_soldout = products[2]

    response = client.post(
        PUBLIC_ORDERS_URL,
        json={"table_id": tbl_free.id, "items": [{"product_id": p_soldout.id, "quantity": 1}]},
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == ErrorCode.INSUFFICIENT_STOCK


def test_create_public_order_validation_422(client, db_session) -> None:
    """Danh sách món rỗng hoặc quantity = 0 phải trả 422 VALIDATION_ERROR."""
    _, _, tbl_free, _, products = _seed_kiosk_catalog(db_session)

    empty_resp = client.post(
        PUBLIC_ORDERS_URL,
        json={"table_id": tbl_free.id, "items": []},
    )
    assert empty_resp.status_code == 422
    assert empty_resp.json()["error"]["code"] == ErrorCode.VALIDATION_ERROR

    zero_qty_resp = client.post(
        PUBLIC_ORDERS_URL,
        json={"table_id": tbl_free.id, "items": [{"product_id": products[0].id, "quantity": 0}]},
    )
    assert zero_qty_resp.status_code == 422
    assert zero_qty_resp.json()["error"]["code"] == ErrorCode.VALIDATION_ERROR
