"""Kiểm thử đơn vị cho màn hình Tổng quan (Dashboard): KPI và biểu đồ.

Tuân thủ:
- docs/api-contract.md: Endpoint 20 (reports/revenue), 21 (reports/top-products).
- docs/test-cases.md: TC-RPT-01, TC-RPT-02.
"""

from datetime import date
from typing import Any

from gui.api_client import ApiClient, ApiClientError
from gui.i18n import format_currency, t
from gui.main import MainWindow
from gui.views.dashboard_view import (
    MOCK_TOP_PRODUCTS,
    DashboardView,
    build_mock_daily,
    normalize_revenue,
    normalize_top_products,
)


def test_mock_daily_has_30_increasing_days() -> None:
    """Dữ liệu mẫu đủ 30 ngày, tăng dần và có doanh thu dương."""
    rows = build_mock_daily(date(2026, 11, 17))
    assert len(rows) == 30
    assert rows[0]["date"] == "2026-10-19"
    assert rows[-1]["date"] == "2026-11-17"

    dates = [row["date"] for row in rows]
    assert dates == sorted(dates)
    assert all(row["revenue"] > 0 for row in rows)
    assert all(row["order_count"] > 0 for row in rows)


def test_normalize_revenue_accepts_dict_and_list() -> None:
    """Đọc được cả envelope dict lẫn list dòng doanh thu."""
    dict_payload: dict[str, Any] = {
        "total_revenue": 100000,
        "total_orders": 4,
        "daily": [
            {"date": "2026-11-16", "revenue": 40000, "order_count": 2},
            {"date": "2026-11-17", "revenue": 60000, "order_count": 2},
        ],
    }
    daily, total, orders = normalize_revenue(dict_payload)
    assert len(daily) == 2
    assert total == 100000
    assert orders == 4

    list_payload = [{"revenue": 30000, "order_count": 1}, {"revenue": 20000, "order_count": 1}]
    daily, total, orders = normalize_revenue(list_payload)
    assert len(daily) == 2
    assert total == 50000
    assert orders == 2

    assert normalize_revenue(None) == ([], 0, 0)


def test_normalize_top_products_accepts_variants() -> None:
    """Chuẩn hoá tên và số lượng từ các khoá response khác nhau."""
    payload = {
        "items": [
            {"name": "Trà đào cam sả", "quantity_sold": 12},
            {"product_name": "Cà phê đen đá", "total_quantity": 7},
        ]
    }
    products = normalize_top_products(payload)
    assert products == [
        {"name": "Trà đào cam sả", "quantity": 12},
        {"name": "Cà phê đen đá", "quantity": 7},
    ]
    assert normalize_top_products(None) == []


def test_dashboard_renders_kpis_and_charts(qapp: Any) -> None:
    """Màn hình hiển thị đúng 4 KPI, 2 biểu đồ và trạng thái dữ liệu."""
    view = DashboardView(ApiClient(), use_mock=True)
    payload = view._collect_mock_data()
    view._on_data(payload)

    assert view._state_stack.currentWidget() is view._data_widget

    today_row = payload["daily"][-1]
    assert view._kpi_values["revenue_today"].text() == format_currency(today_row["revenue"])
    assert view._kpi_values["orders_today"].text() == str(today_row["order_count"])
    assert view._kpi_values["revenue_period"].text() == format_currency(payload["total_revenue"])
    assert view._kpi_values["top_product"].text() == MOCK_TOP_PRODUCTS[0]["name"]

    assert len(view._revenue_chart.series()) == 1
    assert len(view._top_chart.series()) == 1
    assert len(view._top_chart.axes()) == 2


def test_dashboard_load_runs_worker_and_shows_data(qapp: Any) -> None:
    """load() nạp dữ liệu và chuyển sang trạng thái dữ liệu."""
    view = DashboardView(ApiClient(), use_mock=True)
    payload = view._collect_mock_data()
    view._on_data(payload)
    assert view._state_stack.currentWidget() is view._data_widget
    assert view._kpi_values["top_product"].text() == MOCK_TOP_PRODUCTS[0]["name"]


