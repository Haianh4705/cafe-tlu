"""Màn hình Tổng quan (Dashboard) với 4 thẻ KPI và 2 biểu đồ trong CafeTLU.

Tuân thủ:
- docs/api-contract.md: Endpoint 20 (reports/revenue), 21 (reports/top-products).
- docs/test-cases.md: TC-RPT-01, TC-RPT-02.
- .claude/skills/ui-design/SKILL.md: lưới 8pt, màu Navy, số liệu đậm trên nhãn nhạt.
- .claude/skills/pyside6-screen/SKILL.md: 4 trạng thái, HTTP trên luồng nền, F5 làm mới.
"""

from datetime import date, datetime, timedelta, timezone
from typing import Any

from PySide6.QtCharts import (
    QBarCategoryAxis,
    QBarSet,
    QCategoryAxis,
    QChart,
    QChartView,
    QHorizontalBarSeries,
    QLineSeries,
    QValueAxis,
)
from PySide6.QtCore import QMargins, Qt, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from gui.api_client import ApiClient
from gui.i18n import format_currency, t
from gui.theme import COLOR, FONT, RADIUS, SPACE
from gui.views.base import BaseView

PERIOD_DAYS = 30
TOP_PRODUCT_LIMIT = 5
CAFE_TIMEZONE = timezone(timedelta(hours=7), name="Asia/Ho_Chi_Minh")


def _cafe_today() -> date:
    """Ngày lịch của quán theo timezone Việt Nam, không phụ thuộc timezone máy chạy GUI."""
    return datetime.now(CAFE_TIMEZONE).date()


# Dữ liệu mẫu chỉ dùng sau khi người dùng chủ động chọn Demo.
MOCK_TOP_PRODUCTS: list[dict[str, Any]] = [
    {"product_id": 4, "name": "Trà đào cam sả", "quantity": 58, "revenue": 2030000},
    {"product_id": 2, "name": "Cà phê sữa đá", "quantity": 51, "revenue": 1479000},
    {"product_id": 7, "name": "Matcha đá xay", "quantity": 44, "revenue": 1848000},
    {"product_id": 1, "name": "Cà phê đen đá", "quantity": 39, "revenue": 975000},
    {"product_id": 10, "name": "Tiramisu truyền thống", "quantity": 27, "revenue": 945000},
]


