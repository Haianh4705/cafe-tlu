"""Kiểm thử đơn vị cho giao diện và logic trong màn hình Thực đơn (ProductListView)."""

from typing import Any

import pytest

from gui.api_client import ApiClient, ApiClientError
from gui.views.product_list_view import ProductListView, format_currency
from gui.widgets.product_dialog import ConfirmDeleteDialog, ProductFormDialog

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


def test_product_form_rejects_non_positive_price_before_submit(qapp: Any) -> None:
    """Giá âm bị QSpinBox chặn ở 0 và form không submit giá không hợp lệ."""
    submitted: list[dict[str, Any]] = []
    dialog = ProductFormDialog(
        [{"id": 1, "name": "Cà phê"}],
        on_submit=submitted.append,
    )
    dialog._name_input.setText("Cà phê mới")
    dialog._unit_input.setText("ly")

    dialog._price_spin.setValue(-1000)
    assert dialog._price_spin.value() == 0

    dialog._validate_and_accept()

    assert dialog.result() != ProductFormDialog.DialogCode.Accepted
    assert dialog._error_label.isHidden() is False
    assert submitted == []


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
    assert view._empty_action_btn.isHidden() is False
    assert view._empty_action_btn.text() == "Xoá bộ lọc"


def test_product_list_view_empty_filter_can_be_cleared(qapp: Any, monkeypatch: Any) -> None:
    """Khi tìm kiếm rỗng, thao tác Xoá bộ lọc đưa về trang đầu và giữ được điều hướng."""
    view = ProductListView(ApiClient())
    loads: list[tuple[bool, str, Any]] = []
    monkeypatch.setattr(
        view,
        "load_products",
        lambda reset_page=False: loads.append(
            (reset_page, view._search_input.text(), view._cat_combo.currentData())
        ),
    )
    view._search_input.setText("không có món này")
    view._cat_combo.blockSignals(True)
    view._cat_combo.addItem("Trà", 2)
    view._cat_combo.setCurrentIndex(1)
    view._cat_combo.blockSignals(False)
    view._page = 3
    view._on_products_loaded({"data": [], "meta": {"page": 1, "total": 0, "total_pages": 1}})

    assert view._empty_action_btn.text() == "Xoá bộ lọc"
    view._empty_action_btn.click()

    assert view._search_input.text() == ""
    assert view._cat_combo.currentData() is None
    assert loads == [(True, "", None)]


def test_deleting_only_item_on_last_page_loads_previous_valid_page(
    qapp: Any, monkeypatch: Any
) -> None:
    """Xoá món cuối trên trang cuối sẽ tải lại trang hợp lệ gần nhất."""
    view = ProductListView(ApiClient())
    view._page = 3
    requested_pages: list[int] = []
    monkeypatch.setattr(
        view, "load_products", lambda reset_page=False: requested_pages.append(view._page)
    )

    view._on_products_loaded({"data": [], "meta": {"page": 3, "total": 40, "total_pages": 2}})

    assert view._page == 2
    assert requested_pages == [2]


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


@pytest.mark.parametrize("edit_mode", [False, True], ids=["create", "edit"])
@pytest.mark.parametrize(
    "error",
    [
        ApiClientError("PRODUCT_NAME_DUPLICATED", "Tên món đã tồn tại"),
        ApiClientError("NETWORK_ERROR", "Không thể kết nối đến máy chủ API"),
    ],
    ids=["duplicate-name", "network-error"],
)
def test_product_form_keeps_input_when_save_fails(
    qapp: Any,
    monkeypatch: Any,
    edit_mode: bool,
    error: ApiClientError,
) -> None:
    """Lỗi thêm/sửa bật lại form, hiện lỗi và giữ nguyên nội dung người dùng nhập."""
    view = ProductListView(ApiClient())
    view.set_user_role("admin")
    view._categories = [{"id": 2, "name": "Trà"}]
    view._cat_combo.addItem("Trà", 2)
    workers: list[dict[str, Any]] = []
    monkeypatch.setattr(
        view,
        "start_worker",
        lambda func, on_success, on_error=None, *args, **kwargs: workers.append(
            {"func": func, "on_success": on_success, "on_error": on_error, **kwargs}
        ),
    )
    dialogs: list[ProductFormDialog] = []

    def submit_form(dialog: ProductFormDialog) -> int:
        dialog._name_input.setText("Trà đào mới")
        dialog._cat_combo.setCurrentIndex(dialog._cat_combo.findData(2))
        dialog._price_spin.setValue(42000)
        dialog._unit_input.setText("ly")
        dialog._validate_and_accept()
        dialogs.append(dialog)
        return dialog.result()

    monkeypatch.setattr(ProductFormDialog, "exec", submit_form)
    if edit_mode:
        view._open_edit_dialog(
            {"id": 17, "name": "Trà đào cũ", "category_id": 2, "price": 35000, "unit": "ly"}
        )
    else:
        view._open_add_dialog()

    dialog = dialogs[0]
    assert len(workers) == 1
    assert dialog._save_btn.isEnabled() is False
    workers[0]["on_error"](error)

    assert dialog.result() != ProductFormDialog.DialogCode.Accepted
    assert dialog._name_input.text() == "Trà đào mới"
    assert dialog._cat_combo.currentData() == 2
    assert dialog._price_spin.value() == 42000
    assert dialog._unit_input.text() == "ly"
    assert dialog._error_label.text() == error.message
    assert dialog._save_btn.isEnabled() is True


