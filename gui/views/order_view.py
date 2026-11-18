"""Màn hình Bán hàng / Gọi món tại bàn (OrderView) trong CafeTLU.

Tuân thủ:
- docs/api-contract.md: Endpoint 8 (products), 13 (tables), 14-19 (orders & checkout).
- docs/test-cases.md: TC-ORD-01 đến TC-ORD-03.
- .claude/skills/ui-design/SKILL.md: Ngân sách ngang 1280x720, QFrame#objectName, token theme.
- .claude/skills/pyside6-screen/SKILL.md: 4 trạng thái, HTTP trên luồng nền, phím tắt Ctrl+F/F5.
"""

import logging
import os
from datetime import datetime
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QResizeEvent, QShortcut
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

from gui.api_client import ApiClient, ApiClientError
from gui.i18n import format_currency, t
from gui.theme import COLOR, FONT, RADIUS, SPACE
from gui.views.base import BaseView
from gui.widgets.checkout_dialog import CheckoutDialog
from gui.widgets.order_cart import OrderCartWidget
from gui.widgets.receipt_dialog import ReceiptDialog
from gui.widgets.table_card import TableCardWidget

logger = logging.getLogger(__name__)

# Dữ liệu mẫu dùng khi APP_ENV=demo trước khi API bàn/đơn sẵn sàng
MOCK_TABLES: list[dict[str, Any]] = [
    {"id": i, "name": f"Bàn {i:02d}", "capacity": 4 if i % 3 != 0 else 6, "status": "free"}
    for i in range(1, 13)
]