def build_mock_daily(today: date | None = None) -> list[dict[str, Any]]:
    """Sinh doanh thu mẫu 30 ngày ổn định để dựng và kiểm thử Dashboard."""
    end = today or _cafe_today()
    rows: list[dict[str, Any]] = []
    for offset in range(PERIOD_DAYS - 1, -1, -1):
        day = end - timedelta(days=offset)
        revenue = 1850000 + (day.day * 37000) % 420000
        if day.weekday() >= 5:
            revenue += 520000
        rows.append(
            {
                "date": day.isoformat(),
                "revenue": revenue,
                "order_count": max(8, revenue // 62000),
            }
        )
    return rows


def _row_revenue(row: dict[str, Any]) -> int:
    return int(row.get("revenue") or row.get("total_revenue") or 0)


def _row_orders(row: dict[str, Any]) -> int:
    return int(row.get("order_count") or row.get("orders") or row.get("total_orders") or 0)


def normalize_revenue(raw: Any) -> tuple[list[dict[str, Any]], int, int]:
    """Chuẩn hoá response báo cáo doanh thu về (daily, tổng doanh thu, tổng đơn)."""
    if isinstance(raw, list):
        daily, total, orders = raw, None, None
    elif isinstance(raw, dict):
        daily = raw.get("daily") or raw.get("items") or []
        total = raw.get("total_revenue")
        orders = raw.get("total_orders")
    else:
        daily, total, orders = [], None, None

    daily = [row for row in daily if isinstance(row, dict)]
    total = int(total) if total is not None else sum(_row_revenue(row) for row in daily)
    orders = int(orders) if orders is not None else sum(_row_orders(row) for row in daily)
    return daily, total, orders


def normalize_top_products(raw: Any) -> list[dict[str, Any]]:
    """Chuẩn hoá response top món về danh sách {name, quantity}."""
    if isinstance(raw, dict):
        raw = raw.get("items") or raw.get("products") or raw.get("top_products") or []
    if not isinstance(raw, list):
        return []

    products: list[dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        products.append(
            {
                "name": str(item.get("name") or item.get("product_name") or ""),
                "quantity": int(
                    item.get("quantity")
                    or item.get("quantity_sold")
                    or item.get("total_quantity")
                    or 0
                ),
            }
        )
    return products


def _chart_axis_font() -> QFont:
    return QFont(str(FONT["family"]), int(FONT["caption"]))


def _short_date(value: Any) -> str:
    text = str(value or "")[:10]
    try:
        return date.fromisoformat(text).strftime("%d/%m")
    except ValueError:
        return text


class DashboardView(BaseView):
    """Màn hình Tổng quan: 4 thẻ KPI + biểu đồ doanh thu và top món."""

    navigate_requested = Signal(str)

    def __init__(
        self,
        api_client: ApiClient,
        parent: QWidget | None = None,
        *,
        use_mock: bool | None = None,
    ) -> None:
        self.api = api_client
        self._user_role: str = "admin"
        # Dữ liệu mẫu chỉ bật sau khi người dùng chọn Demo trong Dashboard.
        self._use_mock = bool(use_mock)
        super().__init__(parent)
        self._init_dashboard_ui()

    def set_user_role(self, role: str) -> None:
        """Cập nhật vai trò người dùng để điều chỉnh giao diện phù hợp quyền hạn."""
        self._user_role = role

    def reset_session_demo(self) -> None:
        """Không để lựa chọn Demo của phiên trước ảnh hưởng phiên đăng nhập mới."""
        self._use_mock = False

    # ------------------------------------------------------------------
    # Dựng giao diện
    # ------------------------------------------------------------------
    def _init_dashboard_ui(self) -> None:
        title = QLabel(t("dashboard_title"), self)
        title.setStyleSheet(
            f"color: {COLOR['navy']}; font-size: {FONT['h1']}px; font-weight: bold;"
        )

        subtitle = QLabel(t("dashboard_subtitle"), self)
        subtitle.setStyleSheet(f"color: {COLOR['muted']}; font-size: {FONT['body']}px;")

        self._data_layout.addWidget(title)
        self._data_layout.addWidget(subtitle)

        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(SPACE["md"])
        self._kpi_values: dict[str, QLabel] = {}
        self._kpi_hints: dict[str, QLabel] = {}
        for key, label in (
            ("revenue_today", t("dashboard_kpi_revenue_today")),
            ("orders_today", t("dashboard_kpi_orders_today")),
            ("revenue_period", t("dashboard_kpi_revenue_period")),
            ("top_product", t("dashboard_kpi_top_product")),
        ):
            card, value_label, hint_label = self._create_kpi_card(label)
            self._kpi_values[key] = value_label
            self._kpi_hints[key] = hint_label
            kpi_row.addWidget(card, stretch=1)
        self._data_layout.addLayout(kpi_row)

        charts_row = QHBoxLayout()
        charts_row.setSpacing(SPACE["md"])
        revenue_panel, self._revenue_chart = self._create_chart_panel(t("dashboard_chart_revenue"))
        top_panel, self._top_chart = self._create_chart_panel(t("dashboard_chart_top_products"))
        charts_row.addWidget(revenue_panel, stretch=5)
        charts_row.addWidget(top_panel, stretch=4)
        self._data_layout.addLayout(charts_row, stretch=1)

    def _create_kpi_card(self, label_text: str) -> tuple[QFrame, QLabel, QLabel]:
        card = QFrame(self)
        card.setObjectName("kpiCard")
        card.setMinimumHeight(96)
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        card.setStyleSheet(
            f"QFrame#kpiCard {{ background-color: {COLOR['surface']}; "
            f"border: 1px solid {COLOR['border']}; border-radius: {RADIUS['md']}px; }}"
        )

        layout = QVBoxLayout(card)
        layout.setContentsMargins(SPACE["lg"], SPACE["md"], SPACE["lg"], SPACE["md"])
        layout.setSpacing(SPACE["xs"])

        label = QLabel(label_text, card)
        label.setStyleSheet(
            f"color: {COLOR['muted']}; font-size: {FONT['caption']}px; "
            f"font-weight: 600; background: transparent;"
        )

        value = QLabel("—", card)
        value.setStyleSheet(
            f"color: {COLOR['ink']}; font-size: {FONT['h1']}px; "
            f"font-weight: bold; background: transparent;"
        )
        value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        hint = QLabel("", card)
        hint.setStyleSheet(
            f"color: {COLOR['muted']}; font-size: {FONT['caption']}px; background: transparent;"
        )

        layout.addWidget(label)
        layout.addWidget(value)
        layout.addWidget(hint)
        return card, value, hint

    def _create_chart_panel(self, title_text: str) -> tuple[QFrame, QChart]:
        panel = QFrame(self)
        panel.setObjectName("chartPanel")
        panel.setStyleSheet(
            f"QFrame#chartPanel {{ background-color: {COLOR['surface']}; "
            f"border: 1px solid {COLOR['border']}; border-radius: {RADIUS['md']}px; }}"
        )

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(SPACE["sm"], SPACE["md"], SPACE["sm"], SPACE["md"])
        layout.setSpacing(SPACE["sm"])

        title = QLabel(title_text, panel)
        title.setStyleSheet(
            f"color: {COLOR['ink']}; font-size: {FONT['title']}px; "
            f"font-weight: bold; background: transparent;"
        )

        chart = QChart()
        chart.setBackgroundVisible(False)
        chart.setPlotAreaBackgroundVisible(False)
        chart.legend().setVisible(False)
        chart.setMargins(QMargins(0, 0, 0, 0))
        chart.setAnimationOptions(QChart.AnimationOption.NoAnimation)

        chart_view = QChartView(chart, panel)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        chart_view.setMinimumHeight(240)
        chart_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        chart_view.setStyleSheet("background: transparent; border: none;")

        layout.addWidget(title)
        layout.addWidget(chart_view, stretch=1)
        return panel, chart

    # ------------------------------------------------------------------
    # Nạp dữ liệu (luồng nền)
    # ------------------------------------------------------------------
    def load(self) -> None:
        self._set_state(self.STATE_LOADING)
        if self._use_mock:
            self.start_worker(self._collect_mock_data, self._on_data)
        elif self._user_role != "admin":
            self._on_data(self._collect_staff_notice())
        else:
            # Reports routes are not registered yet; don't issue requests that can only 404.
            self._on_data({"status": "pending_api"})

    def _collect_staff_notice(self) -> dict[str, Any]:
        return {"status": "staff_notice"}

    def _collect_mock_data(self) -> dict[str, Any]:
        daily, total, orders = normalize_revenue(build_mock_daily())
        return {
            "status": "ok",
            "daily": daily,
            "top": normalize_top_products(MOCK_TOP_PRODUCTS),
            "total_revenue": total,
            "total_orders": orders,
        }

    def _enable_mock_and_reload(self) -> None:
        self._use_mock = True
        self.load()

    def _on_data(self, payload: Any) -> None:
        if not isinstance(payload, dict):
            self._set_state(self.STATE_EMPTY, t("dashboard_empty"))
            return

        status = payload.get("status")
        if status == "staff_notice":
            self._set_state(
                self.STATE_EMPTY,
                message=t("dashboard_staff_notice"),
                action_text=t("nav_orders"),
                on_action=lambda: self.navigate_requested.emit("orders"),
            )
            return

        if status == "pending_api":
            self._set_state(
                self.STATE_EMPTY,
                message=t("dashboard_pending_api"),
                action_text=t("dashboard_btn_demo"),
                on_action=self._enable_mock_and_reload,
            )
            return

        daily: list[dict[str, Any]] = payload.get("daily") or []
        top: list[dict[str, Any]] = payload.get("top") or []

        if not daily and not top:
            self._set_state(self.STATE_EMPTY, t("dashboard_empty"))
            return

        self._update_kpis(daily, top, int(payload.get("total_revenue") or 0))
        self._render_revenue_chart(daily)
        self._render_top_products_chart(top[:TOP_PRODUCT_LIMIT])
        self._set_state(self.STATE_DATA)

    def _update_kpis(
        self, daily: list[dict[str, Any]], top: list[dict[str, Any]], total_revenue: int
    ) -> None:
        today_iso = _cafe_today().isoformat()
        today_row = next((row for row in daily if str(row.get("date") or "")[:10] == today_iso), {})
        today_revenue = _row_revenue(today_row)
        today_orders = _row_orders(today_row)

        self._kpi_values["revenue_today"].setText(format_currency(today_revenue))
        self._kpi_hints["revenue_today"].setText(t("dashboard_order_unit", count=today_orders))

        self._kpi_values["orders_today"].setText(str(today_orders))
        self._kpi_hints["orders_today"].setText(
            t("dashboard_today_hint", date=_short_date(today_iso))
        )

        self._kpi_values["revenue_period"].setText(
            format_currency(total_revenue or sum(_row_revenue(row) for row in daily))
        )
        total_orders = sum(_row_orders(row) for row in daily)
        self._kpi_hints["revenue_period"].setText(t("dashboard_order_unit", count=total_orders))

        if top:
            self._kpi_values["top_product"].setText(top[0]["name"] or t("dashboard_no_sales"))
            self._kpi_hints["top_product"].setText(
                t("dashboard_top_product_hint", quantity=top[0]["quantity"])
            )
        else:
            self._kpi_values["top_product"].setText(t("dashboard_no_sales"))
            self._kpi_hints["top_product"].setText("")

    # ------------------------------------------------------------------
    # Biểu đồ
    # ------------------------------------------------------------------
    def _render_revenue_chart(self, daily: list[dict[str, Any]]) -> None:
        self._reset_chart(self._revenue_chart)
        if not daily:
            return

        series = QLineSeries()
        for index, row in enumerate(daily):
            series.append(index, _row_revenue(row) / 1_000_000)

        pen = QPen(QColor(COLOR["navy"]))
        pen.setWidthF(2.0)
        series.setPen(pen)
        self._revenue_chart.addSeries(series)

        axis_x = QCategoryAxis()
        axis_x.setLabelsPosition(QCategoryAxis.AxisLabelsPosition.AxisLabelsPositionOnValue)
        axis_x.setRange(0, max(len(daily) - 1, 1))
        axis_x.setLabelsColor(QColor(COLOR["muted"]))
        axis_x.setLabelsFont(_chart_axis_font())
        step = max(1, len(daily) // 6)
        for index in range(0, len(daily), step):
            axis_x.append(_short_date(daily[index].get("date")), index)

        axis_y = QValueAxis()
        axis_y.setRange(0, max(_row_revenue(row) for row in daily) / 1_000_000 * 1.15 or 1)
        axis_y.setLabelFormat("%.1f")
        axis_y.setTitleText(t("dashboard_chart_revenue_axis"))
        axis_y.setLabelsColor(QColor(COLOR["muted"]))
        axis_y.setLabelsFont(_chart_axis_font())
        axis_y.setGridLineColor(QColor(COLOR["border"]))

        self._revenue_chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        self._revenue_chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)

    def _render_top_products_chart(self, top: list[dict[str, Any]]) -> None:
        self._reset_chart(self._top_chart)
        if not top:
            return

        items = list(reversed(top))
        bar_set = QBarSet(t("dashboard_chart_quantity"))
        bar_set.append([float(item["quantity"]) for item in items])
        bar_set.setColor(QColor(COLOR["navy"]))

        series = QHorizontalBarSeries()
        series.append(bar_set)
        self._top_chart.addSeries(series)

        axis_categories = QBarCategoryAxis()
        axis_categories.append([item["name"] for item in items])
        axis_categories.setLabelsColor(QColor(COLOR["muted"]))
        axis_categories.setLabelsFont(_chart_axis_font())

        axis_values = QValueAxis()
        axis_values.setRange(0, max(item["quantity"] for item in top) * 1.15 or 1)
        axis_values.setLabelFormat("%.0f")
        axis_values.setTitleText(t("dashboard_chart_quantity"))
        axis_values.setLabelsColor(QColor(COLOR["muted"]))
        axis_values.setLabelsFont(_chart_axis_font())
        axis_values.setGridLineColor(QColor(COLOR["border"]))

        self._top_chart.addAxis(axis_categories, Qt.AlignmentFlag.AlignLeft)
        self._top_chart.addAxis(axis_values, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_categories)
        series.attachAxis(axis_values)

    @staticmethod
    def _reset_chart(chart: QChart) -> None:
        chart.removeAllSeries()
        for axis in chart.axes():
            chart.removeAxis(axis)
