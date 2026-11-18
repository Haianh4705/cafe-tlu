"""Kiểm thử giao diện Kiosk khách hàng, widget QR VietQR và regression GUI (#112)."""

from typing import Any

import pytest
from PySide6.QtWidgets import QDialog, QPushButton, QTextBrowser

from gui.api_client import ApiClient, ApiClientError
from gui.i18n import t
from gui.main import MainWindow
from gui.views.customer_kiosk_view import CustomerKioskView
from gui.views.login_view import LoginView
from gui.views.order_view import OrderView
from gui.widgets.checkout_dialog import CheckoutDialog
from gui.widgets.kiosk_dialogs import (
    CustomerItemOptionDialog,
    OrderSubmittedDialog,
    build_kiosk_mock_menu,
)
from gui.widgets.product_dialog import ProductFormDialog
from gui.widgets.qr_widget import QrPaymentWidget, render_qr_pixmap
from gui.widgets.receipt_dialog import ReceiptDialog


def _sample_menu_payload() -> dict[str, Any]:
    return {
        "categories": [
            {"id": 1, "name": "Cà phê", "is_active": True},
            {"id": 2, "name": "Bánh ngọt", "is_active": True},
        ],
        "tables": [
            {
                "id": 10,
                "table_number": "Bàn 01",
                "area": "Tầng 1",
                "seating_capacity": 4,
                "status": "available",
            },
            {
                "id": 11,
                "table_number": "Bàn 02",
                "area": "Tầng 1",
                "seating_capacity": 4,
                "status": "occupied",
            },
        ],
        "products": [
            {
                "id": 101,
                "name": "Cà phê sữa đá",
                "category_id": 1,
                "category": "Cà phê",
                "price": 30000,
                "unit": "ly",
                "is_available": True,
            },
            {
                "id": 102,
                "name": "Trà sen vàng",
                "category_id": 1,
                "category": "Cà phê",
                "price": 45000,
                "unit": "ly",
                "is_available": False,
            },
            {
                "id": 103,
                "name": "Bánh Croissant",
                "category_id": 2,
                "category": "Bánh ngọt",
                "price": 35000,
                "unit": "cái",
                "is_available": True,
            },
        ],
    }


def test_qr_widget_and_checkout_dialog_toggle(qapp: Any) -> None:
    """render_qr_pixmap tạo QPixmap thật và CheckoutDialog bật/tắt QR đúng theo radio."""
    _ = qapp
    pixmap = render_qr_pixmap("CAFETLU|VIETQR|ORD-001|55000", size=160)
    assert not pixmap.isNull()
    assert pixmap.width() == 160
    assert pixmap.height() == 160

    qr_box = QrPaymentWidget("CAFETLU|VIETQR|ORD-001|55000", 55000, "ORD-001")
    assert not qr_box._qr_label.pixmap().isNull()

    dialog = CheckoutDialog(
        "Bàn 01",
        55000,
        [{"name": "Cà phê sữa đá", "quantity": 1, "price": 55000}],
    )
    assert dialog._cash_radio.isChecked()
    assert dialog._qr_widget.isHidden()

    dialog._qr_radio.setChecked(True)
    assert not dialog._qr_widget.isHidden()
    assert dialog._confirm_btn.isEnabled()


def test_customer_item_option_dialog_drink_and_pastry(qapp: Any) -> None:
    """Món nước giữ đường/đá, món bánh ẩn đường/đá; ghép ghi chú và số lượng."""
    _ = qapp
    coffee_dlg = CustomerItemOptionDialog(
        {"id": 1, "name": "Bạc xỉu", "category": "Cà phê", "price": 35000}
    )
    assert coffee_dlg._has_drink_options is True
    assert coffee_dlg._sugar_group is not None
    assert coffee_dlg._ice_group is not None
    coffee_dlg._sugar_group.buttons()[2].setChecked(True)
    coffee_dlg._ice_group.buttons()[1].setChecked(True)
    coffee_dlg._change_qty(2)
    coffee_dlg._note_input.setText("Ít bọt")
    assert coffee_dlg.get_selection() == {
        "quantity": 3,
        "notes": "50% đường, Ít đá, Ít bọt",
    }

    pastry_dlg = CustomerItemOptionDialog(
        {"id": 2, "name": "Bánh su kem", "category": "Bánh ngọt", "price": 25000}
    )
    assert pastry_dlg._has_drink_options is False
    assert pastry_dlg._sugar_group is None
    pastry_dlg._note_input.setText("Làm nóng nhẹ")
    assert pastry_dlg.get_selection() == {"quantity": 1, "notes": "Làm nóng nhẹ"}


def test_kiosk_menu_soldout_lock_and_filter_recovery(qapp: Any) -> None:
    """Món tạm hết bị khoá; tìm kiếm không khớp vẫn giữ thanh tìm kiếm để xoá bộ lọc."""
    _ = qapp
    view = CustomerKioskView(ApiClient(), use_mock=False)
    view.resize(1280, 720)
    view._on_menu_loaded(_sample_menu_payload())

    assert view._menu_scroll.horizontalScrollBar().maximum() == 0
    assert view._table_combo.count() == 1
    assert view._table_combo.currentData() == 10

    buttons = view._menu_container.findChildren(QPushButton)
    soldout_btns = [b for b in buttons if b.text() == t("product_out_of_stock")]
    choose_btns = [b for b in buttons if b.text() == t("kiosk_choose_btn")]
    assert len(soldout_btns) == 1
    assert soldout_btns[0].isEnabled() is False
    assert len(choose_btns) == 2
    assert all(b.isEnabled() for b in choose_btns)

    view._search_input.setText("không-tồn-tại-xyz")
    assert not view._search_input.isHidden()
    assert not view._menu_empty_label.isHidden()

    view._clear_filter_btn.click()
    assert view._search_input.text() == ""
    assert view._menu_empty_label.isHidden()
    assert not view._menu_scroll.isHidden()


