"""Widget Giỏ hàng / Hoá đơn tạm tính tại bàn (OrderCartWidget) trong CafeTLU.

Tuân thủ:
- docs/api-contract.md: Endpoint 14-19 (Order lifecycle & checkout).
- docs/test-cases.md: TC-ORD-01, TC-ORD-02, TC-ORD-03.
- .claude/skills/ui-design/SKILL.md: Phân cấp thông tin, bảng gọn gàng, nút bấm rõ ràng.
"""

from decimal import Decimal
from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from gui.i18n import format_currency, t
from gui.theme import COLOR, FONT, RADIUS, SPACE


class ConfirmCancelOrderDialog(QDialog):
    """Hộp thoại xác nhận huỷ toàn bộ đơn hàng của bàn với nút thao tác rõ ràng."""

    def __init__(self, table_name: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(t("order_confirm_cancel_title"))
        self.setFixedWidth(440)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE["lg"], SPACE["lg"], SPACE["lg"], SPACE["lg"])
        layout.setSpacing(SPACE["md"])

        title = QLabel(t("order_confirm_cancel", table_name=table_name), self)
        title.setWordWrap(True)
        title.setStyleSheet(
            f"color: {COLOR['ink']}; font-size: {FONT['title']}px; font-weight: bold;"
        )

        warning = QLabel(t("order_confirm_cancel_warning"), self)
        warning.setWordWrap(True)
        warning.setStyleSheet(
            f"color: {COLOR['muted']}; font-size: {FONT['body']}px; line-height: 1.4;"
        )

        layout.addWidget(title)
        layout.addWidget(warning)
        layout.addSpacing(SPACE["sm"])

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(SPACE["md"])

        self.skip_btn = QPushButton(t("skip"), self)
        self.skip_btn.setProperty("variant", "secondary")
        self.skip_btn.setStyleSheet(
            f"QPushButton {{ background-color: {COLOR['surface']}; color: {COLOR['navy']}; "
            f"border: 1.5px solid {COLOR['navy']}; border-radius: {RADIUS['sm']}px; "
            f"font-weight: bold; font-size: {FONT['body']}px; "
            f"padding: {SPACE['sm']}px {SPACE['md']}px; min-height: 22px; }} "
            f"QPushButton:hover {{ background-color: {COLOR['tint_100']}; }}"
        )
        self.skip_btn.clicked.connect(self.reject)

        self.confirm_btn = QPushButton(t("order_confirm_cancel_btn"), self)
        self.confirm_btn.setProperty("variant", "danger")
        self.confirm_btn.setStyleSheet(
            f"QPushButton {{ background-color: {COLOR['red']}; color: {COLOR['surface']}; "
            f"border: none; border-radius: {RADIUS['sm']}px; "
            f"font-weight: bold; font-size: {FONT['body']}px; "
            f"padding: {SPACE['sm']}px {SPACE['md']}px; min-height: 22px; }} "
            f"QPushButton:hover {{ background-color: {COLOR['red_text']}; }}"
        )
        self.confirm_btn.clicked.connect(self.accept)

        btn_layout.addStretch()
        btn_layout.addWidget(self.skip_btn)
        btn_layout.addWidget(self.confirm_btn)
        layout.addLayout(btn_layout)


