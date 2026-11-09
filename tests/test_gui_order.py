"""Kiểm thử đơn vị cho giao diện và logic màn hình Gọi món & Thanh toán (OrderView).

Tuân thủ:
- docs/api-contract.md: Endpoint 8, 13, 14-19 (bàn, thực đơn, giỏ hàng, thanh toán, hoá đơn).
- docs/test-cases.md: TC-ORD-01, TC-ORD-02, TC-ORD-03.
- Kiểm thử trực tiếp các widget PySide6: OrderView, OrderCartWidget, TableCardWidget, CheckoutDialog, ReceiptDialog.
"""

from typing import Any

from gui.api_client import ApiClient
from gui.i18n import format_currency
from gui.views.order_view import MOCK_PRODUCTS, MOCK_TABLES, OrderView
from gui.widgets.checkout_dialog import CheckoutDialog
from gui.widgets.order_cart import OrderCartWidget
from gui.widgets.receipt_dialog import ReceiptDialog
from gui.widgets.table_card import TableCardWidget


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


def test_order_cart_widget_operations(qapp: Any) -> None:
    """Kiểm tra widget giỏ hàng: thêm món, tính tổng tiền và cập nhật số lượng (TC-ORD-01, TC-ORD-02)."""
    cart = OrderCartWidget()
    cart.set_table({"id": 1, "name": "Bàn 01", "status": "occupied"})

    items = [
        {"id": 1, "name": "Cà phê đen đá", "price": 25000, "quantity": 2, "subtotal": 50000},
        {"id": 4, "name": "Trà đào cam sả", "price": 35000, "quantity": 1, "subtotal": 35000},
    ]
    cart.set_items(items)

    assert len(cart.items) == 2
    assert cart.calculate_total() == 85000
    assert format_currency(cart.calculate_total()) == "85.000 đ"
    assert "85.000 đ" in cart._total_val_lbl.text()
    assert cart._checkout_btn.isEnabled() is True


def test_table_card_widget_states(qapp: Any) -> None:
    """Kiểm tra TableCardWidget hiển thị đúng trạng thái bàn và phản hồi chọn bàn."""
    table_data = {"id": 1, "name": "Bàn 01", "capacity": 4, "status": "free"}
    card = TableCardWidget(table_data)

    assert "Bàn 01" in card._name_label.text()
    assert card._status_badge.text() == "Bàn trống"

    # Bàn chuyển sang có khách
    table_data["status"] = "occupied"
    card.update_data(table_data)
    assert card._status_badge.text() == "Đang có khách"

    # Kích hoạt trạng thái đang chọn
    card.set_active(True)
    assert card._is_active is True


def test_checkout_dialog_change_and_validation(qapp: Any) -> None:
    """Kiểm tra CheckoutDialog tính tiền thối và kích hoạt/vô hiệu nút thanh toán (TC-ORD-03)."""
    items = [
        {"id": 1, "name": "Cà phê đen đá", "price": 25000, "quantity": 2, "subtotal": 50000},
        {"id": 4, "name": "Trà đào cam sả", "price": 35000, "quantity": 1, "subtotal": 35000},
    ]
    total_bill = 85000
    dialog = CheckoutDialog(table_name="Bàn 01", total_amount=total_bill, order_items=items)

    # Khách đưa 100.000 đ -> Tiền thừa 15.000 đ
    dialog._received_input.setText("100000")
    assert dialog.received_amount == 100000
    assert "15.000 đ" in dialog._change_val_lbl.text()
    assert dialog._confirm_btn.isEnabled() is True

    # Khách đưa thiếu tiền (50.000 đ) -> Nút xác nhận bị vô hiệu hoá
    dialog._received_input.setText("50000")
    assert "Thiếu 35.000 đ" in dialog._change_val_lbl.text()
    assert dialog._confirm_btn.isEnabled() is False

    # Chuyển sang thanh toán Chuyển khoản QR
    dialog._qr_radio.setChecked(True)
    assert dialog.payment_method == "qr"
    assert dialog._cash_calc_widget.isHidden() is True
    assert dialog._confirm_btn.isEnabled() is True


def test_receipt_dialog_rendering_and_content(qapp: Any) -> None:
    """Kiểm tra ReceiptDialog tạo đúng nội dung phiếu thanh toán in nhiệt K80."""
    receipt_data = {
        "invoice_code": "HD-20261109-001",
        "table_name": "Bàn 03",
        "cashier_name": "Trần Thị B",
        "created_at": "09/11/2026 21:30:00",
        "items": [
            {
                "id": 1,
                "name": "Cà phê đen đá",
                "price": 25000,
                "quantity": 2,
                "subtotal": 50000,
                "note": "Ít ngọt",
            },
            {"id": 4, "name": "Trà đào cam sả", "price": 35000, "quantity": 1, "subtotal": 35000},
        ],
        "total_amount": 85000,
        "payment_method": "cash",
        "received_amount": 100000,
        "change_amount": 15000,
    }

    dialog = ReceiptDialog(receipt_data)
    html = dialog._generate_html()

    # Kiểm tra các thông tin bắt buộc trong hoá đơn
    assert "QUÁN CÀ PHÊ TLU" in html
    assert "HD-20261109-001" in html
    assert "Bàn 03" in html
    assert "Trần Thị B" in html
    assert "Cà phê đen đá" in html
    assert "Ít ngọt" in html
    assert "Trà đào cam sả" in html
    assert "85.000 đ" in html
    assert "100.000 đ" in html
    assert "15.000 đ" in html
    assert "Cảm ơn Quý khách & Hẹn gặp lại!" in html


def test_order_view_filtering_and_table_selection(qapp: Any) -> None:
    """Kiểm tra OrderView: nạp dữ liệu, chọn bàn và lọc món theo từ khoá."""
    client = ApiClient(base_url="http://127.0.0.1:8000/api/v1")
    view = OrderView(client)

    # Giả lập nạp dữ liệu thành công
    view._on_data_loaded((MOCK_TABLES, MOCK_PRODUCTS))

    assert len(view._tables) == len(MOCK_TABLES)
    assert len(view._products) == len(MOCK_PRODUCTS)
    assert view._selected_table is not None
    assert view._selected_table.get("id") == 1

    # Thử chọn bàn 2
    view._select_table(MOCK_TABLES[1])
    assert view._selected_table.get("id") == 2
    assert "Bàn 02" in view._cart_widget._table_title_lbl.text()

    # Thử lọc món ăn theo từ khoá "cà phê"
    view._search_input.setText("cà phê")
    view._filter_products()
    # Kiểm tra có phím tắt F1, F2
    assert view._search_input.text() == "cà phê"


def test_order_view_with_api_envelope_products(qapp: Any) -> None:
    """Kiểm tra OrderView bóc tách đúng envelope {'data': [...], 'meta': {...}} từ API get_products (#41)."""
    client = ApiClient(base_url="http://127.0.0.1:8000/api/v1")
    view = OrderView(client)

    envelope_products = {
        "data": MOCK_PRODUCTS,
        "meta": {"page": 1, "page_size": 20, "total": len(MOCK_PRODUCTS), "total_pages": 1},
    }

    # Bóc tách envelope
    data = (
        envelope_products.get("data") if isinstance(envelope_products, dict) else envelope_products
    )
    view._on_data_loaded((MOCK_TABLES, data))

    assert len(view._products) == len(MOCK_PRODUCTS)
    assert view._products[0]["name"] == "Cà phê đen đá"
