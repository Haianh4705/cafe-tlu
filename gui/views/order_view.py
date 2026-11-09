"""Màn hình Bán hàng / Gọi món tại bàn (OrderView) trong CafeTLU.

Tuân thủ:
- docs/api-contract.md: Endpoint 8 (products), 13 (tables), 14-19 (orders & checkout).
- docs/test-cases.md: TC-ORD-01 đến TC-ORD-03.
- .claude/skills/ui-design/SKILL.md: Bố cục POS 3 cột khoa học, tương phản cao, bảng màu TLU.
- .claude/skills/pyside6-screen/SKILL.md: 4 trạng thái, HTTP trên luồng nền, phím tắt Ctrl+F/F5.
"""

import logging
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from gui.api_client import ApiClient
from gui.i18n import format_currency, t
from gui.theme import COLOR, FONT, RADIUS, SPACE
from gui.views.base import BaseView
from gui.widgets.checkout_dialog import CheckoutDialog
from gui.widgets.order_cart import OrderCartWidget
from gui.widgets.receipt_dialog import ReceiptDialog
from gui.widgets.table_card import TableCardWidget

logger = logging.getLogger(__name__)


# Dữ liệu dự phòng mẫu để kiểm thử khi API backend chưa triển khai xong
MOCK_TABLES: list[dict[str, Any]] = [
    {"id": i, "name": f"Bàn {i:02d}", "capacity": 4 if i % 3 != 0 else 6, "status": "free"}
    for i in range(1, 13)
]

MOCK_PRODUCTS: list[dict[str, Any]] = [
    {
        "id": 1,
        "name": "Cà phê đen đá",
        "category": "Cà phê",
        "price": 25000,
        "unit": "ly",
        "is_available": True,
    },
    {
        "id": 2,
        "name": "Cà phê sữa đá",
        "category": "Cà phê",
        "price": 29000,
        "unit": "ly",
        "is_available": True,
    },
    {
        "id": 3,
        "name": "Bạc xỉu Thăng Long",
        "category": "Cà phê",
        "price": 32000,
        "unit": "ly",
        "is_available": True,
    },
    {
        "id": 4,
        "name": "Trà đào cam sả",
        "category": "Trà trái cây",
        "price": 35000,
        "unit": "ly",
        "is_available": True,
    },
    {
        "id": 5,
        "name": "Trà ô long vải",
        "category": "Trà trái cây",
        "price": 35000,
        "unit": "ly",
        "is_available": True,
    },
    {
        "id": 6,
        "name": "Trà sen vàng",
        "category": "Trà trái cây",
        "price": 39000,
        "unit": "ly",
        "is_available": True,
    },
    {
        "id": 7,
        "name": "Matcha đá xay",
        "category": "Đá xay",
        "price": 42000,
        "unit": "ly",
        "is_available": True,
    },
    {
        "id": 8,
        "name": "Sô-cô-la đá xay",
        "category": "Đá xay",
        "price": 42000,
        "unit": "ly",
        "is_available": True,
    },
    {
        "id": 9,
        "name": "Bánh sừng bò phô mai",
        "category": "Bánh ngọt",
        "price": 28000,
        "unit": "cái",
        "is_available": True,
    },
    {
        "id": 10,
        "name": "Tiramisu truyền thống",
        "category": "Bánh ngọt",
        "price": 35000,
        "unit": "cái",
        "is_available": True,
    },
]


