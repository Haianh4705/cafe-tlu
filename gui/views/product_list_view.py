"""Màn hình Quản lý Thực đơn (ProductListView) trong CafeTLU.

Tuân thủ:
- docs/api-contract.md: Endpoint 6, 8, 9, 10, 11, 12 (CRUD products + categories).
- docs/test-cases.md: TC-PRD-01 đến TC-PRD-05, TC-SRC-01 đến TC-SRC-03.
- .claude/skills/ui-design/SKILL.md: Spacing 8pt, font Manrope, màu từ gui/theme.py.
- .claude/skills/pyside6-screen/SKILL.md: 4 trạng thái, giữ bộ lọc khi rỗng, giữ form khi lỗi.
"""

import logging
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)

from gui.api_client import ApiClient, ApiClientError
from gui.i18n import format_currency, t
from gui.theme import COLOR, FONT, SPACE
from gui.views.base import BaseView
from gui.widgets.product_dialog import ConfirmDeleteDialog, ProductFormDialog

logger = logging.getLogger(__name__)


class ProductListView(BaseView):
    """Màn hình danh sách thực đơn và quản lý CRUD món ăn."""

    def __init__(self, api_client: ApiClient, parent: QWidget | None = None) -> None:
        self.api = api_client
        self._categories: list[dict[str, Any]] = []
        self._products: list[dict[str, Any]] = []
        self._user_role: str = "staff"
        self._page: int = 1
        self._page_size: int = 20
        self._total_pages: int = 1
        self._total_count: int = 0

        super().__init__(parent)
        self._init_data_ui()
        self._setup_shortcuts()

    def set_user_role(self, role: str) -> None:
        """Cập nhật vai trò người dùng (admin, staff, barista) để phân quyền."""
        self._user_role = role
        if hasattr(self, "_add_btn"):
            self._add_btn.setVisible(self.is_admin)

    @property
    def is_admin(self) -> bool:
        """Kiểm tra người dùng hiện tại có vai trò admin hay không."""
        return self._user_role == "admin"

    def _init_data_ui(self) -> None:
        """Khởi tạo giao diện thanh công cụ và bảng danh sách món."""
        top_bar = QHBoxLayout()
        top_bar.setSpacing(SPACE["md"])

        title = QLabel(t("nav_products"), self)
        title.setStyleSheet(
            f"color: {COLOR['navy']}; font-size: {FONT['h1']}px; font-weight: bold;"
        )
        top_bar.addWidget(title)
        top_bar.addStretch()

        self._add_btn = QPushButton("+ " + t("add_new"), self)
        self._add_btn.setFixedHeight(36)
        self._add_btn.clicked.connect(self._open_add_dialog)
        top_bar.addWidget(self._add_btn)
        self._data_layout.addLayout(top_bar)

        filter_bar = QHBoxLayout()
        filter_bar.setSpacing(SPACE["sm"])

        self._search_input = QLineEdit(self)
        self._search_input.setPlaceholderText(t("product_search_placeholder"))
        self._search_input.setFixedHeight(36)
        self._search_input.returnPressed.connect(lambda: self.load_products(reset_page=True))
        filter_bar.addWidget(self._search_input, stretch=3)

        self._cat_combo = QComboBox(self)
        self._cat_combo.setFixedHeight(36)
        self._cat_combo.addItem(t("product_all_categories"), None)
        self._cat_combo.currentIndexChanged.connect(lambda _: self.load_products(reset_page=True))
        filter_bar.addWidget(self._cat_combo, stretch=2)

        search_btn = QPushButton(t("search"), self)
        search_btn.setProperty("variant", "secondary")
        search_btn.setFixedHeight(36)
        search_btn.clicked.connect(lambda: self.load_products(reset_page=True))
        filter_bar.addWidget(search_btn)

        refresh_btn = QPushButton(t("refresh"), self)
        refresh_btn.setProperty("variant", "secondary")
        refresh_btn.setFixedHeight(36)
        refresh_btn.clicked.connect(self.refresh)
        filter_bar.addWidget(refresh_btn)

        self._data_layout.addLayout(filter_bar)

        self._table = QTableWidget(self)
        self._table.setColumnCount(6)
        self._table.setHorizontalHeaderLabels(
            [
                t("product_col_id"),
                t("product_name"),
                t("product_category"),
                t("product_price"),
                t("product_unit"),
                t("product_status"),
            ]
        )
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)
        self._table.setShowGrid(False)

        header = self._table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

        self._table.cellDoubleClicked.connect(self._on_table_double_click)
        self._data_layout.addWidget(self._table)

        pagination_bar = QHBoxLayout()
        pagination_bar.setSpacing(SPACE["sm"])

        self._count_label = QLabel("", self)
        self._count_label.setStyleSheet(f"color: {COLOR['muted']}; font-size: {FONT['caption']}px;")
        pagination_bar.addWidget(self._count_label)
        pagination_bar.addStretch()

        self._prev_page_btn = QPushButton(t("product_prev_page"), self)
        self._prev_page_btn.setProperty("variant", "secondary")
        self._prev_page_btn.setFixedHeight(30)
        self._prev_page_btn.clicked.connect(self._go_prev_page)
        pagination_bar.addWidget(self._prev_page_btn)

        self._page_label = QLabel("Trang 1 / 1", self)
        self._page_label.setStyleSheet(f"font-size: {FONT['caption']}px; font-weight: 600;")
        pagination_bar.addWidget(self._page_label)

        self._next_page_btn = QPushButton(t("product_next_page"), self)
        self._next_page_btn.setProperty("variant", "secondary")
        self._next_page_btn.setFixedHeight(30)
        self._next_page_btn.clicked.connect(self._go_next_page)
        pagination_bar.addWidget(self._next_page_btn)

        self._data_layout.addLayout(pagination_bar)

    def _go_prev_page(self) -> None:
        if self._page > 1:
            self._page -= 1
            self.load_products()

    def _go_next_page(self) -> None:
        if self._page < self._total_pages:
            self._page += 1
            self.load_products()

    def _clear_filters(self) -> None:
        self._search_input.clear()
        self._cat_combo.blockSignals(True)
        self._cat_combo.setCurrentIndex(0)
        self._cat_combo.blockSignals(False)
        self.load_products(reset_page=True)

    def _setup_shortcuts(self) -> None:
        """Thiết lập phím tắt Ctrl+F để focus ô tìm kiếm, Delete để xoá món."""
        search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        search_shortcut.activated.connect(self._focus_search)

        delete_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Delete), self)
        delete_shortcut.activated.connect(self._handle_delete_selected)

    def _focus_search(self) -> None:
        self._search_input.setFocus()
        self._search_input.selectAll()

    def load(self) -> None:
        """Nạp dữ liệu ban đầu gồm Danh mục và Danh sách món."""
        self._set_state(self.STATE_LOADING)
        self.start_worker(
            self.api.get_categories,
            on_success=self._on_categories_loaded,
            on_error=self._on_load_error,
        )

    def _on_categories_loaded(self, categories_data: Any) -> None:
        self._categories = categories_data if isinstance(categories_data, list) else []

        current_id = self._cat_combo.currentData()
        self._cat_combo.blockSignals(True)
        self._cat_combo.clear()
        self._cat_combo.addItem(t("product_all_categories"), None)
        for cat in self._categories:
            self._cat_combo.addItem(cat.get("name", ""), cat.get("id"))

        if current_id is not None:
            idx = self._cat_combo.findData(current_id)
            if idx >= 0:
                self._cat_combo.setCurrentIndex(idx)
        self._cat_combo.blockSignals(False)

        self.load_products()

    def load_products(self, reset_page: bool = False) -> None:
        """Gọi API lấy danh sách món theo từ khoá tìm kiếm, danh mục và trang hiện tại."""
        if reset_page:
            self._page = 1
        search_text = self._search_input.text().strip() or None
        category_id = self._cat_combo.currentData()

        self._set_state(self.STATE_LOADING)
        self.start_worker(
            self.api.get_products,
            on_success=self._on_products_loaded,
            on_error=self._on_load_error,
            search=search_text,
            category_id=category_id,
            page=self._page,
            page_size=self._page_size,
        )

    def _on_products_loaded(self, products_data: Any) -> None:
        if isinstance(products_data, dict):
            self._products = products_data.get("data") or []
            meta = products_data.get("meta") or {}
            self._total_pages = max(1, int(meta.get("total_pages", 1) or 1))
            self._total_count = int(meta.get("total", len(self._products)) or 0)
            self._page = int(meta.get("page", self._page) or 1)
        elif isinstance(products_data, list):
            self._products = products_data
            self._total_count = len(products_data)
            self._total_pages = max(1, (self._total_count + self._page_size - 1) // self._page_size)
        else:
            self._products = []
            self._total_count = 0
            self._total_pages = 1

        if not self._products and self._page > 1 and self._total_count > 0:
            self._page = min(self._page - 1, self._total_pages)
            self.load_products()
            return

        if not self._products:
            search_query = self._search_input.text().strip()
            has_filter = bool(search_query or self._cat_combo.currentData() is not None)
            if search_query:
                msg = t("product_search_empty", query=search_query)
            elif has_filter:
                msg = t("order_no_matching_product")
            else:
                msg = t("product_empty")

            if has_filter:
                action_text = t("product_clear_filter")
                on_action = self._clear_filters
            elif self.is_admin:
                action_text = t("add_new")
                on_action = self._open_add_dialog
            else:
                action_text = None
                on_action = None

            self._set_state(
                self.STATE_EMPTY,
                message=msg,
                action_text=action_text,
                on_action=on_action,
            )
            return

        self._render_table()
        self._set_state(self.STATE_DATA)

    def _on_load_error(self, exc: Exception) -> None:
        logger.error("Lỗi khi tải dữ liệu thực đơn: %s", exc)
        msg = exc.message if isinstance(exc, ApiClientError) else t("product_load_error")
        self._set_state(self.STATE_ERROR, message=msg)

    def _render_table(self) -> None:
        """Điền danh sách món vào QTableWidget."""
        self._table.setRowCount(len(self._products))

        for row, prod in enumerate(self._products):
            self._table.setRowHeight(row, 38)

            id_item = QTableWidgetItem(f"#{prod.get('id', '')}")
            id_item.setForeground(QColor(COLOR["muted"]))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self._table.setItem(row, 0, id_item)

            name_item = QTableWidgetItem(str(prod.get("name", "")))
            name_font = name_item.font()
            name_font.setBold(True)
            name_item.setFont(name_font)
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self._table.setItem(row, 1, name_item)

            cat_name = prod.get("category") or self._find_category_name(prod.get("category_id"))
            cat_item = QTableWidgetItem(cat_name)
            cat_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self._table.setItem(row, 2, cat_item)

            price = prod.get("price", 0)
            price_item = QTableWidgetItem(format_currency(price))
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self._table.setItem(row, 3, price_item)

            unit_item = QTableWidgetItem(str(prod.get("unit", "ly")))
            unit_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self._table.setItem(row, 4, unit_item)

            is_available = bool(prod.get("is_available", True))
            status_text = t("product_available") if is_available else t("product_out_of_stock")
            status_item = QTableWidgetItem(status_text)
            status_item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
            )
            status_item.setForeground(QColor(COLOR["success"] if is_available else COLOR["muted"]))
            self._table.setItem(row, 5, status_item)

        self._count_label.setText(
            t("product_count_status", shown=len(self._products), total=self._total_count)
        )
        self._page_label.setText(
            t("product_page_status", page=self._page, total_pages=self._total_pages)
        )
        self._prev_page_btn.setEnabled(self._page > 1)
        self._next_page_btn.setEnabled(self._page < self._total_pages)

    def _find_category_name(self, cat_id: int | None) -> str:
        if cat_id is None:
            return "—"
        for cat in self._categories:
            if cat.get("id") == cat_id:
                return str(cat.get("name", "—"))
        return "—"

    def _open_add_dialog(self) -> None:
        """Mở hộp thoại tạo món mới, giữ form khi API lỗi."""
        if not self.is_admin:
            QMessageBox.warning(
                self,
                t("product_no_permission_title"),
                t("product_no_permission_add"),
            )
            return

        dialog: ProductFormDialog

        def submit(payload: dict[str, Any]) -> None:
            dialog.set_submitting(True)
            self.start_worker(
                self.api.create_product,
                on_success=lambda _: (dialog.accept(), self.load_products()),
                on_error=lambda exc: self._on_dialog_error(dialog, exc),
                payload=payload,
            )

        dialog = ProductFormDialog(self._categories, parent=self, on_submit=submit)
        dialog.exec()

    def _on_table_double_click(self, row: int, _col: int) -> None:
        """Mở hộp thoại sửa khi người dùng nhấp đúp vào dòng."""
        if not self.is_admin:
            QMessageBox.warning(
                self,
                t("product_no_permission_title"),
                t("product_no_permission_edit"),
            )
            return

        if 0 <= row < len(self._products):
            self._open_edit_dialog(self._products[row])

    def _open_edit_dialog(self, product: dict[str, Any]) -> None:
        """Mở hộp thoại cập nhật món ăn, giữ form khi API lỗi."""
        if not self.is_admin:
            QMessageBox.warning(
                self,
                t("product_no_permission_title"),
                t("product_no_permission_edit"),
            )
            return

        prod_id = product.get("id")
        if prod_id is None:
            return

        dialog: ProductFormDialog

        def submit(payload: dict[str, Any]) -> None:
            dialog.set_submitting(True)
            self.start_worker(
                self.api.update_product,
                on_success=lambda _: (dialog.accept(), self.load_products()),
                on_error=lambda exc: self._on_dialog_error(dialog, exc),
                product_id=prod_id,
                payload=payload,
            )

        dialog = ProductFormDialog(self._categories, product=product, parent=self, on_submit=submit)
        dialog.exec()

    def _on_dialog_error(self, dialog: ProductFormDialog, exc: Exception) -> None:
        logger.error("Lỗi khi lưu món ăn: %s", exc)
        msg = exc.message if isinstance(exc, ApiClientError) else t("error_default")
        dialog.show_error(msg)

    def _handle_delete_selected(self) -> None:
        """Xử lý xoá món đang chọn trong bảng."""
        if not self.is_admin:
            QMessageBox.warning(
                self,
                t("product_no_permission_title"),
                t("product_no_permission_delete"),
            )
            return

        selected_row = self._table.currentRow()
        if 0 <= selected_row < len(self._products):
            product = self._products[selected_row]
            dialog = ConfirmDeleteDialog(str(product.get("name", "")), parent=self)
            if dialog.exec() == ConfirmDeleteDialog.DialogCode.Accepted:
                prod_id = product.get("id")
                if prod_id is not None:
                    self._set_state(self.STATE_LOADING)
                    self.start_worker(
                        self.api.delete_product,
                        on_success=lambda _: self.load_products(),
                        on_error=self._on_action_error,
                        product_id=prod_id,
                    )

    def _on_action_error(self, exc: Exception) -> None:
        logger.error("Lỗi khi xoá món ăn: %s", exc)
        msg = exc.message if isinstance(exc, ApiClientError) else t("product_delete_error")
        self._set_state(self.STATE_ERROR, message=msg)