def test_dashboard_shows_empty_state(qapp: Any) -> None:
    """Không có dữ liệu báo cáo thì hiện trạng thái rỗng, không phải bảng trống."""
    view = DashboardView(ApiClient(), use_mock=True)
    view._on_data({"daily": [], "top": [], "total_revenue": 0, "total_orders": 0})

    assert view._state_stack.currentWidget() is view._empty_widget


def test_dashboard_staff_notice_and_navigation(qapp: Any) -> None:
    """Tài khoản staff khi vào Dashboard thấy thông báo quyền hạn và nút chuyển sang Bán hàng."""
    view = DashboardView(ApiClient(), use_mock=False)
    view.set_user_role("staff")
    assert view._user_role == "staff"

    # Worker thu thập thông báo staff
    payload = view._collect_staff_notice()
    assert payload == {"status": "staff_notice"}

    view._on_data(payload)
    assert view._state_stack.currentWidget() is view._empty_widget
    assert view._empty_label.text() == t("dashboard_staff_notice")
    assert not view._empty_action_btn.isHidden()
    assert view._empty_action_btn.text() == t("nav_orders")

    # Bấm nút hành động phát tín hiệu navigate_requested("orders")
    nav_targets: list[str] = []
    view.navigate_requested.connect(nav_targets.append)
    view._empty_action_btn.click()
    assert nav_targets == ["orders"]


def test_dashboard_admin_pending_api_fallback_to_demo(qapp: Any, monkeypatch: Any) -> None:
    """Khi API báo cáo chưa sẵn sàng (404), admin thấy thông báo chờ tích hợp và nút xem Demo."""
    api = ApiClient()

    def mock_get_revenue(*args: Any, **kwargs: Any) -> Any:
        raise ApiClientError(code="HTTP_404", message="Not Found")

    monkeypatch.setattr(api, "get_revenue_report", mock_get_revenue)

    view = DashboardView(api, use_mock=False)
    view.set_user_role("admin")

    # Khi gọi API bị 404, collect trả về status pending_api
    payload = view._collect_api_data()
    assert payload == {"status": "pending_api"}

    view._on_data(payload)
    assert view._state_stack.currentWidget() is view._empty_widget
    assert view._empty_label.text() == t("dashboard_pending_api")
    assert not view._empty_action_btn.isHidden()
    assert view._empty_action_btn.text() == t("dashboard_btn_demo")

    # Bấm nút Demo chuyển sang chế độ mock và tải lại
    reloaded: list[bool] = []
    monkeypatch.setattr(view, "load", lambda: reloaded.append(True))
    view._empty_action_btn.click()
    assert view._use_mock is True
    assert reloaded == [True]


def test_main_window_default_navigation_and_role_handling(qapp: Any, monkeypatch: Any) -> None:
    """MainWindow phân quyền vai trò cho Dashboard và điều hướng sang Order khi staff yêu cầu."""
    win = MainWindow()
    monkeypatch.setattr(win._dashboard_view, "load", lambda: None)
    monkeypatch.setattr(win._order_view, "load", lambda: None)

    # Khi admin đăng nhập thành công
    win._on_login_success(
        {"id": 1, "username": "admin", "full_name": "Quản trị viên", "role": "admin"}
    )
    assert win._dashboard_view._user_role == "admin"
    assert win._content_stack.currentWidget() is win._dashboard_view

    # Khi staff đăng nhập thành công
    win._on_login_success(
        {"id": 2, "username": "thungan01", "full_name": "Thu ngân 1", "role": "staff"}
    )
    assert win._dashboard_view._user_role == "staff"
    assert win._content_stack.currentWidget() is win._dashboard_view

    # Khi DashboardView của staff yêu cầu điều hướng sang orders
    win._dashboard_view.navigate_requested.emit("orders")
    assert win._content_stack.currentWidget() is win._order_view
    win.close()