class OrderView(BaseView):
    """Màn hình Bán hàng & Gọi món tại bàn dạng POS."""

    def __init__(self, api_client: ApiClient, parent: QWidget | None = None) -> None:
        self.api = api_client
        self._tables: list[dict[str, Any]] = []
        self._products: list[dict[str, Any]] = []
        self._selected_table: dict[str, Any] | None = None
        self._table_cards: dict[int, TableCardWidget] = {}
        # Lưu trữ giỏ hàng từng bàn ở client: table_id -> list[items]
        self._table_orders: dict[int, list[dict[str, Any]]] = {}
        self.cashier_name: str = "Thu ngân"

        super().__init__(parent)
        self._init_pos_ui()
        self._setup_shortcuts()

    def _init_pos_ui(self) -> None:
        """Khởi tạo bố cục POS 3 cột khoa học."""
        self._data_layout.setContentsMargins(SPACE["md"], SPACE["md"], SPACE["md"], SPACE["md"])
        self._data_layout.setSpacing(SPACE["md"])

        # 1. Tiêu đề chính màn hình
        top_bar = QHBoxLayout()
        title_lbl = QLabel(t("order_title"), self)
        title_lbl.setStyleSheet(
            f"color: {COLOR['navy']}; font-size: {FONT['h1']}px; font-weight: bold;"
        )
        top_bar.addWidget(title_lbl)
        top_bar.addStretch()

        refresh_btn = QPushButton(t("refresh"), self)
        refresh_btn.setProperty("variant", "secondary")
        refresh_btn.setFixedHeight(34)
        refresh_btn.clicked.connect(self.refresh)
        top_bar.addWidget(refresh_btn)
        self._data_layout.addLayout(top_bar)

        # 2. Khung 3 cột làm việc
        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(SPACE["md"])

        # --- CỘT 1: Sơ đồ bàn (Width 280px) ---
        table_panel = self._build_table_panel()
        columns_layout.addWidget(table_panel)

        # --- CỘT 2: Thực đơn món (Stretch = 2) ---
        menu_panel = self._build_menu_panel()
        columns_layout.addWidget(menu_panel, stretch=2)

        # --- CỘT 3: Giỏ hàng / Đơn hàng (Width 380px) ---
        cart_panel = self._build_cart_panel()
        columns_layout.addWidget(cart_panel)

        self._data_layout.addLayout(columns_layout, stretch=1)

    def _build_table_panel(self) -> QWidget:
        panel = QFrame(self)
        panel.setFixedWidth(290)
        panel.setStyleSheet(
            f"QFrame {{ background-color: {COLOR['surface']}; "
            f"border: 1px solid {COLOR['border']}; border-radius: {RADIUS['md']}px; }}"
        )
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(SPACE["sm"], SPACE["md"], SPACE["sm"], SPACE["md"])
        layout.setSpacing(SPACE["sm"])

        title = QLabel(t("nav_tables"), panel)
        title.setStyleSheet(
            f"font-size: {FONT['title']}px; font-weight: bold; color: {COLOR['navy']}; border: none;"
        )
        layout.addWidget(title)

        # Bộ lọc bàn (Tất cả / Trống / Có khách)
        self._table_filter_combo = QComboBox(panel)
        self._table_filter_combo.setFixedHeight(32)
        self._table_filter_combo.addItem(t("table_all"), "all")
        self._table_filter_combo.addItem(t("table_filter_free"), "free")
        self._table_filter_combo.addItem(t("table_filter_occupied"), "occupied")
        self._table_filter_combo.currentIndexChanged.connect(self._filter_tables)
        layout.addWidget(self._table_filter_combo)

        # Vùng cuộn danh sách bàn
        scroll = QScrollArea(panel)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")

        self._table_container = QWidget()
        self._table_container.setStyleSheet("background: transparent;")
        self._table_layout = QVBoxLayout(self._table_container)
        self._table_layout.setContentsMargins(0, 0, 0, 0)
        self._table_layout.setSpacing(SPACE["xs"])
        self._table_layout.addStretch()

        scroll.setWidget(self._table_container)
        layout.addWidget(scroll, stretch=1)
        return panel

    def _build_menu_panel(self) -> QWidget:
        panel = QFrame(self)
        panel.setStyleSheet(
            f"QFrame {{ background-color: {COLOR['surface']}; "
            f"border: 1px solid {COLOR['border']}; border-radius: {RADIUS['md']}px; }}"
        )
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(SPACE["md"], SPACE["md"], SPACE["md"], SPACE["md"])
        layout.setSpacing(SPACE["sm"])

        # Thanh tìm kiếm và lọc danh mục
        filter_bar = QHBoxLayout()
        filter_bar.setSpacing(SPACE["sm"])

        self._search_input = QLineEdit(panel)
        self._search_input.setPlaceholderText(t("product_search_placeholder"))
        self._search_input.setFixedHeight(34)
        self._search_input.textChanged.connect(self._filter_products)
        filter_bar.addWidget(self._search_input, stretch=3)

        self._category_combo = QComboBox(panel)
        self._category_combo.setFixedHeight(34)
        self._category_combo.addItem(t("product_all_categories"), "all")
        self._category_combo.currentIndexChanged.connect(self._filter_products)
        filter_bar.addWidget(self._category_combo, stretch=2)
        layout.addLayout(filter_bar)

        # Danh sách thẻ món ăn
        scroll = QScrollArea(panel)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")

        self._menu_container = QWidget()
        self._menu_container.setStyleSheet("background: transparent;")
        self._menu_grid = QGridLayout(self._menu_container)
        self._menu_grid.setContentsMargins(0, 0, 0, 0)
        self._menu_grid.setSpacing(SPACE["sm"])

        scroll.setWidget(self._menu_container)
        layout.addWidget(scroll, stretch=1)
        return panel

    def _build_cart_panel(self) -> QWidget:
        self._cart_widget = OrderCartWidget(self)
        self._cart_widget.setFixedWidth(380)
        self._cart_widget.checkout_requested.connect(self._open_checkout_dialog)
        self._cart_widget.cancel_order_requested.connect(self._handle_cancel_order)
        self._cart_widget.item_quantity_changed.connect(self._sync_cart_to_table_order)
        self._cart_widget.item_removed.connect(self._sync_cart_to_table_order)
        return self._cart_widget

    def _setup_shortcuts(self) -> None:
        shortcut_search = QShortcut(QKeySequence("Ctrl+F"), self)
        shortcut_search.activated.connect(self._focus_search)

        shortcut_f1 = QShortcut(QKeySequence("F1"), self)
        shortcut_f1.activated.connect(self._focus_search)

        shortcut_f2 = QShortcut(QKeySequence("F2"), self)
        shortcut_f2.activated.connect(self._open_checkout_dialog)

        shortcut_refresh = QShortcut(QKeySequence("F5"), self)
        shortcut_refresh.activated.connect(self.refresh)

    def _focus_search(self) -> None:
        self._search_input.setFocus()
        self._search_input.selectAll()

    # ------------------------------------------------------------------
    # Nạp dữ liệu (Lifecycle)
    # ------------------------------------------------------------------
    def load(self) -> None:
        """Nạp danh sách bàn và thực đơn món."""
        self._set_state(self.STATE_LOADING)

        def fetch_data() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
            # Gọi API lấy bàn và thực đơn
            try:
                tables = self.api.get_tables() or []
            except Exception as exc:
                logger.warning("Không thể lấy /tables từ API (%s), dùng dữ liệu giả lập", exc)
                tables = MOCK_TABLES

            try:
                products_res = self.api.get_products()
                if isinstance(products_res, dict):
                    products = products_res.get("data") or []
                elif isinstance(products_res, list):
                    products = products_res
                else:
                    products = []
            except Exception as exc:
                logger.warning("Không thể lấy /products từ API (%s), dùng dữ liệu giả lập", exc)
                products = MOCK_PRODUCTS

            return tables or MOCK_TABLES, products or MOCK_PRODUCTS

        self.start_worker(
            fetch_data,
            on_success=self._on_data_loaded,
            on_error=self._on_load_error,
        )

    def _on_data_loaded(self, result: tuple[list[dict[str, Any]], list[dict[str, Any]]]) -> None:
        tables, products = result
        self._tables = tables
        self._products = products

        # Cập nhật danh mục vào ComboBox
        categories = sorted({p.get("category", "") for p in products if p.get("category")})
        self._category_combo.blockSignals(True)
        self._category_combo.clear()
        self._category_combo.addItem(t("product_all_categories"), "all")
        for cat in categories:
            self._category_combo.addItem(cat, cat)
        self._category_combo.blockSignals(False)

        self._render_tables()
        self._filter_products()

        # Chọn bàn đầu tiên nếu chưa chọn bàn nào
        if not self._selected_table and self._tables:
            self._select_table(self._tables[0])

        self._set_state(self.STATE_DATA)

    def _on_load_error(self, exc: Exception) -> None:
        logger.error("Lỗi khi tải dữ liệu OrderView: %s", exc)
        self.set_error_state(f"Không thể kết nối máy chủ: {exc}", on_retry=self.load)

    # ------------------------------------------------------------------
    # Xử lý Bàn (Tables)
    # ------------------------------------------------------------------
    def _render_tables(self) -> None:
        # Xóa các card bàn cũ
        while self._table_layout.count() > 1:
            item = self._table_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._table_cards.clear()

        filter_status = self._table_filter_combo.currentData()
        for tbl in self._tables:
            status = tbl.get("status", "free")
            if filter_status != "all" and status != filter_status:
                continue

            t_id = tbl.get("id", 0)
            is_active = self._selected_table and self._selected_table.get("id") == t_id
            card = TableCardWidget(tbl, is_active=bool(is_active), parent=self._table_container)
            card.selected.connect(self._select_table)
            self._table_cards[t_id] = card
            self._table_layout.insertWidget(self._table_layout.count() - 1, card)

    def _filter_tables(self) -> None:
        self._render_tables()

    def _select_table(self, table_data: dict[str, Any]) -> None:
        self._selected_table = table_data
        t_id = table_data.get("id", 0)

        # Cập nhật visual active cho các card
        for cid, card in self._table_cards.items():
            card.set_active(cid == t_id)

        # Cập nhật giỏ hàng theo bàn đã chọn
        self._cart_widget.set_table(table_data)
        saved_items = self._table_orders.get(t_id, [])
        self._cart_widget.set_items(saved_items)

    # ------------------------------------------------------------------
    # Xử lý Thực đơn (Menu)
    # ------------------------------------------------------------------
    def _filter_products(self) -> None:
        query = self._search_input.text().strip().lower()
        cat_filter = self._category_combo.currentData()

        # Dọn sạch menu grid cũ
        while self._menu_grid.count() > 0:
            item = self._menu_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        filtered = []
        for p in self._products:
            name = p.get("name", "").lower()
            cat = p.get("category", "")
            if query and query not in name:
                continue
            if cat_filter != "all" and cat != cat_filter:
                continue
            filtered.append(p)

        # Vẽ các card món ăn dạng lưới (2 cột)
        cols = 2
        for idx, prod in enumerate(filtered):
            card = self._build_product_card(prod)
            row = idx // cols
            col = idx % cols
            self._menu_grid.addWidget(card, row, col)

    def _build_product_card(self, prod: dict[str, Any]) -> QWidget:
        card = QFrame(self._menu_container)
        card.setFixedHeight(80)
        card.setStyleSheet(
            f"QFrame {{ background-color: {COLOR['surface_subtle']}; "
            f"border: 1px solid {COLOR['border']}; border-radius: {RADIUS['sm']}px; }}"
            f"QFrame:hover {{ border-color: {COLOR['brand_400']}; "
            f"background-color: {COLOR['tint_100']}; }}"
        )
        card.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(SPACE["md"], SPACE["sm"], SPACE["md"], SPACE["sm"])

        info_box = QVBoxLayout()
        info_box.setSpacing(2)

        name_lbl = QLabel(prod.get("name", "Món"), card)
        name_lbl.setStyleSheet(
            f"font-size: {FONT['label']}px; font-weight: bold; color: {COLOR['ink']}; border: none;"
        )
        price_lbl = QLabel(format_currency(prod.get("price", 0)), card)
        price_lbl.setStyleSheet(
            f"font-size: {FONT['caption']}px; font-weight: bold; color: {COLOR['navy']}; border: none;"
        )
        info_box.addWidget(name_lbl)
        info_box.addWidget(price_lbl)
        layout.addLayout(info_box, stretch=1)

        add_btn = QPushButton("+ Thêm", card)
        add_btn.setFixedSize(68, 28)
        add_btn.setStyleSheet(
            f"QPushButton {{ background-color: {COLOR['navy']}; color: {COLOR['surface']}; "
            f"border-radius: {RADIUS['sm']}px; font-weight: 600; min-height: 0px; padding: 0px; }} "
            f"QPushButton:hover {{ background-color: {COLOR['navy_600']}; }}"
        )
        add_btn.clicked.connect(lambda _, p=prod: self._add_product_to_cart(p))
        layout.addWidget(add_btn)

        return card

    def _add_product_to_cart(self, product: dict[str, Any]) -> None:
        if not self._selected_table:
            QMessageBox.information(self, "Thông báo", t("order_select_table_hint"))
            return

        self._cart_widget.add_product(product)
        self._sync_cart_to_table_order()

    def _sync_cart_to_table_order(self, *_: Any) -> None:
        """Đồng bộ giỏ hàng vào bộ nhớ bàn và cập nhật trạng thái occupied."""
        if not self._selected_table:
            return

        t_id = self._selected_table.get("id", 0)
        self._table_orders[t_id] = list(self._cart_widget.items)

        # Cập nhật trạng thái bàn sang occupied nếu có món
        new_status = "occupied" if len(self._cart_widget.items) > 0 else "free"
        self._selected_table["status"] = new_status
        for tbl in self._tables:
            if tbl.get("id") == t_id:
                tbl["status"] = new_status
                break

        if t_id in self._table_cards:
            self._table_cards[t_id].update_data(self._selected_table)
        self._cart_widget.set_table(self._selected_table)

    def _handle_cancel_order(self) -> None:
        """Xử lý hủy đơn bàn hiện tại."""
        if not self._selected_table:
            return
        t_id = self._selected_table.get("id", 0)
        self._table_orders[t_id] = []
        self._selected_table["status"] = "free"
        for tbl in self._tables:
            if tbl.get("id") == t_id:
                tbl["status"] = "free"
                break
        if t_id in self._table_cards:
            self._table_cards[t_id].update_data(self._selected_table)
        self._cart_widget.set_table(self._selected_table)

    # ------------------------------------------------------------------
    # Thanh toán (Checkout)
    # ------------------------------------------------------------------
    def _open_checkout_dialog(self) -> None:
        if not self._selected_table or not self._cart_widget.items:
            return

        table_name = self._selected_table.get("name", "Bàn")
        total_amount = self._cart_widget.calculate_total()
        dialog = CheckoutDialog(
            table_name=table_name,
            total_amount=total_amount,
            order_items=self._cart_widget.items,
            parent=self,
        )
        if dialog.exec() == CheckoutDialog.DialogCode.Accepted:
            # Lưu snapshot đơn hàng trước khi làm sạch giỏ
            items_snapshot = [dict(item) for item in self._cart_widget.items]
            payment_method = dialog.payment_method
            received_amount = dialog.received_amount
            change_amount = max(0, received_amount - total_amount)

            # Thanh toán thành công: Dọn sạch đơn, đổi bàn về free
            t_id = self._selected_table.get("id", 0)
            self._table_orders[t_id] = []
            self._selected_table["status"] = "free"
            for tbl in self._tables:
                if tbl.get("id") == t_id:
                    tbl["status"] = "free"
                    break

            if t_id in self._table_cards:
                self._table_cards[t_id].update_data(self._selected_table)

            self._cart_widget.set_table(self._selected_table)
            self._cart_widget.set_items([])

            # Hiển thị phiếu in hoá đơn thanh toán K80
            from datetime import datetime

            invoice_code = f"HD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            receipt_data = {
                "invoice_code": invoice_code,
                "table_name": table_name,
                "cashier_name": self.cashier_name,
                "created_at": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "items": items_snapshot,
                "total_amount": total_amount,
                "payment_method": payment_method,
                "received_amount": received_amount,
                "change_amount": change_amount,
            }
            receipt_dialog = ReceiptDialog(receipt_data, parent=self)
            receipt_dialog.exec()