def test_product_form_closes_and_reloads_only_after_save_success(
    qapp: Any, monkeypatch: Any
) -> None:
    """Thêm món chỉ đóng form và tải danh sách sau phản hồi thành công."""
    view = ProductListView(ApiClient())
    view.set_user_role("admin")
    workers: list[dict[str, Any]] = []
    loads: list[bool] = []
    monkeypatch.setattr(
        view,
        "start_worker",
        lambda func, on_success, on_error=None, *args, **kwargs: workers.append(
            {"on_success": on_success, "on_error": on_error, **kwargs}
        ),
    )
    monkeypatch.setattr(view, "load_products", lambda: loads.append(True))
    dialogs: list[ProductFormDialog] = []

    def submit_form(dialog: ProductFormDialog) -> int:
        dialog._name_input.setText("Latte")
        dialog._price_spin.setValue(40000)
        dialog._validate_and_accept()
        dialogs.append(dialog)
        return dialog.result()

    monkeypatch.setattr(ProductFormDialog, "exec", submit_form)
    view._open_add_dialog()
    dialog = dialogs[0]
    assert dialog.result() != ProductFormDialog.DialogCode.Accepted
    assert loads == []

    workers[0]["on_success"]({"id": 1})

    assert dialog.result() == ProductFormDialog.DialogCode.Accepted
    assert loads == [True]


@pytest.mark.parametrize("succeeds", [False, True], ids=["failure", "success"])
def test_delete_result_is_reported_and_only_success_reloads(
    qapp: Any, monkeypatch: Any, succeeds: bool
) -> None:
    """Xoá thành công thì tải lại; thất bại hiện lỗi và không xoá danh sách cục bộ."""
    view = ProductListView(ApiClient())
    view.set_user_role("admin")
    view._on_products_loaded(
        {"data": [SAMPLE_PRODUCTS[0]], "meta": {"page": 1, "total": 1, "total_pages": 1}}
    )
    view._table.selectRow(0)
    monkeypatch.setattr(
        ConfirmDeleteDialog,
        "exec",
        lambda _dialog: ConfirmDeleteDialog.DialogCode.Accepted,
    )
    workers: list[dict[str, Any]] = []
    loads: list[bool] = []
    monkeypatch.setattr(
        view,
        "start_worker",
        lambda func, on_success, on_error=None, *args, **kwargs: workers.append(
            {"func": func, "on_success": on_success, "on_error": on_error, **kwargs}
        ),
    )
    monkeypatch.setattr(view, "load_products", lambda: loads.append(True))

    view._handle_delete_selected()
    assert workers[0]["product_id"] == SAMPLE_PRODUCTS[0]["id"]
    if succeeds:
        workers[0]["on_success"]({"id": SAMPLE_PRODUCTS[0]["id"]})
        assert loads == [True]
        assert view._products == [SAMPLE_PRODUCTS[0]]
    else:
        error = ApiClientError("NETWORK_ERROR", "Không thể xoá món do mất kết nối")
        workers[0]["on_error"](error)
        assert loads == []
        assert view._products == [SAMPLE_PRODUCTS[0]]
        assert view._state_stack.currentWidget() == view._error_widget
        assert view._error_label.text() == error.message
