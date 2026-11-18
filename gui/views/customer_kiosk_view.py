"""Màn hình Kiosk khách hàng tự chọn món kèm mã QR (CustomerKioskView).

Tuân thủ:
- docs/api-contract.md: Endpoint #24 GET /public/menu, #25 POST /public/orders.
- .claude/skills/ui-design/SKILL.md & pyside6-screen/SKILL.md.
"""

import logging
import os
from typing import Any

from PySide6.QtCore import Signal
from PySide6.QtGui import QKeySequence, QResizeEvent, QShortcut
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QPushButton,
    QWidget,
)

from gui.api_client import ApiClient, ApiClientError
from gui.i18n import t
from gui.theme import COLOR, RADIUS, SPACE
from gui.views.base import BaseView
from gui.widgets.kiosk_cart import (
    KioskCartPanel,
    build_kiosk_header,
    build_kiosk_product_card,
)
from gui.widgets.kiosk_dialogs import (
    CustomerItemOptionDialog,
    OrderSubmittedDialog,
    build_kiosk_menu_section,
    build_kiosk_mock_menu,
    build_kiosk_mock_order,
)
from gui.widgets.order_cart import ConfirmCancelOrderDialog

logger = logging.getLogger(__name__)


class CustomerKioskView(BaseView):
    """Màn hình tự phục vụ cho khách tại quầy: duyệt thực đơn, chọn bàn, gửi đơn và nhận QR."""

    exit_kiosk_requested = Signal()

    def __init__(
        self,
        api_client: ApiClient,
        parent: QWidget | None = None,
        *,
        use_mock: bool | None = None,
    ) -> None:
        self.api = api_client
        # shortcut: mock menu Kiosk khi APP_ENV=demo, mặc định gọi API public thật
        self._use_mock = (
            use_mock if use_mock is not None else os.getenv("APP_ENV", "").strip().lower() == "demo"
        )
        self._categories: list[dict[str, Any]] = []
        self._tables: list[dict[str, Any]] = []
        self._products: list[dict[str, Any]] = []
        self._filtered_products: list[dict[str, Any]] = []
        self._cart_items: list[dict[str, Any]] = []
        self._selected_category: str = "all"
        self._cat_buttons: dict[str, QPushButton] = {}
        self._current_cols: int = 3
        self._is_submitting: bool = False

        super().__init__(parent)
        self._init_kiosk_ui()
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self._focus_search)

    def _init_kiosk_ui(self) -> None:
        self._data_layout.setContentsMargins(0, 0, 0, 0)
        self._data_layout.setSpacing(0)
        header, self._table_combo = build_kiosk_header(
            self,
            on_table_changed=self._on_table_changed,
            on_refresh=self.refresh,
            on_exit=self.exit_kiosk_requested.emit,
        )
        self._data_layout.addWidget(header)

        body = QWidget(self)
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(SPACE["md"], SPACE["md"], SPACE["md"], SPACE["md"])
        body_layout.setSpacing(SPACE["md"])
        menu_ui = build_kiosk_menu_section(
            self,
            on_search_changed=self._apply_filters,
            on_clear_filters=self._reset_filters,
        )
        self._cat_bar_widget = menu_ui["cat_bar_widget"]
        self._cat_bar_layout = menu_ui["cat_bar_layout"]
        self._search_input = menu_ui["search_input"]
        self._clear_filter_btn = menu_ui["clear_filter_btn"]
        self._menu_scroll = menu_ui["menu_scroll"]
        self._menu_container = menu_ui["menu_container"]
        self._menu_grid = menu_ui["menu_grid"]
        self._menu_empty_label = menu_ui["menu_empty_label"]
        body_layout.addWidget(menu_ui["panel"], stretch=1)

        self._cart_panel = KioskCartPanel(self)
        self._cart_panel.qty_changed.connect(self._change_cart_qty)
        self._cart_panel.item_removed.connect(self._remove_cart_item)
        self._cart_panel.clear_requested.connect(self._handle_clear_cart)
        self._cart_panel.submit_requested.connect(self._handle_submit_order)
        body_layout.addWidget(self._cart_panel)

        self._data_layout.addWidget(body, stretch=1)
        self._refresh_cart_ui()

    def _focus_search(self) -> None:
        self._search_input.setFocus()
        self._search_input.selectAll()

    def load(self) -> None:
        """Tải danh sách bàn, danh mục và món ăn qua API public hoặc dữ liệu demo."""
        self._set_state(self.STATE_LOADING)
        if self._use_mock:
            self.start_worker(build_kiosk_mock_menu, self._on_menu_loaded, self._on_load_error)
        else:
            self.start_worker(self.api.get_public_menu, self._on_menu_loaded, self._on_load_error)

    def _on_load_error(self, exc: Exception) -> None:
        logger.error("Lỗi khi tải thực đơn Kiosk: %s", exc)
        msg = exc.message if isinstance(exc, ApiClientError) else t("error_default")
        self._set_state(self.STATE_ERROR, message=msg)

    def _on_menu_loaded(self, payload: Any) -> None:
        if not isinstance(payload, dict):
            self._set_state(self.STATE_ERROR, message=t("error_default"))
            return

        self._categories = list(payload.get("categories") or [])
        self._tables = list(payload.get("tables") or [])
        self._products = list(payload.get("products") or [])
        if not self._products:
            self._set_state(
                self.STATE_EMPTY,
                message=t("kiosk_empty_menu"),
                action_text=t("retry"),
                on_action=self.refresh,
            )
            return

        self._populate_tables()
        self._render_category_chips()
        self._apply_filters()
        self._refresh_cart_ui()
        self._set_state(self.STATE_DATA)

    def _populate_tables(self) -> None:
        prev_id = self._table_combo.currentData()
        self._table_combo.blockSignals(True)
        self._table_combo.clear()

        available = [
            tbl for tbl in self._tables if tbl.get("status", "available") in ("available", "free")
        ]
        for tbl in available:
            num = tbl.get("table_number") or tbl.get("name", "")
            area = tbl.get("area", "")
            cap = tbl.get("seating_capacity") or tbl.get("capacity", 4)
            label = f"{num} ({area} · {cap} chỗ)" if area else f"{num} ({cap} chỗ)"
            self._table_combo.addItem(label, tbl.get("id"))

        if not available:
            self._table_combo.addItem(t("kiosk_no_free_table"), None)
        elif prev_id is not None:
            idx = self._table_combo.findData(prev_id)
            if idx >= 0:
                self._table_combo.setCurrentIndex(idx)

        self._table_combo.blockSignals(False)
        self._on_table_changed()

    def _on_table_changed(self) -> None:
        table_id = self._table_combo.currentData()
        if table_id is None:
            self._cart_panel.table_badge.setText(t("kiosk_select_table"))
        else:
            tbl = next((x for x in self._tables if x.get("id") == table_id), {})
            self._cart_panel.table_badge.setText(
                str(tbl.get("table_number") or tbl.get("name", ""))
            )
        self._refresh_submit_state()

    def _render_category_chips(self) -> None:
        while self._cat_bar_layout.count():
            item = self._cat_bar_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._cat_buttons.clear()

        options = [("all", t("product_all_categories"))] + [
            (str(c["name"]), str(c["name"])) for c in self._categories if c.get("name")
        ]
        for key, text in options:
            btn = QPushButton(text, self._cat_bar_widget)
            btn.setCheckable(True)
            btn.setChecked(key == self._selected_category)
            btn.setStyleSheet(
                f"QPushButton {{ background-color: {COLOR['surface_subtle']}; color: {COLOR['ink']}; "
                f"border: 1px solid {COLOR['border']}; border-radius: {RADIUS['sm']}px; "
                f"padding: {SPACE['xs']}px {SPACE['sm']}px; font-weight: 500; min-height: 0px; }} "
                f"QPushButton:hover {{ background-color: {COLOR['tint_100']}; }} "
                f"QPushButton:checked {{ background-color: {COLOR['navy']}; "
                f"color: {COLOR['surface']}; border-color: {COLOR['navy']}; font-weight: 600; }}"
            )
            btn.clicked.connect(lambda _, k=key: self._select_category(k))
            self._cat_bar_layout.addWidget(btn)
            self._cat_buttons[key] = btn
        self._cat_bar_layout.addStretch()

    def _select_category(self, category_key: str) -> None:
        self._selected_category = category_key
        for key, btn in self._cat_buttons.items():
            btn.setChecked(key == category_key)
        self._apply_filters()

    def _reset_filters(self) -> None:
        self._search_input.clear()
        self._select_category("all")

    def _apply_filters(self) -> None:
        query = self._search_input.text().strip().lower()
        cat = self._selected_category
        self._filtered_products = [
            p
            for p in self._products
            if (not query or query in str(p.get("name", "")).lower())
            and (cat == "all" or p.get("category") == cat)
        ]
        while self._menu_grid.count():
            item = self._menu_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        has_items = len(self._filtered_products) > 0
        self._menu_scroll.setVisible(has_items)
        self._menu_empty_label.setVisible(not has_items)

        cols = 3 if self._menu_scroll.viewport().width() >= 640 else 2
        self._current_cols = cols
        for idx, prod in enumerate(self._filtered_products):
            card = build_kiosk_product_card(
                self._menu_container, prod, on_choose=self._open_option_dialog
            )
            self._menu_grid.addWidget(card, idx // cols, idx % cols)

    def _open_option_dialog(self, product: dict[str, Any]) -> None:
        dialog = CustomerItemOptionDialog(product, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            sel = dialog.get_selection()
            self.add_to_cart(product, quantity=int(sel["quantity"]), notes=str(sel["notes"]))

    def add_to_cart(self, product: dict[str, Any], quantity: int = 1, notes: str = "") -> None:
        """Thêm món vào giỏ hàng; gộp dòng nếu trùng cả product_id và ghi chú."""
        pid = product.get("id")
        for item in self._cart_items:
            if item["product_id"] == pid and item["notes"] == notes:
                item["quantity"] += quantity
                self._refresh_cart_ui()
                return
        self._cart_items.append(
            {
                "product_id": pid,
                "name": str(product.get("name", "")),
                "price": int(product.get("price", 0)),
                "quantity": quantity,
                "notes": notes,
            }
        )
        self._cart_panel.submit_error_banner.setVisible(False)
        self._refresh_cart_ui()

    def _change_cart_qty(self, index: int, delta: int) -> None:
        if 0 <= index < len(self._cart_items):
            new_qty = self._cart_items[index]["quantity"] + delta
            if new_qty <= 0:
                self._cart_items.pop(index)
            else:
                self._cart_items[index]["quantity"] = new_qty
            self._refresh_cart_ui()

    def _remove_cart_item(self, index: int) -> None:
        if 0 <= index < len(self._cart_items):
            self._cart_items.pop(index)
            self._refresh_cart_ui()

    def _refresh_cart_ui(self) -> None:
        self._cart_panel.render_items(self._cart_items)
        self._refresh_submit_state()

    def _refresh_submit_state(self) -> None:
        has_items = len(self._cart_items) > 0
        has_table = self._table_combo.currentData() is not None
        self._cart_panel.clear_btn.setEnabled(has_items and not self._is_submitting)
        self._cart_panel.submit_btn.setEnabled(has_items and has_table and not self._is_submitting)
        if not has_table:
            self._cart_panel.submit_hint_lbl.setText(t("kiosk_submit_hint_no_table"))
        elif not has_items:
            self._cart_panel.submit_hint_lbl.setText(t("kiosk_submit_hint_empty"))
        else:
            self._cart_panel.submit_hint_lbl.setText("")

    def _handle_clear_cart(self) -> None:
        table_name = self._cart_panel.table_badge.text() or t("kiosk_cart_title")
        if (
            ConfirmCancelOrderDialog(table_name=table_name, parent=self).exec()
            == QDialog.DialogCode.Accepted
        ):
            self._cart_items.clear()
            self._cart_panel.order_note_input.clear()
            self._cart_panel.submit_error_banner.setVisible(False)
            self._refresh_cart_ui()

    def _handle_submit_order(self) -> None:
        table_id = self._table_combo.currentData()
        if not self._cart_items or table_id is None or self._is_submitting:
            return

        payload = {
            "table_id": int(table_id),
            "notes": self._cart_panel.order_note_input.text().strip() or None,
            "items": [
                {
                    "product_id": int(item["product_id"]),
                    "quantity": int(item["quantity"]),
                    "notes": item["notes"] or None,
                }
                for item in self._cart_items
            ],
        }
        self._cart_panel.submit_error_banner.setVisible(False)
        self._is_submitting = True
        self._cart_panel.submit_btn.setText(t("kiosk_submitting_btn"))
        self._refresh_submit_state()

        if self._use_mock:
            self.start_worker(
                lambda: build_kiosk_mock_order(payload, self._tables, self._cart_items),
                self._on_submit_success,
                self._on_submit_error,
            )
        else:
            self.start_worker(
                self.api.create_public_order,
                self._on_submit_success,
                self._on_submit_error,
                payload=payload,
            )

    def _on_submit_success(self, order_data: Any) -> None:
        self._is_submitting = False
        self._cart_panel.submit_btn.setText(t("kiosk_submit_btn"))
        self._cart_panel.submit_error_banner.setVisible(False)
        if isinstance(order_data, dict):
            OrderSubmittedDialog(order_data, parent=self).exec()
        self._cart_items.clear()
        self._cart_panel.order_note_input.clear()
        self._refresh_cart_ui()
        self.load()

    def _on_submit_error(self, exc: Exception) -> None:
        self._is_submitting = False
        self._cart_panel.submit_btn.setText(t("kiosk_submit_btn"))
        self._refresh_submit_state()
        msg = exc.message if isinstance(exc, ApiClientError) else t("error_default")
        self._cart_panel.submit_error_banner.setText(msg)
        self._cart_panel.submit_error_banner.setVisible(True)

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        super().resizeEvent(event)
        new_cols = 3 if self._menu_scroll.viewport().width() >= 640 else 2
        if self._filtered_products and new_cols != self._current_cols:
            self._apply_filters()
