"""Test API bàn và đơn gọi món tại bàn (Issue #93) trên MySQL test."""

import re
from datetime import datetime

from api.core.security import create_access_token
from api.models.category import Category
from api.models.order import Order
from api.models.product import Product
from api.models.table import CafeTable
from shared.error_codes import ErrorCode

TABLES_URL = "/api/v1/tables"
ORDERS_URL = "/api/v1/orders"


def _auth(user) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(user)}"}


def _seed(db) -> tuple[CafeTable, Product, Product]:
    category = Category(name="Đồ uống Order")
    db.add(category)
    db.flush()

    table = CafeTable(
        table_number="Bàn O01",
        area="Tầng 1",
        seating_capacity=4,
        status="available",
        is_active=True,
    )
    db.add(table)
    db.flush()

    coffee = Product(
        name="Cà phê Order",
        category_id=category.id,
        price=25000,
        unit="ly",
        is_available=True,
    )
    cake = Product(
        name="Bánh Order",
        category_id=category.id,
        price=45000,
        unit="cái",
        is_available=True,
    )
    db.add_all([coffee, cake])
    db.flush()
    return table, coffee, cake


def _create_order(client, headers, table_id: int) -> dict:
    response = client.post(ORDERS_URL, json={"table_id": table_id}, headers=headers)
    assert response.status_code == 201
    return response.json()["data"]


def test_tables_requires_auth_and_exposes_open_order(client, db_session, staff_user) -> None:
    """GET /tables cần đăng nhập và trả open_order_id để GUI khôi phục đơn đang mở."""
    assert client.get(TABLES_URL).status_code == 401

    table, _, _ = _seed(db_session)
    headers = _auth(staff_user)

    data = client.get(TABLES_URL, headers=headers).json()["data"]
    assert data[0]["id"] == table.id
    assert data[0]["status"] == "available"
    assert data[0]["open_order_id"] is None

    order = _create_order(client, headers, table.id)
    data = client.get(TABLES_URL, headers=headers).json()["data"]
    assert data[0]["open_order_id"] == order["id"]
    assert data[0]["status"] == "occupied"


def test_create_and_get_order_404_409(client, db_session, staff_user) -> None:
    """POST /orders 201 cho bàn trống; mở trùng bàn 409; id không tồn tại 404."""
    table, _, _ = _seed(db_session)
    headers = _auth(staff_user)

    order = _create_order(client, headers, table.id)
    today = datetime.now().strftime("%Y%m%d")
    assert re.fullmatch(rf"ORD-{today}-\d{{3}}", order["order_code"])
    assert order["status"] == "pending"
    assert order["total_amount"] == 0

    duplicate = client.post(ORDERS_URL, json={"table_id": table.id}, headers=headers)
    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == ErrorCode.CONFLICT

    missing_table = client.post(ORDERS_URL, json={"table_id": 999999}, headers=headers)
    assert missing_table.status_code == 404
    assert missing_table.json()["error"]["code"] == ErrorCode.NOT_FOUND

    assert client.get(f"{ORDERS_URL}/{order['id']}", headers=headers).status_code == 200
    missing_order = client.get(f"{ORDERS_URL}/999999", headers=headers)
    assert missing_order.status_code == 404
    assert missing_order.json()["error"]["code"] == ErrorCode.NOT_FOUND


def test_items_add_update_remove_recalculate_total(client, db_session, staff_user) -> None:
    """Thêm/gộp món, sửa số lượng/ghi chú, xoá món đều tính lại total_amount ở server."""
    table, coffee, cake = _seed(db_session)
    headers = _auth(staff_user)
    order = _create_order(client, headers, table.id)
    order_url = f"{ORDERS_URL}/{order['id']}"

    first = client.post(
        f"{order_url}/items",
        json={"product_id": coffee.id, "quantity": 2},
        headers=headers,
    )
    assert first.status_code == 201
    data = first.json()["data"]
    assert data["total_amount"] == 50000
    assert data["items"][0]["unit_price"] == 25000
    assert data["items"][0]["subtotal"] == 50000

    merged = client.post(
        f"{order_url}/items",
        json={"product_id": coffee.id, "quantity": 1},
        headers=headers,
    ).json()["data"]
    assert merged["total_amount"] == 75000
    assert merged["items"][0]["quantity"] == 3

    with_cake = client.post(
        f"{order_url}/items",
        json={"product_id": cake.id, "quantity": 1},
        headers=headers,
    ).json()["data"]
    assert with_cake["total_amount"] == 120000
    coffee_item = next(item for item in with_cake["items"] if item["product_id"] == coffee.id)

    updated = client.patch(
        f"{order_url}/items/{coffee_item['id']}",
        json={"quantity": 5, "notes": "Ít đá"},
        headers=headers,
    )
    assert updated.status_code == 200
    data = updated.json()["data"]
    assert data["total_amount"] == 170000
    coffee_item = next(item for item in data["items"] if item["product_id"] == coffee.id)
    assert coffee_item["quantity"] == 5
    assert coffee_item["notes"] == "Ít đá"

    removed = client.delete(f"{order_url}/items/{coffee_item['id']}", headers=headers)
    assert removed.status_code == 204

    data = client.get(order_url, headers=headers).json()["data"]
    assert len(data["items"]) == 1
    assert data["items"][0]["product_id"] == cake.id
    assert data["total_amount"] == 45000


