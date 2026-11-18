"""Kiểm thử đơn vị cho giao diện và logic trong màn hình Thực đơn (ProductListView)."""

from typing import Any

from gui.api_client import ApiClient
from gui.views.product_list_view import ProductListView, format_currency
from gui.widgets.product_dialog import ConfirmDeleteDialog

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


def test_product_list_view_render_table(qapp: Any) -> None:
    """Kiểm tra ProductListView điền dữ liệu vào bảng và định dạng các cột (TC-PRD-01)."""
    client = ApiClient(base_url="http://127.0.0.1:8000/api/v1")
    view = ProductListView(client)

    payload = {
        "data": SAMPLE_PRODUCTS,
        "meta": {"page": 1, "page_size": 20, "total": len(SAMPLE_PRODUCTS), "total_pages": 1},
    }
    view._on_products_loaded(payload)

    assert view._table.rowCount() == 5
    # Cột ID
    assert view._table.item(0, 0).text() == "#1"
    # Cột Tên món
    assert view._table.item(0, 1).text() == "Cà phê đen đá"
    # Cột Đơn giá
    assert view._table.item(0, 3).text() == "25.000 đ"
    # Cột Đơn vị
    assert view._table.item(0, 4).text() == "ly"
    # Cột Trạng thái
    assert view._table.item(0, 5).text() == "Còn bán"
    assert view._table.item(3, 5).text() == "Tạm hết"
    # Nhãn số lượng
    assert view._count_label.text() == "Hiển thị 5 / 5 món"


def test_product_list_view_pagination_with_meta(qapp: Any) -> None:
    """Kiểm tra xử lý meta phân trang từ API và cập nhật trạng thái nút chuyển trang (#30)."""
    client = ApiClient(base_url="http://127.0.0.1:8000/api/v1")
    view = ProductListView(client)

    payload = {
        "data": SAMPLE_PRODUCTS[:2],
        "meta": {"page": 2, "page_size": 20, "total": 45, "total_pages": 3},
    }
    view._on_products_loaded(payload)

    assert view._page == 2
    assert view._total_pages == 3
    assert view._total_count == 45
    assert view._table.rowCount() == 2
    assert "Trang 2 / 3" in view._page_label.text()
    assert "Hiển thị 2 / 45 món" in view._count_label.text()

    # Trang 2 ở giữa: Cả nút trước và sau đều bật
    assert view._prev_page_btn.isEnabled() is True
    assert view._next_page_btn.isEnabled() is True


def test_product_list_view_pagination_boundaries(qapp: Any) -> None:
    """Kiểm tra các nút điều hướng phân trang bị vô hiệu hoá ở ranh giới trang đầu và cuối."""
    client = ApiClient(base_url="http://127.0.0.1:8000/api/v1")
    view = ProductListView(client)

    # Trang 1 / 3: Không có trang trước
    view._on_products_loaded(
        {
            "data": SAMPLE_PRODUCTS[:2],
            "meta": {"page": 1, "page_size": 20, "total": 50, "total_pages": 3},
        }
    )
    assert view._prev_page_btn.isEnabled() is False
    assert view._next_page_btn.isEnabled() is True

    # Trang 3 / 3: Không có trang sau
    view._on_products_loaded(
        {
            "data": SAMPLE_PRODUCTS[:2],
            "meta": {"page": 3, "page_size": 20, "total": 50, "total_pages": 3},
        }
    )
    assert view._prev_page_btn.isEnabled() is True
    assert view._next_page_btn.isEnabled() is False


def test_product_list_view_reset_page_on_search(qapp: Any) -> None:
    """Kiểm tra khi tìm kiếm hoặc lọc danh mục thì trang tự động reset về trang 1."""
    client = ApiClient(base_url="http://127.0.0.1:8000/api/v1")
    view = ProductListView(client)
    view._page = 4

    view.load_products(reset_page=True)
    assert view._page == 1


def test_product_list_view_empty_state_on_search_not_found(qapp: Any) -> None:
    """Kiểm tra hiển thị trạng thái rỗng khi tìm kiếm từ khoá không tồn tại (TC-SRC-03)."""
    client = ApiClient(base_url="http://127.0.0.1:8000/api/v1")
    view = ProductListView(client)
    view._search_input.setText("trà sữa trân châu 12345")

    # Giả lập API trả về mảng rỗng
    view._on_products_loaded(
        {"data": [], "meta": {"page": 1, "page_size": 20, "total": 0, "total_pages": 1}}
    )

    assert view._state_stack.currentWidget() == view._empty_widget
    assert "Không tìm thấy món ăn nào khớp với" in view._empty_label.text()
    # Bộ lọc và thanh tìm kiếm nằm ngoài phần rỗng nên vẫn hiển thị để người dùng sửa từ khoá (#82)
    assert not view._search_input.isHidden()
    assert view._search_input.text() == "trà sữa trân châu 12345"
    assert not view._cat_combo.isHidden()
    assert not view._empty_action_btn.isHidden()