class OrderCartWidget(QFrame):
    """Widget quản lý danh sách món đã gọi, cập nhật số lượng và chuẩn bị thanh toán."""

    item_quantity_changed = Signal(int, int)  # product_id, new_quantity
    item_removed = Signal(int)  # product_id
    checkout_requested = Signal()
    save_requested = Signal()
    cancel_order_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.table_data: dict[str, Any] | None = None
        self.items: list[dict[str, Any]] = []

        self.setStyleSheet(
            f"OrderCartWidget {{ background-color: {COLOR['surface']}; "
            f"border: 1px solid {COLOR['border']}; border-radius: {RADIUS['md']}px; }}"
        )
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE["md"], SPACE["md"], SPACE["md"], SPACE["md"])
        layout.setSpacing(SPACE["sm"])

        # 1. Header: Tên bàn + Trạng thái
        header_layout = QHBoxLayout()
        self._table_title_lbl = QLabel(t("order_cart_title"), self)
        self._table_title_lbl.setStyleSheet(
            f"font-size: {FONT['title']}px; font-weight: bold; color: {COLOR['navy']}; background: transparent;"
        )
        header_layout.addWidget(self._table_title_lbl)
        header_layout.addStretch()

        self._status_badge = QLabel("", self)
        self._status_badge.setStyleSheet(
            f"font-size: {FONT['caption']}px; font-weight: 600; padding: 2px 8px; "
            f"border-radius: {RADIUS['sm']}px; background: transparent;"
        )
        header_layout.addWidget(self._status_badge)
        layout.addLayout(header_layout)

        # 2. Bảng danh sách món
        self._items_table = QTableWidget(self)
        self._items_table.setColumnCount(4)
        self._items_table.setHorizontalHeaderLabels(
            [t("order_item_name"), t("order_item_qty"), t("order_item_price"), ""]
        )
        self._items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._items_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self._items_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self._items_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self._items_table.setColumnWidth(1, 80)
        self._items_table.setColumnWidth(2, 90)
        self._items_table.setColumnWidth(3, 30)
        self._items_table.verticalHeader().setVisible(False)
        self._items_table.verticalHeader().setDefaultSectionSize(36)
        self._items_table.setAlternatingRowColors(True)
        self._items_table.setStyleSheet(
            f"QTableWidget {{ border: 1px solid {COLOR['border']}; "
            f"border-radius: {RADIUS['sm']}px; background-color: {COLOR['surface']}; "
            f"alternate-background-color: {COLOR['surface_subtle']}; }}"
            f"QHeaderView::section {{ background-color: {COLOR['surface_subtle']}; "
            f"font-weight: bold; border: none; border-bottom: 1px solid {COLOR['border']}; "
            f"padding: 6px; }}"
        )
        layout.addWidget(self._items_table, stretch=1)

        # Thông báo rỗng khi chưa có món
        self._empty_cart_lbl = QLabel(t("order_empty_cart"), self)
        self._empty_cart_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_cart_lbl.setStyleSheet(
            f"color: {COLOR['muted']}; font-size: {FONT['body']}px; padding: {SPACE['lg']}px;"
        )
        layout.addWidget(self._empty_cart_lbl)

        # 3. Khối tổng thanh toán
        summary_frame = QFrame(self)
        summary_frame.setStyleSheet(
            f"background-color: {COLOR['surface_subtle']}; border: 1px solid {COLOR['border']}; "
            f"border-radius: {RADIUS['sm']}px; padding: {SPACE['xs']}px;"
        )
        summary_layout = QVBoxLayout(summary_frame)
        summary_layout.setContentsMargins(SPACE["sm"], SPACE["sm"], SPACE["sm"], SPACE["sm"])
        summary_layout.setSpacing(SPACE["xs"])

        # Tạm tính
        subtotal_row = QHBoxLayout()
        subtotal_lbl = QLabel(t("order_subtotal") + ":", summary_frame)
        subtotal_lbl.setStyleSheet(f"color: {COLOR['muted']}; font-size: {FONT['caption']}px;")
        self._subtotal_val_lbl = QLabel("0 đ", summary_frame)
        self._subtotal_val_lbl.setStyleSheet(f"font-size: {FONT['caption']}px; font-weight: 600;")
        subtotal_row.addWidget(subtotal_lbl)
        subtotal_row.addStretch()
        subtotal_row.addWidget(self._subtotal_val_lbl)
        summary_layout.addLayout(subtotal_row)

        # Tổng cộng
        total_row = QHBoxLayout()
        total_lbl = QLabel(t("order_total") + ":", summary_frame)
        total_lbl.setStyleSheet(
            f"font-size: {FONT['body']}px; font-weight: bold; color: {COLOR['navy']};"
        )
        self._total_val_lbl = QLabel("0 đ", summary_frame)
        self._total_val_lbl.setStyleSheet(
            f"font-size: {FONT['title']}px; font-weight: bold; color: {COLOR['navy']};"
        )
        total_row.addWidget(total_lbl)
        total_row.addStretch()
        total_row.addWidget(self._total_val_lbl)
        summary_layout.addLayout(total_row)

        layout.addWidget(summary_frame)

        # 4. Các nút thao tác
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(SPACE["sm"])

        self._cancel_btn = QPushButton(t("order_btn_cancel"), self)
        self._cancel_btn.setProperty("variant", "danger")
        self._cancel_btn.setFixedHeight(38)
        self._cancel_btn.setStyleSheet(
            f"QPushButton {{ background-color: transparent; color: {COLOR['red_text']}; "
            f"border: 1px solid {COLOR['red']}; border-radius: {RADIUS['sm']}px; font-weight: 600; padding: 0 12px; }} "
            f"QPushButton:hover {{ background-color: #FEE2E2; }}"
        )
        self._cancel_btn.clicked.connect(self._handle_cancel_clicked)
        actions_layout.addWidget(self._cancel_btn, stretch=1)

        self._checkout_btn = QPushButton(t("order_btn_checkout"), self)
        self._checkout_btn.setFixedHeight(38)
        self._checkout_btn.setStyleSheet(
            f"QPushButton {{ background-color: {COLOR['navy']}; color: {COLOR['surface']}; "
            f"border: none; border-radius: {RADIUS['sm']}px; font-weight: 600; padding: 0 12px; }} "
            f"QPushButton:hover {{ background-color: {COLOR['navy_600']}; }} "
            f"QPushButton:disabled {{ background-color: #E7E5E4; color: {COLOR['muted']}; }}"
        )
        self._checkout_btn.clicked.connect(self.checkout_requested.emit)
        actions_layout.addWidget(self._checkout_btn, stretch=2)

        layout.addLayout(actions_layout)

        self._update_ui_state()

    def set_table(self, table_data: dict[str, Any] | None) -> None:
        """Đặt bàn đang làm việc."""
        self.table_data = table_data
        if not table_data:
            self._table_title_lbl.setText(t("order_cart_title"))
            self._status_badge.setVisible(False)
            self.set_items([])
            return

        table_name = table_data.get("name", "Bàn")
        self._table_title_lbl.setText(f"{t('order_cart_title')} — {table_name}")

        status = table_data.get("status", "free")
        self._status_badge.setVisible(True)
        if status == "occupied":
            self._status_badge.setText(t("table_occupied"))
            self._status_badge.setStyleSheet(
                f"background-color: {COLOR['tint_200']}; color: {COLOR['navy']}; "
                f"border-radius: {RADIUS['sm']}px; padding: 2px 6px; font-weight: bold;"
            )
        else:
            self._status_badge.setText(t("table_free"))
            self._status_badge.setStyleSheet(
                f"background-color: #D1FAE5; color: {COLOR['success']}; "
                f"border-radius: {RADIUS['sm']}px; padding: 2px 6px; font-weight: bold;"
            )

    def set_items(self, items: list[dict[str, Any]]) -> None:
        """Nạp danh sách món trong đơn hàng."""
        self.items = list(items)
        self._render_items()

    def add_product(self, product: dict[str, Any]) -> None:
        """Thêm 1 món vào đơn hàng hiện tại hoặc tăng số lượng nếu đã có."""
        p_id = product.get("id")
        for it in self.items:
            if it.get("product_id") == p_id or it.get("id") == p_id:
                it["quantity"] = it.get("quantity", 1) + 1
                self._render_items()
                self.item_quantity_changed.emit(p_id, it["quantity"])
                return

        new_item = {
            "product_id": p_id,
            "product_name": product.get("name", "Món"),
            "price": product.get("price", 0),
            "quantity": 1,
            "note": "",
        }
        self.items.append(new_item)
        self._render_items()
        self.item_quantity_changed.emit(p_id, 1)

    @staticmethod
    def _to_vnd(value: Any) -> int:
        """Chuyển đổi giá tiền (int/float/Decimal/str) sang số nguyên VNĐ."""
        if isinstance(value, int) and not isinstance(value, bool):
            return value
        if value in (None, ""):
            return 0
        return int(Decimal(str(value)))

    def calculate_total(self) -> int:
        """Tính tổng tiền toàn bộ các món trong đơn (số nguyên VNĐ)."""
        return sum(
            self._to_vnd(it.get("price", 0)) * int(it.get("quantity", 1)) for it in self.items
        )

    def _render_items(self) -> None:
        total = self.calculate_total()
        self._subtotal_val_lbl.setText(format_currency(total))
        self._total_val_lbl.setText(format_currency(total))

        self._items_table.clearContents()
        self._items_table.setRowCount(len(self.items))
        for row, it in enumerate(self.items):
            p_id = it.get("product_id") or it.get("id", 0)
            name = it.get("product_name") or it.get("name", "Món")
            qty = int(it.get("quantity", 1))
            price = self._to_vnd(it.get("price", 0))
            line_total = price * qty

            # Cột 1: Tên món
            name_item = QTableWidgetItem(name)
            name_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self._items_table.setItem(row, 0, name_item)

            # Cột 2: Nút - SL +
            qty_widget = QWidget()
            qty_layout = QHBoxLayout(qty_widget)
            qty_layout.setContentsMargins(0, 0, 0, 0)
            qty_layout.setSpacing(2)

            minus_btn = QPushButton("-", qty_widget)
            minus_btn.setFixedSize(22, 22)
            minus_btn.setStyleSheet(
                f"QPushButton {{ background-color: {COLOR['surface_subtle']}; color: {COLOR['ink']}; "
                f"border: 1px solid {COLOR['border']}; border-radius: {RADIUS['sm']}px; "
                f"font-weight: bold; min-height: 0px; padding: 0px; }} "
                f"QPushButton:hover {{ background-color: {COLOR['tint_100']}; }}"
            )
            minus_btn.clicked.connect(lambda _, pid=p_id: self._change_qty(pid, -1))

            qty_lbl = QLabel(str(qty), qty_widget)
            qty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            qty_lbl.setFixedWidth(24)

            plus_btn = QPushButton("+", qty_widget)
            plus_btn.setFixedSize(22, 22)
            plus_btn.setStyleSheet(
                f"QPushButton {{ background-color: {COLOR['surface_subtle']}; color: {COLOR['ink']}; "
                f"border: 1px solid {COLOR['border']}; border-radius: {RADIUS['sm']}px; "
                f"font-weight: bold; min-height: 0px; padding: 0px; }} "
                f"QPushButton:hover {{ background-color: {COLOR['tint_100']}; }}"
            )
            plus_btn.clicked.connect(lambda _, pid=p_id: self._change_qty(pid, 1))

            qty_layout.addWidget(minus_btn)
            qty_layout.addWidget(qty_lbl)
            qty_layout.addWidget(plus_btn)
            self._items_table.setCellWidget(row, 1, qty_widget)

            # Cột 3: Thành tiền
            total_item = QTableWidgetItem(format_currency(line_total))
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            total_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self._items_table.setItem(row, 2, total_item)

            # Cột 4: Nút Xoá
            del_btn = QPushButton("X")
            del_btn.setFixedSize(22, 22)
            del_btn.setStyleSheet(
                f"QPushButton {{ background-color: transparent; color: {COLOR['red_text']}; "
                f"border: none; font-weight: bold; font-size: 13px; min-height: 0px; padding: 0px; }} "
                f"QPushButton:hover {{ color: {COLOR['red']}; background-color: #FEE2E2; border-radius: 3px; }}"
            )
            del_btn.clicked.connect(lambda _, pid=p_id: self._remove_item(pid))
            self._items_table.setCellWidget(row, 3, del_btn)

        self._update_ui_state()

    def _change_qty(self, product_id: int, delta: int) -> None:
        for it in self.items:
            if (it.get("product_id") == product_id) or (it.get("id") == product_id):
                new_q = it.get("quantity", 1) + delta
                if new_q <= 0:
                    self._remove_item(product_id)
                else:
                    it["quantity"] = new_q
                    self._render_items()
                    self.item_quantity_changed.emit(product_id, new_q)
                return

    def _remove_item(self, product_id: int) -> None:
        self.items = [
            it
            for it in self.items
            if (it.get("product_id") != product_id and it.get("id") != product_id)
        ]
        self._render_items()
        self.item_removed.emit(product_id)

    def _update_ui_state(self) -> None:
        has_items = len(self.items) > 0
        has_table = self.table_data is not None

        self._items_table.setVisible(has_items)
        self._empty_cart_lbl.setVisible(not has_items)
        self._checkout_btn.setEnabled(has_items and has_table)
        self._cancel_btn.setEnabled(has_items and has_table)

        if not has_table:
            self._empty_cart_lbl.setText(t("order_select_table_hint"))
        else:
            self._empty_cart_lbl.setText(t("order_empty_cart"))

    def _handle_cancel_clicked(self) -> None:
        table_name = self.table_data.get("name", "bàn") if self.table_data else "bàn"
        dialog = ConfirmCancelOrderDialog(table_name=table_name, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.set_items([])
            self.cancel_order_requested.emit()