def test_kiosk_cart_preserves_on_error_and_clears_on_success(
    qapp: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Lỗi POST giữ nguyên giỏ và hiện banner; gửi thành công mở QR dialog rồi xoá giỏ."""
    _ = qapp
    view = CustomerKioskView(ApiClient(), use_mock=False)
    view._on_menu_loaded(_sample_menu_payload())

    prod = _sample_menu_payload()["products"][0]
    view.add_to_cart(prod, quantity=2, notes="Ít đá")
    assert view._cart_panel.total_val_lbl.text() == "60.000 đ"
    assert view._cart_panel.submit_btn.isEnabled()

    view._on_submit_error(ApiClientError("CONFLICT", "Bàn vừa có khách", 409))
    assert len(view._cart_items) == 1
    assert not view._cart_panel.submit_error_banner.isHidden()
    assert "Bàn vừa có khách" in view._cart_panel.submit_error_banner.text()

    shown_orders: list[dict[str, Any]] = []

    def _fake_exec(dlg: OrderSubmittedDialog) -> int:
        shown_orders.append(dlg._order_data)
        assert not dlg.qr_widget._qr_label.pixmap().isNull()
        return int(QDialog.DialogCode.Accepted)

    monkeypatch.setattr(OrderSubmittedDialog, "exec", _fake_exec)
    monkeypatch.setattr(view, "load", lambda: None)

    view._on_submit_success(
        {
            "order_code": "ORD-20261118-001",
            "table_number": "Bàn 01",
            "total_amount": 60000,
            "qr_payload": "CAFETLU|VIETQR|ORD-20261118-001|60000",
            "items": [{"product_name": "Cà phê sữa đá", "quantity": 2}],
        }
    )
    assert len(shown_orders) == 1
    assert view._cart_items == []
    assert view._cart_panel.submit_error_banner.isHidden()
    assert not view._cart_panel.submit_btn.isEnabled()


def test_kiosk_mock_menu_structure() -> None:
    """Dữ liệu mock Kiosk chuẩn hoá bàn available và danh mục khớp API."""
    mock = build_kiosk_mock_menu()
    assert mock["categories"]
    assert mock["tables"]
    assert mock["products"]
    assert all(tbl["status"] in ("available", "occupied", "reserved") for tbl in mock["tables"])


def test_polished_gui_regressions(qapp: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    """Regression: Receipt product_name, ProductDialog giữ form khi lỗi, Order 1280x720, MainWindow."""
    receipt = ReceiptDialog(
        {
            "invoice_code": "HD-20261118-001",
            "table_name": "Bàn 01",
            "items": [{"product_name": "Bạc xỉu Kiosk", "quantity": 2, "price": 30000}],
            "total_amount": 60000,
        }
    )
    browser = receipt.findChild(QTextBrowser)
    assert browser is not None
    assert "Bạc xỉu Kiosk" in receipt._generate_html()
    assert "Bạc xỉu Kiosk" in browser.toPlainText()

    submitted_payloads: list[dict[str, Any]] = []
    form = ProductFormDialog(
        categories=[{"id": 1, "name": "Cà phê"}],
        on_submit=lambda data: (submitted_payloads.append(data), form.show_error("Trùng tên món")),
    )
    form._name_input.setText("Cà phê test")
    form._unit_input.setText("ly")
    form._save_btn.click()
    assert len(submitted_payloads) == 1
    assert form.result() == 0
    assert not form._error_label.isHidden()
    assert form._error_label.text() == "Trùng tên món"

    order_view = OrderView(ApiClient(), use_mock=True)
    order_view.resize(1060, 664)
    order_view.load()
    qapp.processEvents()
    assert order_view._menu_scroll.horizontalScrollBar().maximum() == 0

    win = MainWindow()
    monkeypatch.setattr(win._kiosk_view, "load", lambda: None)
    monkeypatch.setattr(win._dashboard_view, "load", lambda: None)

    assert isinstance(win._login_view, LoginView)
    win._login_view._kiosk_btn.click()
    assert win._root_stack.currentWidget() is win._kiosk_view

    win._close_kiosk()
    assert win._root_stack.currentWidget() is win._login_view

    win._on_login_success({"username": "staff01", "full_name": "Thu ngân", "role": "staff"})
    assert win._root_stack.currentWidget() is win._app_shell

    def _fail_logout() -> None:
        raise ApiClientError("NETWORK", "Mất kết nối", 0)

    monkeypatch.setattr(win.api, "logout", _fail_logout)
    win._handle_logout()
    assert win._logout_worker is not None
    win._logout_worker.wait(3000)
    qapp.processEvents()
    assert win.current_user is None
    assert win._root_stack.currentWidget() is win._login_view
    win.close()