PRODUCT_PAGE_SIZE = 100

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

    def __init__(
        self,
        api_client: ApiClient,
        parent: QWidget | None = None,
        *,
        use_mock: bool | None = None,
    ) -> None:
        self.api = api_client
        # shortcut: mock bàn/món chỉ bật khi APP_ENV=demo hoặc use_mock=True, bỏ khi #93 xong
        self._use_mock = (
            use_mock if use_mock is not None else os.getenv("APP_ENV", "").strip().lower() == "demo"
        )
        self._tables: list[dict[str, Any]] = []
        self._products: list[dict[str, Any]] = []
        self._filtered_products: list[dict[str, Any]] = []
        self._selected_table: dict[str, Any] | None = None
        self._table_cards: dict[int, TableCardWidget] = {}
        self._table_orders: dict[int, list[dict[str, Any]]] = {}
        self._order_ids: dict[int, int] = {}
        self._item_ids: dict[int, dict[int, int]] = {}
        self._current_cols: int = 1
        self.cashier_name: str = t("role_staff")

        super().__init__(parent)
        self._init_pos_ui()
        self._setup_shortcuts()

    def _init_pos_ui(self) -> None:
        """Khởi tạo bố cục POS 3 cột không tràn ngang ở 1280x720."""
        self._data_layout.setContentsMargins(SPACE["md"], SPACE["md"], SPACE["md"], SPACE["md"])
        self._data_layout.setSpacing(SPACE["md"])

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

        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(SPACE["md"])
        columns_layout.addWidget(self._build_table_panel())
        columns_layout.addWidget(self._build_menu_panel(), stretch=1)
        columns_layout.addWidget(self._build_cart_panel())

        self._data_layout.addLayout(columns_layout, stretch=1)

    def _build_table_panel(self) -> QWidget:
        panel = QFrame(self)
        panel.setObjectName("orderTablePanel")
        panel.setFixedWidth(240)
        panel.setStyleSheet(
            f"QFrame#orderTablePanel {{ background-color: {COLOR['surface']}; "
            f"border: 1px solid {COLOR['border']}; border-radius: {RADIUS['md']}px; }}"
        )
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(SPACE["sm"], SPACE["md"], SPACE["sm"], SPACE["md"])
        layout.setSpacing(SPACE["sm"])

        title = QLabel(t("nav_tables"), panel)
        title.setStyleSheet(
            f"font-size: {FONT['title']}px; font-weight: bold; color: {COLOR['navy']}; "
            f"background: transparent; border: none;"
        )
        layout.addWidget(title)

        self._table_filter_combo = QComboBox(panel)
        self._table_filter_combo.setFixedHeight(32)
        self._table_filter_combo.addItem(t("table_all"), "all")
        self._table_filter_combo.addItem(t("table_filter_free"), "free")
        self._table_filter_combo.addItem(t("table_filter_occupied"), "occupied")
        self._table_filter_combo.currentIndexChanged.connect(self._filter_tables)
        layout.addWidget(self._table_filter_combo)

        scroll = QScrollArea(panel)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

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
        panel.setObjectName("orderMenuPanel")
        panel.setStyleSheet(
            f"QFrame#orderMenuPanel {{ background-color: {COLOR['surface']}; "
            f"border: 1px solid {COLOR['border']}; border-radius: {RADIUS['md']}px; }}"
        )
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(SPACE["md"], SPACE["md"], SPACE["md"], SPACE["md"])
        layout.setSpacing(SPACE["sm"])

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

        self._menu_scroll = QScrollArea(panel)
        self._menu_scroll.setWidgetResizable(True)
        self._menu_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._menu_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self._menu_container = QWidget()
        self._menu_container.setStyleSheet("background: transparent;")
        self._menu_grid = QGridLayout(self._menu_container)
        self._menu_grid.setContentsMargins(0, 0, SPACE["xs"], 0)
        self._menu_grid.setSpacing(SPACE["sm"])

        self._menu_scroll.setWidget(self._menu_container)
        layout.addWidget(self._menu_scroll, stretch=1)

        self._menu_empty_label = QLabel(t("order_no_matching_product"), panel)
        self._menu_empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._menu_empty_label.setStyleSheet(
            f"color: {COLOR['muted']}; font-size: {FONT['body']}px; "
            f"background: transparent; border: none;"
        )
        self._menu_empty_label.setVisible(False)
        layout.addWidget(self._menu_empty_label, stretch=1)
        return panel

    def _build_cart_panel(self) -> QWidget:
        self._cart_widget = OrderCartWidget(self)
        self._cart_widget.setFixedWidth(340)
        self._cart_widget.checkout_requested.connect(self._open_checkout_dialog)
        self._cart_widget.cancel_order_requested.connect(self._handle_cancel_order)
        self._cart_widget.item_quantity_changed.connect(self._on_cart_quantity_changed)
        self._cart_widget.item_removed.connect(self._on_cart_item_removed)
        return self._cart_widget

    def _setup_shortcuts(self) -> None:
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self._focus_search)
        QShortcut(QKeySequence("F1"), self).activated.connect(self._focus_search)
        QShortcut(QKeySequence("F2"), self).activated.connect(self._open_checkout_dialog)
        QShortcut(QKeySequence("F5"), self).activated.connect(self.refresh)

    def _focus_search(self) -> None:
        self._search_input.setFocus()
        self._search_input.selectAll()

    @staticmethod
    def _extract_products(products_res: Any) -> list[dict[str, Any]]:
        """Bóc tách danh sách món từ envelope {'data': [...], 'meta': ...} hoặc list trực tiếp."""
        if isinstance(products_res, dict):
            return list(products_res.get("data") or [])
        if isinstance(products_res, list):
            return list(products_res)
        return []

    def _fetch_all_products(self) -> list[dict[str, Any]]:
        """Tải hết các trang món theo meta phân trang để không bỏ sót món ngoài trang đầu."""
        first_page = self.api.get_products(page=1, page_size=PRODUCT_PAGE_SIZE)
        products = self._extract_products(first_page)
        meta = first_page.get("meta") if isinstance(first_page, dict) else None
        total_pages = int(meta.get("total_pages") or 1) if isinstance(meta, dict) else 1

        for page in range(2, total_pages + 1):
            batch = self._extract_products(
                self.api.get_products(page=page, page_size=PRODUCT_PAGE_SIZE)
            )
            if not batch:
                break
            products.extend(batch)
        return products

    def load(self) -> None:
        """Nạp danh sách bàn và thực đơn món."""
        self._set_state(self.STATE_LOADING)

        def fetch_data() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
            if self._use_mock:
                # shortcut: mock bàn/món khi chưa có API, bỏ khi #93 xong
                try:
                    tables = self.api.get_tables() or MOCK_TABLES
                except Exception as exc:
                    logger.warning("Chế độ demo dùng bàn mẫu (%s)", exc)
                    tables = MOCK_TABLES

                try:
                    products = self._fetch_all_products() or MOCK_PRODUCTS
                except Exception as exc:
                    logger.warning("Chế độ demo dùng thực đơn mẫu (%s)", exc)
                    products = MOCK_PRODUCTS

                return tables, products

            tables = self.api.get_tables() or []
            products = self._fetch_all_products()
            return tables, products

        self.start_worker(fetch_data, on_success=self._on_data_loaded, on_error=self._on_load_error)

    def _on_data_loaded(self, result: tuple[list[dict[str, Any]], list[dict[str, Any]]]) -> None:
        tables, products = result
        self._tables = tables
        self._products = products
        self._order_ids = {
            int(tbl["id"]): int(tbl["open_order_id"])
            for tbl in tables
            if tbl.get("open_order_id") is not None
        }

        if not self._tables and not self._products:
            self._set_state(
                self.STATE_EMPTY,
                message=t("no_data"),
                action_text=t("retry"),
                on_action=self.refresh,
            )
            return

        categories = sorted({p.get("category", "") for p in products if p.get("category")})
        self._category_combo.blockSignals(True)
        self._category_combo.clear()
        self._category_combo.addItem(t("product_all_categories"), "all")
        for cat in categories:
            self._category_combo.addItem(cat, cat)
        self._category_combo.blockSignals(False)

        self._render_tables()
        self._filter_products()

        if not self._selected_table and self._tables:
            self._select_table(self._tables[0])

        self._set_state(self.STATE_DATA)

    def _on_load_error(self, exc: Exception) -> None:
        logger.error("Lỗi khi tải dữ liệu OrderView: %s", exc)
        msg = (
            exc.message if isinstance(exc, ApiClientError) else t("order_connect_error", error=exc)
        )
        self._set_state(self.STATE_ERROR, message=msg)

    def _render_tables(self) -> None:
        while self._table_layout.count() > 1:
            item = self._table_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._table_cards.clear()

        filter_status = self._table_filter_combo.currentData()
        for tbl in self._tables:
            raw_status = tbl.get("status", "free")
            norm_status = "free" if raw_status in ("free", "available") else raw_status
            if filter_status != "all" and norm_status != filter_status:
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

        for cid, card in self._table_cards.items():
            card.set_active(cid == t_id)

        self._cart_widget.set_table(table_data)
        if self._use_mock:
            self._cart_widget.set_items(self._table_orders.get(t_id, []))
            return

        order_id = self._order_ids.get(t_id)
        if order_id is None or table_data.get("status") in ("free", "available"):
            self._order_ids.pop(t_id, None)
            self._cart_widget.set_items([])
            return
        self.start_worker(
            self.api.get_order,
            order_id,
            on_success=self._apply_order,
            on_error=self._on_action_error,
        )

    def _apply_order(self, order: dict[str, Any]) -> None:
        """Đồng bộ giỏ hàng và trạng thái bàn từ đơn do server trả về."""
        table_id = int(order["table_id"])
        self._order_ids[table_id] = int(order["id"])
        self._item_ids[table_id] = {
            int(item["product_id"]): int(item["id"]) for item in order.get("items", [])
        }
        items = [
            {
                "id": item["id"],
                "product_id": item["product_id"],
                "name": item["product_name"],
                "product_name": item["product_name"],
                "price": item["unit_price"],
                "quantity": item["quantity"],
                "note": item.get("notes") or "",
            }
            for item in order.get("items", [])
        ]
        self._table_orders[table_id] = items

        status = "occupied" if order.get("status") in ("pending", "serving") else "free"
        if status == "free":
            self._order_ids.pop(table_id, None)
        for tbl in self._tables:
            if tbl.get("id") == table_id:
                tbl["status"] = status
                if table_id in self._table_cards:
                    self._table_cards[table_id].update_data(tbl)
                break

        if self._selected_table and self._selected_table.get("id") == table_id:
            self._selected_table["status"] = status
            self._cart_widget.set_table(self._selected_table)
            self._cart_widget.set_items(items)

    def _save_added_product(self, table_id: int, product_id: int) -> dict[str, Any]:
        """Tạo đơn nếu bàn chưa có rồi thêm món; luôn để server tính tiền."""
        order_id = self._order_ids.get(table_id)
        if order_id is None:
            order = self.api.create_order(table_id)
            order_id = int(order["id"])
            self._order_ids[table_id] = order_id
        return self.api.add_order_item(order_id, product_id, 1)

    def _on_cart_quantity_changed(self, product_id: int, quantity: int) -> None:
        """Lưu số lượng mới lên server; demo giữ đồng bộ trong bộ nhớ."""
        if self._use_mock:
            self._sync_cart_to_table_order()
            return
        if not self._selected_table:
            return
        table_id = int(self._selected_table.get("id", 0))
        order_id = self._order_ids.get(table_id)
        item_id = self._item_ids.get(table_id, {}).get(product_id)
        if order_id is None or item_id is None:
            return
        note = next(
            (
                str(item.get("note") or "")
                for item in self._cart_widget.items
                if item.get("product_id") == product_id
            ),
            "",
        )
        self.start_worker(
            self.api.update_order_item,
            order_id,
            item_id,
            quantity,
            note,
            on_success=self._apply_order,
            on_error=self._on_action_error,
        )

    def _on_cart_item_removed(self, product_id: int) -> None:
        """Xoá món trên server rồi đọc lại đơn để giỏ hàng khớp dữ liệu thật."""
        if self._use_mock:
            self._sync_cart_to_table_order()
            return
        if not self._selected_table:
            return
        table_id = int(self._selected_table.get("id", 0))
        order_id = self._order_ids.get(table_id)
        item_id = self._item_ids.get(table_id, {}).pop(product_id, None)
        if order_id is None or item_id is None:
            return

        def remove_and_reload() -> dict[str, Any]:
            self.api.remove_order_item(order_id, item_id)
            return self.api.get_order(order_id)

        self.start_worker(
            remove_and_reload,
            on_success=self._apply_order,
            on_error=self._on_action_error,
        )

    def _on_action_error(self, exc: Exception) -> None:
        logger.error("Lỗi thao tác đơn tại bàn: %s", exc)
        message = exc.message if isinstance(exc, ApiClientError) else str(exc)
        QMessageBox.warning(self, t("notice"), message)

    def _menu_column_count(self) -> int:
        return 2 if self._menu_scroll.viewport().width() >= 420 else 1

    def _filter_products(self) -> None:
        query = self._search_input.text().strip().lower()
        cat_filter = self._category_combo.currentData()

        while self._menu_grid.count() > 0:
            item = self._menu_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        filtered = [
            p
            for p in self._products
            if (not query or query in str(p.get("name", "")).lower())
            and (cat_filter == "all" or p.get("category", "") == cat_filter)
        ]

        self._filtered_products = filtered
        has_results = len(filtered) > 0
        self._menu_scroll.setVisible(has_results)
        self._menu_empty_label.setVisible(not has_results)

        cols = self._menu_column_count()
        self._current_cols = cols
        for idx, prod in enumerate(filtered):
            self._menu_grid.addWidget(self._build_product_card(prod), idx // cols, idx % cols)

    def _build_product_card(self, prod: dict[str, Any]) -> QWidget:
        is_avail = bool(prod.get("is_available", True))
        card = QFrame(self._menu_container)
        card.setObjectName("orderProductCard")
        card.setFixedHeight(78)
        card.setStyleSheet(
            f"QFrame#orderProductCard {{ background-color: {COLOR['surface_subtle']}; "
            f"border: 1px solid {COLOR['border']}; border-radius: {RADIUS['sm']}px; }} "
            f"QFrame#orderProductCard:hover {{ border-color: {COLOR['brand_400']}; "
            f"background-color: {COLOR['tint_100']}; }}"
        )
        card.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(SPACE["md"], SPACE["sm"], SPACE["md"], SPACE["sm"])

        info_box = QVBoxLayout()
        info_box.setSpacing(2)

        name_lbl = QLabel(str(prod.get("name", "")), card)
        name_lbl.setStyleSheet(
            f"font-size: {FONT['label']}px; font-weight: bold; color: {COLOR['ink']}; "
            f"background: transparent; border: none;"
        )
        price_lbl = QLabel(format_currency(prod.get("price", 0)), card)
        price_lbl.setStyleSheet(
            f"font-size: {FONT['caption']}px; font-weight: bold; color: {COLOR['navy']}; "
            f"background: transparent; border: none;"
        )
        info_box.addWidget(name_lbl)
        info_box.addWidget(price_lbl)
        layout.addLayout(info_box, stretch=1)

        add_btn = QPushButton(t("order_add_btn") if is_avail else t("product_out_of_stock"), card)
        add_btn.setFixedHeight(28)
        add_btn.setEnabled(is_avail)
        add_btn.setStyleSheet(
            f"QPushButton {{ background-color: {COLOR['navy']}; color: {COLOR['surface']}; "
            f"border-radius: {RADIUS['sm']}px; font-weight: 600; "
            f"min-height: 0px; padding: 0px {SPACE['sm']}px; }} "
            f"QPushButton:hover {{ background-color: {COLOR['navy_600']}; }} "
            f"QPushButton:disabled {{ background-color: {COLOR['border']}; color: {COLOR['muted']}; }}"
        )
        if is_avail:
            add_btn.clicked.connect(lambda _, p=prod: self._add_product_to_cart(p))
        layout.addWidget(add_btn)
        return card

    def _add_product_to_cart(self, product: dict[str, Any]) -> None:
        if not bool(product.get("is_available", True)):
            return
        if not self._selected_table:
            QMessageBox.information(self, t("notice"), t("order_select_table_hint"))
            return
        if self._use_mock:
            self._cart_widget.add_product(product)
            self._sync_cart_to_table_order()
            return

        self.start_worker(
            self._save_added_product,
            int(self._selected_table.get("id", 0)),
            int(product.get("id", 0)),
            on_success=self._apply_order,
            on_error=self._on_action_error,
        )

    def _sync_cart_to_table_order(self, *_: Any) -> None:
        """Đồng bộ giỏ hàng vào bộ nhớ bàn và cập nhật trạng thái occupied."""
        if not self._selected_table:
            return

        t_id = self._selected_table.get("id", 0)
        self._table_orders[t_id] = list(self._cart_widget.items)

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

    def _open_checkout_dialog(self) -> None:
        if not self._selected_table or not self._cart_widget.items:
            return

        table_name = str(
            self._selected_table.get("table_number")
            or self._selected_table.get("name", t("order_cart_table"))
        )
        total_amount = self._cart_widget.calculate_total()
        dialog = CheckoutDialog(
            table_name=table_name,
            total_amount=total_amount,
            order_items=self._cart_widget.items,
            parent=self,
        )
        if dialog.exec() == CheckoutDialog.DialogCode.Accepted:
            items_snapshot = [dict(item) for item in self._cart_widget.items]
            payment_method = dialog.payment_method
            received_amount = dialog.received_amount
            change_amount = max(0, received_amount - total_amount)

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

            # shortcut: tạm sinh invoice_code ở client khi chưa nối API checkout (#94)
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
            ReceiptDialog(receipt_data, parent=self).exec()

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        super().resizeEvent(event)
        new_cols = self._menu_column_count()
        if self._filtered_products and new_cols != self._current_cols:
            self._filter_products()