def test_product_role_permissions(qapp: Any) -> None:
    """Kiểm tra phân quyền vai trò admin vs staff trong ProductListView (#30)."""
    client = ApiClient(base_url="http://127.0.0.1:8000/api/v1")
    view = ProductListView(client)

    # Vai trò staff: Không thấy nút Thêm món, is_admin là False
    view.set_user_role("staff")
    assert view.is_admin is False
    assert view._add_btn.isHidden() is True

    # Vai trò admin: Thấy nút Thêm món, is_admin là True
    view.set_user_role("admin")
    assert view.is_admin is True
    assert view._add_btn.isHidden() is False

    # Vai trò barista: Không có quyền admin
    view.set_user_role("barista")
    assert view.is_admin is False
    assert view._add_btn.isHidden() is True


def test_product_find_category_name(qapp: Any) -> None:
    """Kiểm tra tra cứu tên danh mục từ ID trong ProductListView."""
    client = ApiClient(base_url="http://127.0.0.1:8000/api/v1")
    view = ProductListView(client)
    view._categories = [
        {"id": 1, "name": "Cà phê"},
        {"id": 2, "name": "Trà trái cây"},
    ]
    assert view._find_category_name(1) == "Cà phê"
    assert view._find_category_name(2) == "Trà trái cây"
    assert view._find_category_name(99) == "—"
    assert view._find_category_name(None) == "—"


def test_product_list_view_empty_state_can_clear_or_edit_filter(
    qapp: Any, monkeypatch: Any
) -> None:
    """Đã tìm không ra vẫn sửa hoặc xóa được bộ lọc để thấy danh sách trở lại (#82)."""
    client = ApiClient(base_url="http://127.0.0.1:8000/api/v1")
    view = ProductListView(client)
    view._search_input.setText("tên không có")

    # Giả lập khi tìm kiếm rỗng
    view._on_products_loaded(
        {"data": [], "meta": {"page": 1, "page_size": 20, "total": 0, "total_pages": 1}}
    )
    assert view._state_stack.currentWidget() == view._empty_widget

    # Ca 1: Bấm nút Xoá bộ lọc -> reset ô tìm kiếm và gọi lại load_products
    loaded_params: list[dict[str, Any]] = []

    def mock_load(reset_page: bool = False) -> None:
        loaded_params.append(
            {"page": view._page, "search": view._search_input.text(), "reset": reset_page}
        )

    monkeypatch.setattr(view, "load_products", mock_load)

    view._empty_action_btn.click()
    assert view._search_input.text() == ""
    assert len(loaded_params) == 1
    assert loaded_params[0]["reset"] is True

    # Ca 2: Người dùng sửa từ khoá tìm kiếm trực tiếp trên ô tìm kiếm vẫn mở
    view._search_input.setText("Cà phê")
    view._search_input.returnPressed.emit()
    assert len(loaded_params) == 2
    assert loaded_params[1]["search"] == "Cà phê"


def test_product_list_view_delete_last_item_on_last_page_returns_to_previous_page(
    qapp: Any, monkeypatch: Any
) -> None:
    """Xóa món duy nhất trên trang cuối sẽ tự động lùi về trang hợp lệ trước đó (#82)."""
    client = ApiClient(base_url="http://127.0.0.1:8000/api/v1")
    view = ProductListView(client)
    view.set_user_role("admin")

    # Giả lập trang 3 có đúng 1 món duy nhất
    view._page = 3
    view._total_pages = 3
    view._total_count = 41
    view._products = [SAMPLE_PRODUCTS[0]]
    view._render_table()
    view._table.selectRow(0)

    # Mock dialog xác nhận xoá luôn chấp nhận
    monkeypatch.setattr(
        ConfirmDeleteDialog, "exec", lambda self: ConfirmDeleteDialog.DialogCode.Accepted
    )

    # Bắt worker gọi API delete
    reloaded_pages: list[int] = []

    def mock_start_worker(func: Any, on_success: Any, on_error: Any = None, **kwargs: Any) -> None:
        # Gọi on_success để mô phỏng API xoá thành công
        on_success(None)

    def mock_load_products(reset_page: bool = False) -> None:
        reloaded_pages.append(view._page)

    monkeypatch.setattr(view, "start_worker", mock_start_worker)
    monkeypatch.setattr(view, "load_products", mock_load_products)

    view._handle_delete_selected()

    # Trang phải được giảm từ 3 về 2
    assert view._page == 2
    assert reloaded_pages == [2]


def test_product_list_view_auto_retreats_when_page_reloaded_is_empty(
    qapp: Any, monkeypatch: Any
) -> None:
    """Khi nạp một trang bị rỗng nhưng tổng số món > 0, tự động lùi về trang hợp lệ (#82)."""
    client = ApiClient(base_url="http://127.0.0.1:8000/api/v1")
    view = ProductListView(client)
    view._page = 2

    reloaded_pages: list[int] = []
    monkeypatch.setattr(view, "load_products", lambda: reloaded_pages.append(view._page))

    # Giả lập trang 2 trả về 0 món, nhưng DB còn 20 món (1 trang duy nhất)
    view._on_products_loaded(
        {"data": [], "meta": {"page": 2, "page_size": 20, "total": 20, "total_pages": 1}}
    )

    assert view._page == 1
    assert reloaded_pages == [1]
