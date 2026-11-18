"""Widget giỏ hàng và thẻ giao diện Kiosk khách hàng (KioskCartPanel, header, product card)."""

from collections.abc import Callable
from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from gui.i18n import format_currency, t
from gui.theme import COLOR, FONT, RADIUS, SPACE


def _header_btn_qss() -> str:
    return (
        f"QPushButton {{ background-color: transparent; color: {COLOR['surface']}; "
        f"border: 1px solid {COLOR['tint_200']}; border-radius: {RADIUS['sm']}px; "
        f"padding: {SPACE['xs']}px {SPACE['sm']}px; min-height: 0px; }} "
        f"QPushButton:hover {{ background-color: {COLOR['navy_600']}; color: {COLOR['surface']}; }} "
        f"QPushButton:disabled {{ background-color: {COLOR['navy_strong']}; color: {COLOR['muted']}; }}"
    )


def build_kiosk_header(
    parent: QWidget,
    *,
    on_table_changed: Callable[[], None],
    on_refresh: Callable[[], None],
    on_exit: Callable[[], None],
) -> tuple[QFrame, QComboBox]:
    """Tạo thanh header xanh navy cho Kiosk gồm dropdown bàn, nút tải lại và thoát về quầy."""
    header = QFrame(parent)
    header.setObjectName("kioskHeader")
    header.setFixedHeight(56)
    header.setStyleSheet(
        f"QFrame#kioskHeader {{ background-color: {COLOR['navy']}; border: none; }}"
    )
    layout = QHBoxLayout(header)
    layout.setContentsMargins(SPACE["md"], 0, SPACE["md"], 0)
    layout.setSpacing(SPACE["md"])

    brand = QLabel(t("app_name"), header)
    brand.setStyleSheet(
        f"color: {COLOR['surface']}; font-size: {FONT['title']}px; "
        f"font-weight: bold; background: transparent; border: none;"
    )
    badge = QLabel(t("kiosk_header_badge"), header)
    badge.setFixedHeight(24)
    badge.setStyleSheet(
        f"color: {COLOR['tint_100']}; font-size: {FONT['caption']}px; "
        f"background: transparent; border: 1px solid {COLOR['brand_400']}; "
        f"border-radius: {RADIUS['sm']}px; padding: 2px {SPACE['sm']}px;"
    )

    table_lbl = QLabel(t("kiosk_select_table") + ":", header)
    table_lbl.setStyleSheet(
        f"color: {COLOR['tint_100']}; font-size: {FONT['body']}px; "
        f"font-weight: 600; background: transparent; border: none;"
    )
    table_combo = QComboBox(header)
    table_combo.setMinimumWidth(220)
    table_combo.setFixedHeight(34)
    table_combo.currentIndexChanged.connect(on_table_changed)

    refresh_btn = QPushButton(t("refresh"), header)
    refresh_btn.setProperty("variant", "secondary")
    refresh_btn.setStyleSheet(_header_btn_qss())
    refresh_btn.clicked.connect(on_refresh)

    exit_btn = QPushButton(t("kiosk_exit_btn"), header)
    exit_btn.setProperty("variant", "secondary")
    exit_btn.setStyleSheet(_header_btn_qss())
    exit_btn.clicked.connect(on_exit)

    layout.addWidget(brand)
    layout.addWidget(badge)
    layout.addStretch()
    layout.addWidget(table_lbl)
    layout.addWidget(table_combo)
    layout.addWidget(refresh_btn)
    layout.addWidget(exit_btn)
    return header, table_combo


def build_kiosk_product_card(
    parent: QWidget,
    prod: dict[str, Any],
    *,
    on_choose: Callable[[dict[str, Any]], None],
) -> QFrame:
    """Tạo thẻ món trong lưới thực đơn Kiosk, khoá nút khi tạm hết."""
    is_avail = bool(prod.get("is_available", True))
    card = QFrame(parent)
    card.setObjectName("kioskProductCard")
    card.setMinimumHeight(110)
    card.setStyleSheet(
        f"QFrame#kioskProductCard {{ background-color: {COLOR['surface']}; "
        f"border: 1px solid {COLOR['border']}; border-radius: {RADIUS['md']}px; }}"
    )
    layout = QVBoxLayout(card)
    layout.setContentsMargins(SPACE["md"], SPACE["sm"], SPACE["md"], SPACE["sm"])
    layout.setSpacing(SPACE["xs"])

    cat_lbl = QLabel(str(prod.get("category", "")), card)
    cat_lbl.setStyleSheet(
        f"color: {COLOR['muted']}; font-size: {FONT['caption']}px; "
        f"background: transparent; border: none;"
    )
    name_lbl = QLabel(str(prod.get("name", "")), card)
    name_lbl.setWordWrap(True)
    name_lbl.setStyleSheet(
        f"color: {COLOR['ink']}; font-size: {FONT['body']}px; "
        f"font-weight: bold; background: transparent; border: none;"
    )
    layout.addWidget(cat_lbl)
    layout.addWidget(name_lbl, stretch=1)

    bottom = QHBoxLayout()
    price_lbl = QLabel(format_currency(prod.get("price", 0)), card)
    price_lbl.setStyleSheet(
        f"color: {COLOR['navy']}; font-size: {FONT['body']}px; "
        f"font-weight: bold; background: transparent; border: none;"
    )
    choose_btn = QPushButton(t("kiosk_choose_btn") if is_avail else t("product_out_of_stock"))
    choose_btn.setEnabled(is_avail)
    choose_btn.setFixedHeight(30)
    choose_btn.setStyleSheet(
        f"QPushButton {{ background-color: {COLOR['navy']}; color: {COLOR['surface']}; "
        f"border-radius: {RADIUS['sm']}px; font-weight: 600; "
        f"min-height: 0px; padding: 0px {SPACE['sm']}px; }} "
        f"QPushButton:hover {{ background-color: {COLOR['navy_600']}; }} "
        f"QPushButton:disabled {{ background-color: {COLOR['border']}; color: {COLOR['muted']}; }}"
    )
    if is_avail:
        choose_btn.clicked.connect(lambda _, p=prod: on_choose(p))

    bottom.addWidget(price_lbl)
    bottom.addStretch()
    bottom.addWidget(choose_btn)
    layout.addLayout(bottom)
    return card


