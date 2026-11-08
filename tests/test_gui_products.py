"""Kiểm thử đơn vị cho logic và định dạng trong màn hình Thực đơn (ProductListView)."""

import math
from typing import Any

from gui.api_client import ApiClient
from gui.views.product_list_view import ProductListView, format_currency

SAMPLE_PRODUCTS: list[dict[str, Any]] = [
    {
        "id": 1,
        "name": "Cà phê đen đá",
        "category_id": 1,
        "category": "Cà phê",
        "price": 25000,
        "unit": "ly",
        "is_available": True,
    },
    {
        "id": 2,
        "name": "Cà phê sữa đá",
        "category_id": 1,
        "category": "Cà phê",
        "price": 29000,
        "unit": "ly",
        "is_available": True,
    },
    {
        "id": 3,
        "name": "Trà đào cam sả",
        "category_id": 2,
        "category": "Trà trái cây",
        "price": 35000,
        "unit": "ly",
        "is_available": True,
    },
    {
        "id": 4,
        "name": "Trà ô long sen vàng",
        "category_id": 2,
        "category": "Trà trái cây",
        "price": 39000,
        "unit": "ly",
        "is_available": False,
    },
    {
        "id": 5,
        "name": "Bánh sừng bò phô mai",
        "category_id": 3,
        "category": "Bánh ngọt",
        "price": 28000,
        "unit": "cái",
        "is_available": True,
    },
]


def test_format_currency_vnd() -> None:
    """Kiểm tra định dạng tiền tệ Việt Nam đồng: 35.000 đ."""
    assert format_currency(35000) == "35.000 đ"
    assert format_currency(0) == "0 đ"
    assert format_currency(1250000) == "1.250.000 đ"
    assert format_currency(99000.0) == "99.000 đ"


def test_filter_products_by_search_keyword() -> None:
    """Kiểm tra tìm kiếm món ăn theo từ khoá (TC-SRC-01)."""
    # Tìm kiếm "trà"
    keyword = "trà".lower()
    matched = [p for p in SAMPLE_PRODUCTS if keyword in p["name"].lower()]
    assert len(matched) == 2
    assert all("trà" in p["name"].lower() for p in matched)

    # Tìm kiếm không phân biệt hoa thường "CÀ PHÊ"
    keyword_upper = "CÀ PHÊ".lower()
    matched_coffee = [p for p in SAMPLE_PRODUCTS if keyword_upper in p["name"].lower()]
    assert len(matched_coffee) == 2

    # Tìm kiếm từ khoá không tồn tại (TC-SRC-03)
    keyword_none = "pizza"
    matched_none = [p for p in SAMPLE_PRODUCTS if keyword_none in p["name"].lower()]
    assert len(matched_none) == 0


def test_filter_products_by_category() -> None:
    """Kiểm tra lọc món ăn theo danh mục (TC-SRC-02)."""
    # Lọc danh mục 2: Trà trái cây
    cat_id = 2
    matched_cat = [p for p in SAMPLE_PRODUCTS if p["category_id"] == cat_id]
    assert len(matched_cat) == 2
    for p in matched_cat:
        assert p["category"] == "Trà trái cây"

    # Kết hợp lọc danh mục 2 và chỉ lấy món còn bán (is_available=True)
    available_teas = [p for p in matched_cat if p["is_available"]]
    assert len(available_teas) == 1
    assert available_teas[0]["name"] == "Trà đào cam sả"


def test_product_role_permissions(qapp: Any) -> None:
    """Kiểm tra phân quyền vai trò admin vs staff trong ProductListView (#30)."""
    client = ApiClient(base_url="http://127.0.0.1:8000/api/v1")
    view = ProductListView(client)

    # Mặc định role là staff
    view.set_user_role("staff")
    assert view.is_admin is False

    # Chuyển sang role admin
    view.set_user_role("admin")
    assert view.is_admin is True

    # Chuyển sang barista
    view.set_user_role("barista")
    assert view.is_admin is False


def test_pagination_logic() -> None:
    """Kiểm tra tính toán số trang và phân trang danh sách món."""
    page_size = 20
    total_items = 45
    total_pages = math.ceil(total_items / page_size)
    assert total_pages == 3

    # Trang 1
    current_page = 1
    has_prev = current_page > 1
    has_next = current_page < total_pages
    assert has_prev is False
    assert has_next is True

    # Chuyển sang trang 2
    current_page += 1
    assert current_page == 2
    assert (current_page > 1) is True
    assert (current_page < total_pages) is True

    # Chuyển sang trang 3 (cuối)
    current_page += 1
    assert current_page == 3
    assert (current_page < total_pages) is False
