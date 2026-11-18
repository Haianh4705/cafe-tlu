"""Hộp thoại Thanh toán đơn hàng (CheckoutDialog) kèm QR VietQR trong CafeTLU.

Tuân thủ:
- docs/api-contract.md: Endpoint 19 POST /orders/{id}/checkout.
- docs/test-cases.md: TC-ORD-03.
- .claude/skills/ui-design/SKILL.md: Nút hành động chính Navy, QFrame#objectName, token theme.py.
"""

from typing import Any

from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from gui.i18n import format_currency, t
from gui.theme import COLOR, FONT, RADIUS, SPACE
from gui.widgets.qr_widget import QrPaymentWidget


class CheckoutDialog(QDialog):
    """Hộp thoại xác nhận thanh toán, tính tiền thừa hoặc hiện mã QR chuyển khoản."""

    def __init__(
        self,
        table_name: str,
        total_amount: int,
        order_items: list[dict[str, Any]],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.table_name = table_name
        self.total_amount = total_amount
        self.order_items = order_items
        self.payment_method = "cash"
        self.received_amount = total_amount

        self.setWindowTitle(t("checkout_title"))
        self.setFixedWidth(440)
        self.setModal(True)

        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE["lg"], SPACE["lg"], SPACE["lg"], SPACE["lg"])
        layout.setSpacing(SPACE["md"])

        title_box = QVBoxLayout()
        title_lbl = QLabel(f"{t('checkout_title')} — {self.table_name}", self)
        title_lbl.setStyleSheet(
            f"font-size: {FONT['title']}px; font-weight: bold; color: {COLOR['navy']};"
        )
        subtitle_lbl = QLabel(t("checkout_item_count", count=len(self.order_items)), self)
        subtitle_lbl.setStyleSheet(f"font-size: {FONT['caption']}px; color: {COLOR['muted']};")
        title_box.addWidget(title_lbl)
        title_box.addWidget(subtitle_lbl)
        layout.addLayout(title_box)

        amount_card = QFrame(self)
        amount_card.setObjectName("checkoutAmountCard")
        amount_card.setStyleSheet(
            f"QFrame#checkoutAmountCard {{ background-color: {COLOR['tint_100']}; "
            f"border: 1px solid {COLOR['brand_400']}; border-radius: {RADIUS['md']}px; }}"
        )
        card_layout = QVBoxLayout(amount_card)
        card_layout.setContentsMargins(SPACE["md"], SPACE["sm"], SPACE["md"], SPACE["sm"])

        total_lbl = QLabel(t("order_total"), amount_card)
        total_lbl.setStyleSheet(
            f"font-size: {FONT['caption']}px; font-weight: 600; color: {COLOR['navy']}; "
            f"background: transparent; border: none;"
        )
        self._total_val_lbl = QLabel(format_currency(self.total_amount), amount_card)
        self._total_val_lbl.setStyleSheet(
            f"font-size: {FONT['h1']}px; font-weight: bold; color: {COLOR['navy']}; "
            f"background: transparent; border: none;"
        )
        card_layout.addWidget(total_lbl)
        card_layout.addWidget(self._total_val_lbl)
        layout.addWidget(amount_card)

        pm_lbl = QLabel(t("checkout_payment_method"), self)
        pm_lbl.setStyleSheet(f"font-weight: bold; font-size: {FONT['body']}px;")
        layout.addWidget(pm_lbl)

        pm_layout = QHBoxLayout()
        self._cash_radio = QRadioButton(t("checkout_method_cash"), self)
        self._cash_radio.setChecked(True)
        self._cash_radio.toggled.connect(self._on_method_changed)
        pm_layout.addWidget(self._cash_radio)

        self._qr_radio = QRadioButton(t("checkout_method_qr"), self)
        self._qr_radio.toggled.connect(self._on_method_changed)
        pm_layout.addWidget(self._qr_radio)
        layout.addLayout(pm_layout)

        self._cash_calc_widget = QWidget(self)
        calc_layout = QVBoxLayout(self._cash_calc_widget)
        calc_layout.setContentsMargins(0, 0, 0, 0)
        calc_layout.setSpacing(SPACE["sm"])

        received_lbl = QLabel(t("checkout_customer_pay"), self._cash_calc_widget)
        received_lbl.setStyleSheet(f"font-weight: bold; font-size: {FONT['body']}px;")
        calc_layout.addWidget(received_lbl)

        self._received_input = QLineEdit(self._cash_calc_widget)
        self._received_input.setFixedHeight(36)
        self._received_input.setText(str(self.total_amount))
        self._received_input.textChanged.connect(self._calculate_change)
        calc_layout.addWidget(self._received_input)

        quick_btn_layout = QHBoxLayout()
        quick_btn_layout.setSpacing(SPACE["xs"])
        for amt in [50000, 100000, 200000, 500000]:
            btn = QPushButton(f"{amt // 1000}k", self._cash_calc_widget)
            btn.setProperty("variant", "secondary")
            btn.setFixedHeight(28)
            btn.clicked.connect(lambda _, a=amt: self._set_quick_cash(a))
            quick_btn_layout.addWidget(btn)

        exact_btn = QPushButton(t("checkout_exact"), self._cash_calc_widget)
        exact_btn.setProperty("variant", "secondary")
        exact_btn.setFixedHeight(28)
        exact_btn.clicked.connect(lambda: self._set_quick_cash(self.total_amount))
        quick_btn_layout.addWidget(exact_btn)
        calc_layout.addLayout(quick_btn_layout)

        change_layout = QHBoxLayout()
        change_title = QLabel(t("checkout_change") + ":", self._cash_calc_widget)
        change_title.setStyleSheet(f"font-weight: bold; font-size: {FONT['body']}px;")
        self._change_val_lbl = QLabel("0 đ", self._cash_calc_widget)
        self._change_val_lbl.setStyleSheet(
            f"font-size: {FONT['title']}px; font-weight: bold; color: {COLOR['success']};"
        )
        change_layout.addWidget(change_title)
        change_layout.addStretch()
        change_layout.addWidget(self._change_val_lbl)
        calc_layout.addLayout(change_layout)

        layout.addWidget(self._cash_calc_widget)

        qr_payload = f"CAFETLU|VIETQR|{self.table_name}|{self.total_amount}"
        self._qr_widget = QrPaymentWidget(
            payload=qr_payload,
            amount=self.total_amount,
            memo=self.table_name,
            parent=self,
            qr_size=144,
        )
        self._qr_widget.setVisible(False)
        layout.addWidget(self._qr_widget)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(SPACE["md"])

        cancel_btn = QPushButton(t("cancel"), self)
        cancel_btn.setProperty("variant", "secondary")
        cancel_btn.setStyleSheet(
            f"QPushButton {{ background-color: {COLOR['surface']}; color: {COLOR['navy']}; "
            f"border: 1.5px solid {COLOR['navy']}; border-radius: {RADIUS['sm']}px; "
            f"font-weight: bold; font-size: {FONT['body']}px; "
            f"padding: {SPACE['sm']}px {SPACE['md']}px; min-height: 22px; }} "
            f"QPushButton:hover {{ background-color: {COLOR['tint_100']}; }} "
            f"QPushButton:disabled {{ background-color: {COLOR['border']}; color: {COLOR['muted']}; }}"
        )
        cancel_btn.clicked.connect(self.reject)

        self._confirm_btn = QPushButton(t("checkout_confirm"), self)
        self._confirm_btn.setStyleSheet(
            f"QPushButton {{ background-color: {COLOR['navy']}; color: {COLOR['surface']}; "
            f"border: 1.5px solid {COLOR['navy']}; border-radius: {RADIUS['sm']}px; "
            f"font-weight: bold; font-size: {FONT['body']}px; "
            f"padding: {SPACE['sm']}px {SPACE['md']}px; min-height: 22px; }} "
            f"QPushButton:hover {{ background-color: {COLOR['navy_600']}; }} "
            f"QPushButton:disabled {{ background-color: {COLOR['border']}; color: {COLOR['muted']}; "
            f"border: 1.5px solid {COLOR['border']}; }}"
        )
        self._confirm_btn.clicked.connect(self.accept)

        btn_layout.addWidget(cancel_btn, stretch=1)
        btn_layout.addWidget(self._confirm_btn, stretch=2)
        layout.addLayout(btn_layout)

        self._calculate_change()

    def _on_method_changed(self) -> None:
        if self._cash_radio.isChecked():
            self.payment_method = "cash"
            self._cash_calc_widget.setVisible(True)
            self._qr_widget.setVisible(False)
            self._calculate_change()
        else:
            self.payment_method = "qr"
            self._cash_calc_widget.setVisible(False)
            self._qr_widget.setVisible(True)
            self._received_input.setText(str(self.total_amount))
            self._confirm_btn.setEnabled(True)
            self._confirm_btn.setText(t("checkout_confirm"))
        self.adjustSize()

    def _set_quick_cash(self, amount: int) -> None:
        self._received_input.setText(str(amount))

    def _calculate_change(self) -> None:
        val_str = self._received_input.text().strip().replace(".", "").replace(",", "")
        try:
            val = int(val_str) if val_str else 0
        except ValueError:
            val = 0

        self.received_amount = val
        change = val - self.total_amount
        if change >= 0:
            self._change_val_lbl.setText(format_currency(change))
            self._change_val_lbl.setStyleSheet(
                f"font-size: {FONT['title']}px; font-weight: bold; color: {COLOR['success']};"
            )
            self._confirm_btn.setEnabled(True)
            self._confirm_btn.setText(t("checkout_confirm"))
        else:
            self._change_val_lbl.setText(
                t("checkout_change_shortage", amount=format_currency(abs(change)))
            )
            self._change_val_lbl.setStyleSheet(
                f"font-size: {FONT['body']}px; font-weight: bold; color: {COLOR['red_text']};"
            )
            self._confirm_btn.setEnabled(False)
            self._confirm_btn.setText(t("checkout_insufficient"))
