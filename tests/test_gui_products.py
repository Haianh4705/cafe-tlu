"""Kiểm thử đơn vị cho logic và định dạng trong màn hình Thực đơn (ProductListView)."""

from gui.views.product_list_view import format_currency


def test_format_currency_vnd() -> None:
    """Kiểm tra định dạng tiền tệ Việt Nam đồng: 35.000 đ."""
    assert format_currency(35000) == "35.000 đ"
    assert format_currency(0) == "0 đ"
    assert format_currency(1250000) == "1.250.000 đ"
    assert format_currency(99000.0) == "99.000 đ"
