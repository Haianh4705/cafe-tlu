"""Các hộp thoại phụ trợ cho màn Kiosk khách hàng: tuỳ chọn món và xác nhận đơn kèm QR."""

from collections.abc import Callable
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from gui.i18n import format_currency, t
from gui.theme import COLOR, FONT, RADIUS, SPACE
from gui.widgets.qr_widget import QrPaymentWidget

SUGAR_OPTIONS = ("100% đường", "70% đường", "50% đường", "Không đường")
ICE_OPTIONS = ("Đá vừa", "Ít đá", "Đá riêng", "Không đá")


def _chip_qss() -> str:
    return (
        f"QPushButton {{ background-color: {COLOR['surface_subtle']}; color: {COLOR['ink']}; "
        f"border: 1px solid {COLOR['border']}; border-radius: {RADIUS['sm']}px; "
        f"padding: {SPACE['xs']}px {SPACE['sm']}px; font-weight: 500; }} "
        f"QPushButton:hover {{ background-color: {COLOR['tint_100']}; "
        f"border-color: {COLOR['brand_400']}; }} "
        f"QPushButton:checked {{ background-color: {COLOR['navy']}; color: {COLOR['surface']}; "
        f"border-color: {COLOR['navy']}; font-weight: 600; }}"
    )


def _square_btn_qss() -> str:
    return (
        f"QPushButton {{ background-color: {COLOR['surface']}; color: {COLOR['navy']}; "
        f"border: 1px solid {COLOR['navy']}; border-radius: {RADIUS['sm']}px; "
        f"font-weight: bold; min-height: 0px; padding: 0px; }} "
        f"QPushButton:hover {{ background-color: {COLOR['tint_100']}; }} "
        f"QPushButton:disabled {{ background-color: {COLOR['border']}; color: {COLOR['muted']}; "
        f"border-color: {COLOR['border']}; }}"
    )


def build_kiosk_mock_menu() -> dict[str, Any]:
    """Dữ liệu mẫu khi bật APP_ENV=demo cho màn Kiosk."""
    from gui.views.order_view import MOCK_PRODUCTS, MOCK_TABLES

    cats: list[dict[str, Any]] = []
    seen: set[str] = set()
    for idx, prod in enumerate(MOCK_PRODUCTS, start=1):
        cat_name = str(prod.get("category", ""))
        if cat_name and cat_name not in seen:
            seen.add(cat_name)
            cats.append({"id": idx, "name": cat_name, "is_active": True})
    tables = [
        {
            "id": tbl["id"],
            "table_number": tbl.get("name", f"Bàn {tbl['id']:02d}"),
            "area": "Tầng 1",
            "seating_capacity": tbl.get("capacity", 4),
            "status": (
                "available" if tbl.get("status") == "free" else tbl.get("status", "available")
            ),
        }
        for tbl in MOCK_TABLES
    ]
    return {"categories": cats, "tables": tables, "products": list(MOCK_PRODUCTS)}


