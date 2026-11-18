"""Widget sinh và hiển thị mã QR thanh toán VietQR dùng cho Kiosk và Thu ngân."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget
from reportlab.graphics.barcode.qrencoder import QRCode

from gui.i18n import format_currency, t
from gui.theme import COLOR, FONT, RADIUS, SPACE


def render_qr_pixmap(payload: str, size: int = 176) -> QPixmap:
    """Vẽ ma trận QR thành QPixmap sắc nét (nền trắng, ô navy TLU)."""
    qr = QRCode(None, 1)
    qr.addData(payload or "CAFETLU")
    qr.make()
    modules = qr.modules
    count = qr.getModuleCount()
    quiet_zone = 4
    total_modules = count + quiet_zone * 2

    pixmap = QPixmap(size, size)
    pixmap.fill(QColor(COLOR["surface"]))
    if count <= 0:
        return pixmap

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(COLOR["navy"]))

    cell = max(1, size // total_modules)
    actual_size = cell * total_modules
    offset = (size - actual_size) // 2

    for row in range(count):
        for col in range(count):
            if modules[row][col]:
                x = offset + (col + quiet_zone) * cell
                y = offset + (row + quiet_zone) * cell
                painter.drawRect(x, y, cell, cell)

    painter.end()
    return pixmap


class QrPaymentWidget(QFrame):
    """Khung hiển thị mã QR chuyển khoản kèm thông tin tài khoản và số tiền."""

    def __init__(
        self,
        payload: str,
        amount: int,
        memo: str,
        parent: QWidget | None = None,
        qr_size: int = 168,
    ) -> None:
        super().__init__(parent)
        self._qr_size = qr_size
        self.setObjectName("qrPaymentBox")
        self.setStyleSheet(
            f"QFrame#qrPaymentBox {{ background-color: {COLOR['tint_100']}; "
            f"border: 1px solid {COLOR['tint_200']}; border-radius: {RADIUS['md']}px; }}"
        )
        self._init_ui()
        self.update_payment(payload, amount, memo)

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE["md"], SPACE["md"], SPACE["md"], SPACE["md"])
        layout.setSpacing(SPACE["xs"])
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel(t("qr_payment_title"), self)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            f"color: {COLOR['navy']}; font-size: {FONT['body']}px; "
            f"font-weight: bold; background: transparent; border: none;"
        )
        layout.addWidget(title)

        canvas = QFrame(self)
        canvas.setObjectName("qrCanvas")
        canvas.setStyleSheet(
            f"QFrame#qrCanvas {{ background-color: {COLOR['surface']}; "
            f"border: 1px solid {COLOR['border']}; border-radius: {RADIUS['sm']}px; }}"
        )
        canvas_layout = QVBoxLayout(canvas)
        canvas_layout.setContentsMargins(SPACE["sm"], SPACE["sm"], SPACE["sm"], SPACE["sm"])

        self._qr_label = QLabel(canvas)
        self._qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._qr_label.setStyleSheet("background: transparent; border: none;")
        canvas_layout.addWidget(self._qr_label)
        layout.addWidget(canvas, alignment=Qt.AlignmentFlag.AlignCenter)

        self._bank_label = QLabel(t("qr_bank_account"), self)
        self._bank_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._bank_label.setStyleSheet(
            f"color: {COLOR['ink']}; font-size: {FONT['caption']}px; "
            f"font-weight: 600; background: transparent; border: none;"
        )
        layout.addWidget(self._bank_label)

        self._amount_label = QLabel("", self)
        self._amount_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._amount_label.setStyleSheet(
            f"color: {COLOR['navy']}; font-size: {FONT['body']}px; "
            f"font-weight: bold; background: transparent; border: none;"
        )
        layout.addWidget(self._amount_label)

        self._memo_label = QLabel("", self)
        self._memo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._memo_label.setStyleSheet(
            f"color: {COLOR['muted']}; font-size: {FONT['caption']}px; "
            f"background: transparent; border: none;"
        )
        layout.addWidget(self._memo_label)

    def update_payment(self, payload: str, amount: int, memo: str) -> None:
        """Cập nhật ảnh QR và số tiền / nội dung chuyển khoản."""
        self._qr_label.setPixmap(render_qr_pixmap(payload, size=self._qr_size))
        self._amount_label.setText(t("qr_amount_label", amount=format_currency(amount)))
        self._memo_label.setText(t("qr_transfer_memo", memo=memo))
