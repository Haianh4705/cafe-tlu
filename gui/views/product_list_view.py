"""Màn hình Quản lý Thực đơn (ProductListView) trong CafeTLU.

Tuân thủ:
- docs/api-contract.md: Endpoint 6, 8, 9, 10, 11, 12 (CRUD products + categories).
- docs/test-cases.md: TC-PRD-01 đến TC-PRD-05, TC-SRC-01 đến TC-SRC-03.
- .claude/skills/ui-design/SKILL.md: Spacing 8pt, font Manrope, màu Navy, phân cấp đậm nhạt.
- .claude/skills/pyside6-screen/SKILL.md: 4 trạng thái, HTTP trên luồng nền, phím tắt Ctrl+F/F5.
"""

import logging
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)

from gui.api_client import ApiClient, ApiClientError
from gui.i18n import t
from gui.theme import COLOR, FONT, SPACE
from gui.views.base import BaseView
from gui.widgets.product_dialog import ConfirmDeleteDialog, ProductFormDialog

logger = logging.getLogger(__name__)


def format_currency(amount: int | float) -> str:
    """Định dạng số tiền theo chuẩn VNĐ: 35.000 đ."""
    return f"{int(amount):,} đ".replace(",", ".")


class ProductListView(BaseView):
    """Màn hình danh sách thực đơn và quản lý CRUD món ăn."""

    def __init__(self, api_client: ApiClient, parent: QWidget | None = None) -> None:
        self.api = api_client
        self._categories: list[dict[str, Any]] = []
        self._products: list[dict[str, Any]] = []

        super().__init__(parent)
        self._init_data_ui()
        self._setup_shortcuts()

    def _init_data_ui(self) -> None:
        """Khởi tạo giao diện thanh công cụ và bảng danh sách món."""
        # 1. Header Toolbar
        top_bar = QHBoxLayout()
        top_bar.setSpacing(SPACE["md"])

        title = QLabel(t("nav_products"), self)
        title.setStyleSheet(
            f"color: {COLOR['navy']}; font-size: {FONT['h1']}px; font-weight: bold;"
        )
        top_bar.addWidget(title)
        top_bar.addStretch()

        # Nút Thêm món mới
        self._add_btn = QPushButton("+ " + t("add_new"), self)
        self._add_btn.setFixedHeight(36)
        self._add_btn.clicked.connect(self._open_add_dialog)
        top_bar.addWidget(self._add_btn)

        self._data_layout.addLayout(top_bar)

        # 2. Thanh lọc và tìm kiếm (Filter Bar)
        filter_bar = QHBoxLayout()
        filter_bar.setSpacing(SPACE["sm"])

        # Ô tìm kiếm
        self._search_input = QLineEdit(self)
        self._search_input.setPlaceholderText(t("product_search_placeholder"))
        self._search_input.setFixedHeight(36)
        self._search_input.returnPressed.connect(self.load_products)
        filter_bar.addWidget(self._search_input, stretch=3)

        # Combobox chọn danh mục
        self._cat_combo = QComboBox(self)
        self._cat_combo.setFixedHeight(36)
        self._cat_combo.addItem(t("product_all_categories"), None)
        self._cat_combo.currentIndexChanged.connect(lambda _: self.load_products())
        filter_bar.addWidget(self._cat_combo, stretch=2)

        # Nút tìm kiếm
        search_btn = QPushButton(t("search"), self)
        search_btn.setProperty("variant", "secondary")
        search_btn.setFixedHeight(36)
        search_btn.clicked.connect(self.load_products)
        filter_bar.addWidget(search_btn)

        # Nút làm mới
        refresh_btn = QPushButton(t("refresh"), self)
        refresh_btn.setProperty("variant", "secondary")
        refresh_btn.setFixedHeight(36)
        refresh_btn.clicked.connect(self.refresh)
        filter_bar.addWidget(refresh_btn)

        self._data_layout.addLayout(filter_bar)

        # 3. Bảng dữ liệu (QTableWidget)
        self._table = QTableWidget(self)
        self._table.setColumnCount(6)
        self._table.setHorizontalHeaderLabels(
            [
                "Mã",
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

        # Cấu hình co giãn các cột
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

        # Double-click mở hộp thoại sửa món
        self._table.cellDoubleClicked.connect(self._on_table_double_click)

        self._data_layout.addWidget(self._table)

        # 4. Thanh trạng thái số lượng bản ghi
        self._count_label = QLabel("", self)
        self._count_label.setStyleSheet(f"color: {COLOR['muted']}; font-size: {FONT['caption']}px;")
        self._data_layout.addWidget(self._count_label)

    def _setup_shortcuts(self) -> None:
        """Thiết lập phím tắt Ctrl+F để focus ô tìm kiếm, Delete để xoá món."""
        search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        search_shortcut.activated.connect(self._focus_search)

        delete_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Delete), self)
        delete_shortcut.activated.connect(self._handle_delete_selected)

    def _focus_search(self) -> None:
        self._search_input.setFocus()
        self._search_input.selectAll()

    # ------------------------------------------------------------------
    # Nạp dữ liệu qua API (Luồng nền)
    # ------------------------------------------------------------------
    def load(self) -> None:
        """Nạp dữ liệu ban đầu gồm Danh mục và Danh sách món."""
        self._set_state(self.STATE_LOADING)
        # Nạp danh mục trước, sau đó nạp sản phẩm
        self.start_worker(
            self.api.get_categories,
            on_success=self._on_categories_loaded,
            on_error=self._on_load_error,
        )

    def _on_categories_loaded(self, categories_data: Any) -> None:
        self._categories = categories_data if isinstance(categories_data, list) else []

        # Cập nhật lại dropdown danh mục
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

        # Tiếp tục nạp danh sách sản phẩm
        self.load_products()

    def load_products(self) -> None:
        """Gọi API lấy danh sách món theo từ khoá tìm kiếm và danh mục đã lọc."""
        search_text = self._search_input.text().strip() or None
        category_id = self._cat_combo.currentData()

        self._set_state(self.STATE_LOADING)
        self.start_worker(
            self.api.get_products,
            on_success=self._on_products_loaded,
            on_error=self._on_load_error,
            search=search_text,
            category_id=category_id,
        )

    def _on_products_loaded(self, products_data: Any) -> None:
        self._products = products_data if isinstance(products_data, list) else []

        if not self._products:
            # Chuyển sang trạng thái rỗng (empty)
            search_query = self._search_input.text().strip()
            msg = (
                f"Không tìm thấy món ăn nào khớp với '{search_query}'."
                if search_query
                else t("product_empty")
            )
            self._set_state(
                self.STATE_EMPTY,
                message=msg,
                action_text=t("add_new"),
                on_action=self._open_add_dialog,
            )
            return

        self._render_table()
        self._set_state(self.STATE_DATA)

    def _on_load_error(self, exc: Exception) -> None:
        logger.error("Lỗi khi tải dữ liệu thực đơn: %s", exc)
        msg = (
            exc.message
            if isinstance(exc, ApiClientError)
            else "Không thể nạp dữ liệu thực đơn. Vui lòng thử lại."
        )
        self._set_state(self.STATE_ERROR, message=msg)

    # ------------------------------------------------------------------
    # Hiển thị bảng dữ liệu (Render Data)
    # ------------------------------------------------------------------
    def _render_table(self) -> None:
        """Điền danh sách món vào QTableWidget."""
        self._table.setRowCount(len(self._products))

        for row, prod in enumerate(self._products):
            self._table.setRowHeight(row, 38)

            # Cột 0: ID
            id_item = QTableWidgetItem(f"#{prod.get('id', '')}")
            id_item.setForeground(Qt.GlobalColor.darkGray)
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self._table.setItem(row, 0, id_item)

            # Cột 1: Tên món
            name_item = QTableWidgetItem(str(prod.get("name", "")))
            name_font = name_item.font()
            name_font.setBold(True)
            name_item.setFont(name_font)
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self._table.setItem(row, 1, name_item)

            # Cột 2: Danh mục
            cat_name = prod.get("category") or self._find_category_name(prod.get("category_id"))
            cat_item = QTableWidgetItem(cat_name)
            cat_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self._table.setItem(row, 2, cat_item)

            # Cột 3: Đơn giá
            price = prod.get("price", 0)
            price_item = QTableWidgetItem(format_currency(price))
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self._table.setItem(row, 3, price_item)

            # Cột 4: Đơn vị tính
            unit_item = QTableWidgetItem(str(prod.get("unit", "ly")))
            unit_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self._table.setItem(row, 4, unit_item)

            # Cột 5: Trạng thái còn bán
            is_available = bool(prod.get("is_available", True))
            status_text = t("product_available") if is_available else t("product_out_of_stock")
            status_item = QTableWidgetItem(status_text)
            status_item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
            )
            if is_available:
                status_item.setForeground(Qt.GlobalColor.darkGreen)
            else:
                status_item.setForeground(Qt.GlobalColor.gray)
            self._table.setItem(row, 5, status_item)

        self._count_label.setText(f"Hiển thị {len(self._products)} món")

    def _find_category_name(self, cat_id: int | None) -> str:
        if cat_id is None:
            return "—"
        for cat in self._categories:
            if cat.get("id") == cat_id:
                return str(cat.get("name", "—"))
        return "—"

    # ------------------------------------------------------------------
    # Thao tác CRUD (Thêm, Sửa, Xoá)
    # ------------------------------------------------------------------
    def _open_add_dialog(self) -> None:
        """Mở hộp thoại tạo món mới."""
        dialog = ProductFormDialog(self._categories, parent=self)
        if dialog.exec() == ProductFormDialog.DialogCode.Accepted:
            payload = dialog.get_data()
            self._set_state(self.STATE_LOADING)
            self.start_worker(
                self.api.create_product,
                on_success=lambda _: self.load_products(),
                on_error=self._on_action_error,
                payload=payload,
            )

    def _on_table_double_click(self, row: int, _col: int) -> None:
        """Mở hộp thoại sửa khi người dùng nhấp đúp vào dòng."""
        if 0 <= row < len(self._products):
            product = self._products[row]
            self._open_edit_dialog(product)

    def _open_edit_dialog(self, product: dict[str, Any]) -> None:
        """Mở hộp thoại cập nhật món ăn."""
        dialog = ProductFormDialog(self._categories, product=product, parent=self)
        if dialog.exec() == ProductFormDialog.DialogCode.Accepted:
            payload = dialog.get_data()
            prod_id = product.get("id")
            if prod_id is not None:
                self._set_state(self.STATE_LOADING)
                self.start_worker(
                    self.api.update_product,
                    on_success=lambda _: self.load_products(),
                    on_error=self._on_action_error,
                    product_id=prod_id,
                    payload=payload,
                )

    def _handle_delete_selected(self) -> None:
        """Xử lý xoá món đang chọn trong bảng."""
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
        logger.error("Lỗi khi thực hiện thao tác món ăn: %s", exc)
        self.load_products()