def test_patch_item_empty_payload_returns_400(client, db_session, staff_user) -> None:
    """PATCH không có trường nào trả 400 VALIDATION_ERROR thay vì 422 khó hiểu."""
    table, coffee, _ = _seed(db_session)
    headers = _auth(staff_user)
    order = _create_order(client, headers, table.id)
    item = client.post(
        f"{ORDERS_URL}/{order['id']}/items",
        json={"product_id": coffee.id, "quantity": 1},
        headers=headers,
    ).json()["data"]["items"][0]

    response = client.patch(
        f"{ORDERS_URL}/{order['id']}/items/{item['id']}",
        json={},
        headers=headers,
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == ErrorCode.VALIDATION_ERROR

    null_quantity = client.patch(
        f"{ORDERS_URL}/{order['id']}/items/{item['id']}",
        json={"quantity": None},
        headers=headers,
    )
    assert null_quantity.status_code == 400
    assert null_quantity.json()["error"]["code"] == ErrorCode.VALIDATION_ERROR


def test_paid_order_cannot_be_modified(client, db_session, staff_user) -> None:
    """Đơn đã thanh toán/đóng trả 409 ORDER_ALREADY_PAID khi thêm hoặc sửa món."""
    table, coffee, _ = _seed(db_session)
    headers = _auth(staff_user)
    order_data = _create_order(client, headers, table.id)
    add = client.post(
        f"{ORDERS_URL}/{order_data['id']}/items",
        json={"product_id": coffee.id, "quantity": 1},
        headers=headers,
    )
    item = add.json()["data"]["items"][0]

    order = db_session.get(Order, order_data["id"])
    assert order is not None
    order.status = "completed"
    db_session.commit()

    added = client.post(
        f"{ORDERS_URL}/{order_data['id']}/items",
        json={"product_id": coffee.id, "quantity": 1},
        headers=headers,
    )
    assert added.status_code == 409
    assert added.json()["error"]["code"] == ErrorCode.ORDER_ALREADY_PAID

    patched = client.patch(
        f"{ORDERS_URL}/{order_data['id']}/items/{item['id']}",
        json={"quantity": 2},
        headers=headers,
    )
    assert patched.status_code == 409


def test_add_item_validates_product_state(client, db_session, staff_user) -> None:
    """Món không tồn tại 404; món tạm hết 409; lỗi không làm thay đổi tổng tiền."""
    table, coffee, _ = _seed(db_session)
    unavailable = Product(
        name="Món Tạm Hết Order",
        category_id=coffee.category_id,
        price=30000,
        unit="ly",
        is_available=False,
    )
    db_session.add(unavailable)
    db_session.flush()

    headers = _auth(staff_user)
    order = _create_order(client, headers, table.id)
    order_url = f"{ORDERS_URL}/{order['id']}"

    missing = client.post(
        f"{order_url}/items",
        json={"product_id": 999999, "quantity": 1},
        headers=headers,
    )
    assert missing.status_code == 404
    assert missing.json()["error"]["code"] == ErrorCode.NOT_FOUND

    sold_out = client.post(
        f"{order_url}/items",
        json={"product_id": unavailable.id, "quantity": 1},
        headers=headers,
    )
    assert sold_out.status_code == 409
    assert sold_out.json()["error"]["code"] == ErrorCode.INSUFFICIENT_STOCK

    data = client.get(order_url, headers=headers).json()["data"]
    assert data["items"] == []
    assert data["total_amount"] == 0


def test_item_must_belong_to_order(client, db_session, staff_user) -> None:
    """Không cho sửa/xoá dòng món của đơn khác."""
    table, coffee, _ = _seed(db_session)
    second_table = CafeTable(
        table_number="Bàn O02",
        area="Tầng 1",
        seating_capacity=2,
        status="available",
        is_active=True,
    )
    db_session.add(second_table)
    db_session.flush()

    headers = _auth(staff_user)
    first_order = _create_order(client, headers, table.id)
    second_order = _create_order(client, headers, second_table.id)
    item = client.post(
        f"{ORDERS_URL}/{first_order['id']}/items",
        json={"product_id": coffee.id, "quantity": 1},
        headers=headers,
    ).json()["data"]["items"][0]

    response = client.patch(
        f"{ORDERS_URL}/{second_order['id']}/items/{item['id']}",
        json={"quantity": 2},
        headers=headers,
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == ErrorCode.NOT_FOUND