class CustomerItemOptionDialog(QDialog):
    """Hộp thoại chọn nhanh mức đường, lượng đá, số lượng và ghi chú cho món."""

    def __init__(self, product: dict[str, Any], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._product = product
        self._quantity = 1
        category_name = str(product.get("category") or "").lower()
        self._has_drink_options = "bánh" not in category_name

        self.setWindowTitle(t("kiosk_option_title"))
        self.setFixedWidth(440)
        self.setModal(True)
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE["lg"], SPACE["lg"], SPACE["lg"], SPACE["lg"])
        layout.setSpacing(SPACE["md"])

        header = QFrame(self)
        header.setObjectName("kioskOptionHeader")
        header.setStyleSheet(
            f"QFrame#kioskOptionHeader {{ background-color: {COLOR['tint_100']}; "
            f"border: 1px solid {COLOR['tint_200']}; border-radius: {RADIUS['sm']}px; }}"
        )
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(SPACE["md"], SPACE["sm"], SPACE["md"], SPACE["sm"])

        name_lbl = QLabel(str(self._product.get("name", "")), header)
        name_lbl.setWordWrap(True)
        name_lbl.setStyleSheet(
            f"color: {COLOR['navy']}; font-size: {FONT['title']}px; "
            f"font-weight: bold; background: transparent; border: none;"
        )
        price_lbl = QLabel(format_currency(self._product.get("price", 0)), header)
        price_lbl.setStyleSheet(
            f"color: {COLOR['ink']}; font-size: {FONT['body']}px; "
            f"font-weight: bold; background: transparent; border: none;"
        )
        header_layout.addWidget(name_lbl, stretch=1)
        header_layout.addWidget(price_lbl)
        layout.addWidget(header)

        self._sugar_group: QButtonGroup | None = None
        self._ice_group: QButtonGroup | None = None
        if self._has_drink_options:
            self._sugar_group = self._add_chip_row(layout, t("kiosk_option_sugar"), SUGAR_OPTIONS)
            self._ice_group = self._add_chip_row(layout, t("kiosk_option_ice"), ICE_OPTIONS)

        qty_row = QHBoxLayout()
        qty_lbl = QLabel(t("kiosk_option_qty"), self)
        qty_lbl.setStyleSheet(f"color: {COLOR['ink']}; font-weight: 600;")
        qty_row.addWidget(qty_lbl)
        qty_row.addStretch()

        minus_btn = QPushButton("-", self)
        minus_btn.setProperty("variant", "secondary")
        minus_btn.setFixedSize(32, 32)
        minus_btn.setStyleSheet(_square_btn_qss())
        minus_btn.clicked.connect(lambda: self._change_qty(-1))

        self._qty_val_lbl = QLabel("1", self)
        self._qty_val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._qty_val_lbl.setFixedWidth(36)
        self._qty_val_lbl.setStyleSheet(
            f"font-size: {FONT['title']}px; font-weight: bold; color: {COLOR['ink']};"
        )

        plus_btn = QPushButton("+", self)
        plus_btn.setProperty("variant", "secondary")
        plus_btn.setFixedSize(32, 32)
        plus_btn.setStyleSheet(_square_btn_qss())
        plus_btn.clicked.connect(lambda: self._change_qty(1))

        qty_row.addWidget(minus_btn)
        qty_row.addWidget(self._qty_val_lbl)
        qty_row.addWidget(plus_btn)
        layout.addLayout(qty_row)

        note_lbl = QLabel(t("kiosk_option_note"), self)
        note_lbl.setStyleSheet(f"color: {COLOR['ink']}; font-weight: 600;")
        self._note_input = QLineEdit(self)
        self._note_input.setMaxLength(120)
        self._note_input.setPlaceholderText(t("kiosk_option_note_placeholder"))
        layout.addWidget(note_lbl)
        layout.addWidget(self._note_input)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(SPACE["sm"])
        cancel_btn = QPushButton(t("cancel"), self)
        cancel_btn.setProperty("variant", "secondary")
        cancel_btn.clicked.connect(self.reject)

        self._add_btn = QPushButton("", self)
        self._add_btn.clicked.connect(self.accept)
        self._refresh_add_btn()

        btn_row.addWidget(cancel_btn, stretch=1)
        btn_row.addWidget(self._add_btn, stretch=2)
        layout.addLayout(btn_row)

    def _add_chip_row(
        self, parent_layout: QVBoxLayout, label_text: str, options: tuple[str, ...]
    ) -> QButtonGroup:
        lbl = QLabel(label_text, self)
        lbl.setStyleSheet(f"color: {COLOR['ink']}; font-weight: 600;")
        parent_layout.addWidget(lbl)

        row = QHBoxLayout()
        row.setSpacing(SPACE["xs"])
        group = QButtonGroup(self)
        group.setExclusive(True)
        for idx, opt in enumerate(options):
            btn = QPushButton(opt, self)
            btn.setCheckable(True)
            btn.setChecked(idx == 0)
            btn.setStyleSheet(_chip_qss())
            group.addButton(btn, idx)
            row.addWidget(btn)
        parent_layout.addLayout(row)
        return group

    def _change_qty(self, delta: int) -> None:
        self._quantity = max(1, min(50, self._quantity + delta))
        self._qty_val_lbl.setText(str(self._quantity))
        self._refresh_add_btn()

    def _refresh_add_btn(self) -> None:
        unit_price = int(self._product.get("price", 0))
        subtotal = format_currency(unit_price * self._quantity)
        self._add_btn.setText(f"{t('kiosk_option_add')} · {subtotal}")

    def get_selection(self) -> dict[str, Any]:
        """Trả số lượng và ghi chú đã ghép cho dòng món."""
        parts: list[str] = []
        if self._has_drink_options and self._sugar_group and self._ice_group:
            sugar_btn = self._sugar_group.checkedButton()
            ice_btn = self._ice_group.checkedButton()
            if sugar_btn:
                parts.append(sugar_btn.text())
            if ice_btn:
                parts.append(ice_btn.text())
        extra = self._note_input.text().strip()
        if extra:
            parts.append(extra)
        return {"quantity": self._quantity, "notes": ", ".join(parts)}


