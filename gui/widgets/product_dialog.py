"""Hộp thoại Thêm/Sửa và Xác nhận xoá món ăn trong CafeTLU.

Tuân thủ:
- .claude/skills/ui-design/SKILL.md: Màu Navy #000066 cho nút Lưu, Đỏ #F32409 cho nút Xoá.
- .claude/skills/pyside6-screen/SKILL.md: Validate tại chỗ, hộp thoại xác nhận khi xoá.
"""

from typing import Any

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from gui.i18n import t
from gui.theme import COLOR, FONT, RADIUS, SPACE


class ProductFormDialog(QDialog):
    """Hộp thoại tạo mới hoặc chỉnh sửa món ăn."""

    def __init__(
        self,
        categories: list[dict[str, Any]],
        product: dict[str, Any] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._categories = categories
        self._product = product
        self._is_edit_mode = product is not None

        title = t("product_title_edit") if self._is_edit_mode else t("product_title_add")
        self.setWindowTitle(title)
        self.setFixedWidth(460)
        self.setModal(True)

        self._init_ui()
        if self._is_edit_mode and product:
            self._fill_data(product)

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE["lg"], SPACE["lg"], SPACE["lg"], SPACE["lg"])
        layout.setSpacing(SPACE["md"])

        # Tiêu đề Dialog
        header_text = t("product_title_edit") if self._is_edit_mode else t("product_title_add")
        title_label = QLabel(header_text, self)
        title_label.setStyleSheet(
            f"color: {COLOR['navy']}; font-size: {FONT['title']}px; font-weight: bold;"
        )
        layout.addWidget(title_label)

        # Thông báo lỗi Inline
        self._error_label = QLabel("", self)
        self._error_label.setWordWrap(True)
        self._error_label.setStyleSheet(
            f"color: {COLOR['red_text']}; background-color: #FEF3F2; "
            f"border: 1px solid #FECDCA; border-radius: {RADIUS['sm']}px; "
            f"padding: {SPACE['sm']}px; font-size: {FONT['caption']}px;"
        )
        self._error_label.setVisible(False)
        layout.addWidget(self._error_label)

        # Form fields
        # 1. Tên món
        name_label = QLabel(t("product_name") + " *", self)
        name_label.setStyleSheet(f"font-weight: 600; color: {COLOR['ink']};")
        self._name_input = QLineEdit(self)
        self._name_input.setPlaceholderText("Ví dụ: Cà phê sữa đá, Trà đào cam sả...")
        layout.addWidget(name_label)
        layout.addWidget(self._name_input)

        # 2. Danh mục
        cat_label = QLabel(t("product_category") + " *", self)
        cat_label.setStyleSheet(f"font-weight: 600; color: {COLOR['ink']};")
        self._cat_combo = QComboBox(self)
        for cat in self._categories:
            self._cat_combo.addItem(cat.get("name", ""), cat.get("id"))
        layout.addWidget(cat_label)
        layout.addWidget(self._cat_combo)

        # 3. Đơn giá & Đơn vị tính (trên 1 dòng)
        price_unit_layout = QHBoxLayout()
        price_unit_layout.setSpacing(SPACE["md"])

        # Đơn giá
        price_box = QVBoxLayout()
        price_box.setSpacing(SPACE["xs"])
        price_label = QLabel(t("product_price") + " *", self)
        price_label.setStyleSheet(f"font-weight: 600; color: {COLOR['ink']};")
        self._price_spin = QSpinBox(self)
        self._price_spin.setRange(0, 100_000_000)
        self._price_spin.setSingleStep(1000)
        self._price_spin.setValue(30000)
        self._price_spin.setSuffix(" đ")
        price_box.addWidget(price_label)
        price_box.addWidget(self._price_spin)

        # Đơn vị tính
        unit_box = QVBoxLayout()
        unit_box.setSpacing(SPACE["xs"])
        unit_label = QLabel(t("product_unit") + " *", self)
        unit_label.setStyleSheet(f"font-weight: 600; color: {COLOR['ink']};")
        self._unit_input = QLineEdit(self)
        self._unit_input.setPlaceholderText("ly, cốc, đĩa...")
        self._unit_input.setText("ly")
        unit_box.addWidget(unit_label)
        unit_box.addWidget(self._unit_input)

        price_unit_layout.addLayout(price_box, stretch=2)
        price_unit_layout.addLayout(unit_box, stretch=1)
        layout.addLayout(price_unit_layout)

        # 4. Trạng thái còn bán
        self._available_check = QCheckBox(t("product_available"), self)
        self._available_check.setChecked(True)
        self._available_check.setStyleSheet(f"font-size: {FONT['body']}px;")
        layout.addWidget(self._available_check)

        layout.addSpacing(SPACE["sm"])

        # 5. Thanh nút bấm
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(SPACE["sm"])

        cancel_btn = QPushButton(t("cancel"), self)
        cancel_btn.setProperty("variant", "secondary")
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton(t("save"), self)
        save_btn.clicked.connect(self._validate_and_accept)

        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def _fill_data(self, product: dict[str, Any]) -> None:
        """Điền dữ liệu cũ vào form khi mở ở chế độ chỉnh sửa."""
        self._name_input.setText(str(product.get("name", "")))
        self._price_spin.setValue(int(product.get("price", 0)))
        self._unit_input.setText(str(product.get("unit", "ly")))
        self._available_check.setChecked(bool(product.get("is_available", True)))

        cat_id = product.get("category_id")
        if cat_id is not None:
            idx = self._cat_combo.findData(cat_id)
            if idx >= 0:
                self._cat_combo.setCurrentIndex(idx)

    def _validate_and_accept(self) -> None:
        """Kiểm tra hợp lệ trước khi đóng hộp thoại."""
        name = self._name_input.text().strip()
        price = self._price_spin.value()
        unit = self._unit_input.text().strip()

        if not name:
            self._error_label.setText(t("product_err_name_required"))
            self._error_label.setVisible(True)
            self._name_input.setFocus()
            return

        if price <= 0:
            self._error_label.setText(t("product_err_price_invalid"))
            self._error_label.setVisible(True)
            self._price_spin.setFocus()
            return

        if not unit:
            self._error_label.setText(t("product_err_unit_required"))
            self._error_label.setVisible(True)
            self._unit_input.setFocus()
            return

        self._error_label.setVisible(False)
        self.accept()

    def get_data(self) -> dict[str, Any]:
        """Lấy dữ liệu đã nhập từ form để gửi API."""
        return {
            "name": self._name_input.text().strip(),
            "category_id": self._cat_combo.currentData(),
            "price": self._price_spin.value(),
            "unit": self._unit_input.text().strip(),
            "is_available": self._available_check.isChecked(),
        }