def _qty_btn_qss() -> str:
    return (
        f"QPushButton {{ background-color: {COLOR['surface_subtle']}; color: {COLOR['ink']}; "
        f"border: 1px solid {COLOR['border']}; border-radius: {RADIUS['sm']}px; "
        f"font-weight: bold; min-height: 0px; padding: 0px; }} "
        f"QPushButton:hover {{ background-color: {COLOR['tint_100']}; }} "
        f"QPushButton:disabled {{ background-color: {COLOR['border']}; color: {COLOR['muted']}; }}"
    )


class KioskCartPanel(QFrame):
    """Bảng giỏ hàng bên phải màn Kiosk: bàn đang chọn, món, ghi chú, tổng tiền và nút gửi."""

    qty_changed = Signal(int, int)
    item_removed = Signal(int)
    clear_requested = Signal()
    submit_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("kioskCartPanel")
        self.setFixedWidth(364)
        self.setStyleSheet(
            f"QFrame#kioskCartPanel {{ background-color: {COLOR['surface']}; "
            f"border: 1px solid {COLOR['border']}; border-radius: {RADIUS['md']}px; }}"
        )
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE["md"], SPACE["md"], SPACE["md"], SPACE["md"])
        layout.setSpacing(SPACE["sm"])

        top_row = QHBoxLayout()
        title = QLabel(t("kiosk_cart_title"), self)
        title.setStyleSheet(
            f"color: {COLOR['navy']}; font-size: {FONT['title']}px; "
            f"font-weight: bold; background: transparent; border: none;"
        )
        self.table_badge = QLabel("", self)
        self.table_badge.setStyleSheet(
            f"background-color: {COLOR['tint_100']}; color: {COLOR['navy']}; "
            f"border: 1px solid {COLOR['tint_200']}; border-radius: {RADIUS['sm']}px; "
            f"padding: 2px {SPACE['sm']}px; font-size: {FONT['caption']}px; font-weight: 600;"
        )
        top_row.addWidget(title)
        top_row.addStretch()
        top_row.addWidget(self.table_badge)
        layout.addLayout(top_row)

        self.cart_table = QTableWidget(self)
        self.cart_table.setColumnCount(4)
        self.cart_table.setHorizontalHeaderLabels(
            [t("order_item_name"), t("order_item_qty"), t("order_item_price"), ""]
        )
        header = self.cart_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for col, width in ((1, 72), (2, 92), (3, 28)):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Fixed)
            self.cart_table.setColumnWidth(col, width)
        self.cart_table.verticalHeader().setVisible(False)
        self.cart_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.cart_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        layout.addWidget(self.cart_table, stretch=1)

        self.empty_cart_lbl = QLabel(t("kiosk_cart_empty"), self)
        self.empty_cart_lbl.setWordWrap(True)
        self.empty_cart_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_cart_lbl.setStyleSheet(
            f"color: {COLOR['muted']}; font-size: {FONT['body']}px; "
            f"padding: {SPACE['lg']}px; background: transparent; border: none;"
        )
        layout.addWidget(self.empty_cart_lbl, stretch=1)

        self.order_note_input = QLineEdit(self)
        self.order_note_input.setMaxLength(200)
        self.order_note_input.setPlaceholderText(t("kiosk_order_note_placeholder"))
        layout.addWidget(self.order_note_input)

        self.submit_error_banner = QLabel("", self)
        self.submit_error_banner.setWordWrap(True)
        self.submit_error_banner.setStyleSheet(
            f"color: {COLOR['red_text']}; background-color: {COLOR['danger_bg']}; "
            f"border: 1px solid {COLOR['danger_border']}; border-radius: {RADIUS['sm']}px; "
            f"padding: {SPACE['sm']}px; font-size: {FONT['caption']}px;"
        )
        self.submit_error_banner.setVisible(False)
        layout.addWidget(self.submit_error_banner)

        summary = QFrame(self)
        summary.setObjectName("kioskSummaryBox")
        summary.setStyleSheet(
            f"QFrame#kioskSummaryBox {{ background-color: {COLOR['surface_subtle']}; "
            f"border: 1px solid {COLOR['border']}; border-radius: {RADIUS['sm']}px; }}"
        )
        sum_layout = QHBoxLayout(summary)
        sum_layout.setContentsMargins(SPACE["sm"], SPACE["sm"], SPACE["sm"], SPACE["sm"])
        total_lbl = QLabel(t("order_total"), summary)
        total_lbl.setStyleSheet(
            f"color: {COLOR['muted']}; font-weight: 600; background: transparent; border: none;"
        )
        self.total_val_lbl = QLabel("0 đ", summary)
        self.total_val_lbl.setStyleSheet(
            f"color: {COLOR['navy']}; font-size: {FONT['h1']}px; "
            f"font-weight: bold; background: transparent; border: none;"
        )
        sum_layout.addWidget(total_lbl)
        sum_layout.addStretch()
        sum_layout.addWidget(self.total_val_lbl)
        layout.addWidget(summary)

        self.submit_hint_lbl = QLabel("", self)
        self.submit_hint_lbl.setStyleSheet(
            f"color: {COLOR['muted']}; font-size: {FONT['caption']}px; "
            f"background: transparent; border: none;"
        )
        layout.addWidget(self.submit_hint_lbl)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(SPACE["sm"])
        self.clear_btn = QPushButton(t("kiosk_clear_cart"), self)
        self.clear_btn.setProperty("variant", "danger")
        self.clear_btn.setFixedHeight(40)
        self.clear_btn.clicked.connect(self.clear_requested.emit)

        self.submit_btn = QPushButton(t("kiosk_submit_btn"), self)
        self.submit_btn.setFixedHeight(40)
        self.submit_btn.clicked.connect(self.submit_requested.emit)

        btn_row.addWidget(self.clear_btn, stretch=1)
        btn_row.addWidget(self.submit_btn, stretch=2)
        layout.addLayout(btn_row)

    def render_items(self, items: list[dict[str, Any]]) -> None:
        """Hiển thị lại các dòng món và tổng tiền trong giỏ hàng."""
        has_items = len(items) > 0
        self.cart_table.setVisible(has_items)
        self.empty_cart_lbl.setVisible(not has_items)
        self.cart_table.clearContents()
        self.cart_table.setRowCount(0)
        self.cart_table.setRowCount(len(items))

        total = 0
        for row, item in enumerate(items):
            qty = int(item["quantity"])
            line_total = int(item["price"]) * qty
            total += line_total
            label = item["name"] if not item["notes"] else f"{item['name']}\n({item['notes']})"
            self.cart_table.setRowHeight(row, 48 if item["notes"] else 38)
            self.cart_table.setItem(row, 0, QTableWidgetItem(label))

            qty_box = QWidget()
            qty_layout = QHBoxLayout(qty_box)
            qty_layout.setContentsMargins(0, 0, 0, 0)
            qty_layout.setSpacing(2)

            m_btn = QPushButton("-", qty_box)
            m_btn.setFixedSize(22, 22)
            m_btn.setStyleSheet(_qty_btn_qss())
            m_btn.clicked.connect(lambda _, r=row: self.qty_changed.emit(r, -1))

            q_lbl = QLabel(str(qty), qty_box)
            q_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            q_lbl.setFixedWidth(22)

            p_btn = QPushButton("+", qty_box)
            p_btn.setFixedSize(22, 22)
            p_btn.setStyleSheet(_qty_btn_qss())
            p_btn.clicked.connect(lambda _, r=row: self.qty_changed.emit(r, 1))

            qty_layout.addWidget(m_btn)
            qty_layout.addWidget(q_lbl)
            qty_layout.addWidget(p_btn)
            self.cart_table.setCellWidget(row, 1, qty_box)

            price_it = QTableWidgetItem(format_currency(line_total))
            price_it.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.cart_table.setItem(row, 2, price_it)

            del_btn = QPushButton("×")
            del_btn.setFixedSize(22, 22)
            del_btn.setStyleSheet(
                f"QPushButton {{ background-color: transparent; color: {COLOR['red_text']}; "
                f"border: none; font-weight: bold; min-height: 0px; padding: 0px; }} "
                f"QPushButton:hover {{ background-color: {COLOR['danger_bg']}; "
                f"color: {COLOR['red']}; border-radius: {RADIUS['sm']}px; }}"
            )
            del_btn.clicked.connect(lambda _, r=row: self.item_removed.emit(r))
            self.cart_table.setCellWidget(row, 3, del_btn)

        self.total_val_lbl.setText(format_currency(total))