class OrderSubmittedDialog(QDialog):
    """Hộp thoại thông báo gửi đơn thành công kèm mã đơn và mã QR VietQR."""

    def __init__(self, order_data: dict[str, Any], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._order_data = order_data
        self.setWindowTitle(t("kiosk_submitted_title"))
        self.setFixedWidth(440)
        self.setModal(True)
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE["lg"], SPACE["lg"], SPACE["lg"], SPACE["lg"])
        layout.setSpacing(SPACE["sm"])

        title = QLabel(t("kiosk_submitted_title"), self)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            f"color: {COLOR['success']}; font-size: {FONT['title']}px; font-weight: bold;"
        )
        layout.addWidget(title)

        order_code = str(self._order_data.get("order_code", ""))
        code_lbl = QLabel(t("kiosk_submitted_code", order_code=order_code), self)
        code_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        code_lbl.setStyleSheet(
            f"color: {COLOR['navy']}; font-size: {FONT['h1']}px; font-weight: bold;"
        )
        code_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(code_lbl)

        table_number = str(self._order_data.get("table_number", ""))
        items = self._order_data.get("items") or []
        item_count = sum(int(it.get("quantity", 1)) for it in items)
        sub_lbl = QLabel(
            t("kiosk_submitted_table", table_number=table_number, count=item_count),
            self,
        )
        sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub_lbl.setStyleSheet(f"color: {COLOR['muted']}; font-size: {FONT['body']}px;")
        layout.addWidget(sub_lbl)

        total_amount = int(self._order_data.get("total_amount", 0))
        qr_payload = str(
            self._order_data.get("qr_payload") or f"CAFETLU|VIETQR|{order_code}|{total_amount}"
        )
        self.qr_widget = QrPaymentWidget(
            payload=qr_payload,
            amount=total_amount,
            memo=order_code,
            parent=self,
            qr_size=160,
        )
        layout.addWidget(self.qr_widget)

        guide = QLabel(t("kiosk_submitted_guide"), self)
        guide.setWordWrap(True)
        guide.setAlignment(Qt.AlignmentFlag.AlignCenter)
        guide.setStyleSheet(f"color: {COLOR['muted']}; font-size: {FONT['caption']}px;")
        layout.addWidget(guide)

        done_btn = QPushButton(t("kiosk_submitted_new_order"), self)
        done_btn.setFixedHeight(40)
        done_btn.clicked.connect(self.accept)
        layout.addWidget(done_btn)


def build_kiosk_menu_section(
    parent: QWidget,
    *,
    on_search_changed: Callable[[], None],
    on_clear_filters: Callable[[], None],
) -> dict[str, Any]:
    """Tạo khung thực đơn Kiosk bên trái gồm thanh danh mục, ô tìm kiếm và lưới món."""
    panel = QWidget(parent)
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(SPACE["sm"])

    cat_bar_widget = QWidget(panel)
    cat_bar_layout = QHBoxLayout(cat_bar_widget)
    cat_bar_layout.setContentsMargins(0, 0, 0, 0)
    cat_bar_layout.setSpacing(SPACE["xs"])
    layout.addWidget(cat_bar_widget)

    search_row = QHBoxLayout()
    search_row.setSpacing(SPACE["sm"])
    search_input = QLineEdit(panel)
    search_input.setFixedHeight(36)
    search_input.setPlaceholderText(t("kiosk_search_placeholder"))
    search_input.textChanged.connect(on_search_changed)

    clear_filter_btn = QPushButton(t("product_clear_filter"), panel)
    clear_filter_btn.setProperty("variant", "secondary")
    clear_filter_btn.setFixedHeight(36)
    clear_filter_btn.clicked.connect(on_clear_filters)
    search_row.addWidget(search_input, stretch=1)
    search_row.addWidget(clear_filter_btn)
    layout.addLayout(search_row)

    menu_scroll = QScrollArea(panel)
    menu_scroll.setWidgetResizable(True)
    menu_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    menu_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

    menu_container = QWidget(menu_scroll)
    menu_grid = QGridLayout(menu_container)
    menu_grid.setContentsMargins(0, 0, SPACE["xs"], 0)
    menu_grid.setSpacing(SPACE["sm"])
    menu_scroll.setWidget(menu_container)
    layout.addWidget(menu_scroll, stretch=1)

    menu_empty_label = QLabel(t("kiosk_empty_search"), panel)
    menu_empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    menu_empty_label.setStyleSheet(
        f"color: {COLOR['muted']}; font-size: {FONT['body']}px; padding: {SPACE['lg']}px;"
    )
    menu_empty_label.setVisible(False)
    layout.addWidget(menu_empty_label, stretch=1)
    return {
        "panel": panel,
        "cat_bar_widget": cat_bar_widget,
        "cat_bar_layout": cat_bar_layout,
        "search_input": search_input,
        "clear_filter_btn": clear_filter_btn,
        "menu_scroll": menu_scroll,
        "menu_container": menu_container,
        "menu_grid": menu_grid,
        "menu_empty_label": menu_empty_label,
    }


def build_kiosk_mock_order(
    payload: dict[str, Any],
    tables: list[dict[str, Any]],
    cart_items: list[dict[str, Any]],
) -> dict[str, Any]:
    """Tạo kết quả đặt món giả lập khi chạy Kiosk ở chế độ demo."""
    total = sum(int(it["price"]) * int(it["quantity"]) for it in cart_items)
    tbl = next((x for x in tables if x.get("id") == payload["table_id"]), {})
    order_code = "ORD-DEMO-001"
    return {
        "order_code": order_code,
        "table_number": tbl.get("table_number", "Bàn 01"),
        "total_amount": total,
        "qr_payload": f"CAFETLU|VIETQR|{order_code}|{total}",
        "items": list(cart_items),
    }