class ConfirmDeleteDialog(QDialog):
    """Hộp thoại xác nhận xoá món ăn với màu cảnh báo Đỏ logo TLU."""

    def __init__(self, product_name: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(t("confirm"))
        self.setFixedWidth(420)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE["lg"], SPACE["lg"], SPACE["lg"], SPACE["lg"])
        layout.setSpacing(SPACE["md"])

        # Tiêu đề
        title = QLabel(t("confirm_delete_product", name=product_name), self)
        title.setWordWrap(True)
        title.setStyleSheet(
            f"color: {COLOR['ink']}; font-size: {FONT['title']}px; font-weight: bold;"
        )

        # Cảnh báo
        warning = QLabel(t("product_delete_warning"), self)
        warning.setWordWrap(True)
        warning.setStyleSheet(
            f"color: {COLOR['muted']}; font-size: {FONT['body']}px; line-height: 1.4;"
        )

        layout.addWidget(title)
        layout.addWidget(warning)
        layout.addSpacing(SPACE["sm"])

        # Nút bấm: Huỷ và Xoá (đỏ)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(SPACE["sm"])

        cancel_btn = QPushButton(t("cancel"), self)
        cancel_btn.setProperty("variant", "secondary")
        cancel_btn.clicked.connect(self.reject)

        delete_btn = QPushButton(t("delete"), self)
        delete_btn.setProperty("variant", "danger")
        delete_btn.clicked.connect(self.accept)

        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(delete_btn)
        layout.addLayout(btn_layout)
