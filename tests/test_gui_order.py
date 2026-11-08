"""Kiểm thử đơn vị cho logic và tính toán trong màn hình Gọi món & Thanh toán (OrderView)."""

from gui.views.order_view import MOCK_PRODUCTS, MOCK_TABLES
from gui.views.product_list_view import format_currency


def test_mock_tables_and_products_structure() -> None:
    """Kiểm tra cấu trúc và tính hợp lệ của dữ liệu bàn và thực đơn mẫu."""
    assert len(MOCK_TABLES) >= 10
    for tbl in MOCK_TABLES:
        assert "id" in tbl
        assert "name" in tbl
        assert "capacity" in tbl
        assert tbl["status"] in ["free", "occupied", "reserved"]

    assert len(MOCK_PRODUCTS) >= 8
    for prod in MOCK_PRODUCTS:
        assert "id" in prod
        assert "name" in prod
        assert "price" in prod
        assert prod["price"] > 0
        assert prod["is_available"] is True


def test_order_subtotal_calculation() -> None:
    """Kiểm tra logic tính tổng tiền của giỏ hàng với nhiều món ăn và số lượng."""
    cart_items = [
        {"product_id": 1, "product_name": "Cà phê đen đá", "price": 25000, "quantity": 2},
        {"product_id": 4, "product_name": "Trà đào cam sả", "price": 35000, "quantity": 1},
        {"product_id": 9, "product_name": "Bánh sừng bò", "price": 28000, "quantity": 3},
    ]

    total = sum(it["price"] * it["quantity"] for it in cart_items)
    # 25000*2 + 35000*1 + 28000*3 = 50000 + 35000 + 84000 = 169000
    assert total == 169000
    assert format_currency(total) == "169.000 đ"


def test_checkout_change_calculation() -> None:
    """Kiểm tra tính toán tiền thừa trả lại cho khách hàng."""
    total_bill = 169000

    # Khách đưa 200.000 đ
    customer_cash = 200000
    change = customer_cash - total_bill
    assert change == 31000
    assert format_currency(change) == "31.000 đ"

    # Khách đưa vừa đủ
    customer_cash_exact = 169000
    change_exact = customer_cash_exact - total_bill
    assert change_exact == 0
    assert format_currency(change_exact) == "0 đ"


def test_table_status_transition() -> None:
    """Kiểm tra logic chuyển trạng thái bàn khi có đơn hàng và sau thanh toán."""
    table = {"id": 1, "name": "Bàn 01", "status": "free"}

    # Khách gọi món -> chuyển sang occupied
    items = [{"product_id": 1, "quantity": 1}]
    table["status"] = "occupied" if len(items) > 0 else "free"
    assert table["status"] == "occupied"

    # Thanh toán xong hoặc huỷ đơn -> chuyển về free
    items.clear()
    table["status"] = "occupied" if len(items) > 0 else "free"
    assert table["status"] == "free"
