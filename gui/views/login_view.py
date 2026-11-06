"""Màn hình Đăng nhập (LoginView) cho ứng dụng CafeTLU.

Tuân thủ:
- docs/api-contract.md: Endpoint POST /auth/login.
- docs/test-cases.md: TC-AUTH-01, TC-AUTH-02, TC-AUTH-03.
- .claude/skills/ui-design/SKILL.md: Nhận diện TLU (Navy #000066), lưới 8pt.
- .claude/skills/pyside6-screen/SKILL.md: Validate form tại chỗ, gọi API trên luồng nền.
"""

import logging
from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from gui.api_client import ApiClient, ApiClientError
from gui.i18n import t
from gui.theme import COLOR, FONT, RADIUS, SPACE
from gui.views.base import BaseView

logger = logging.getLogger(__name__)


class LoginView(BaseView):
    """Màn hình Đăng nhập hệ thống kết nối với Backend API."""

    # Tín hiệu phát ra khi đăng nhập thành công, mang theo thông tin tài khoản
    login_success = Signal(dict)

    def __init__(self, api_client: ApiClient, parent: QWidget | None = None) -> None:
        self.api = api_client
        super().__init__(parent)
        self._init_login_form()

    def _init_login_form(self) -> None:
        """Khởi tạo giao diện đăng nhập căn giữa màn hình."""
        # Chuyển BaseView sang trạng thái dữ liệu chính
        self._set_state(self.STATE_DATA)

        # Xoá padding mặc định của BaseView để căn giữa form
        self._data_layout.setContentsMargins(0, 0, 0, 0)
        self._data_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Hộp chứa form đăng nhập (Card đăng nhập)
        card = QFrame(self)
        card.setFixedWidth(400)
        card.setStyleSheet(
            f"QFrame {{ "
            f"  background-color: {COLOR['surface']}; "
            f"  border: 1px solid {COLOR['border']}; "
            f"  border-radius: {RADIUS['md']}px; "
            f"  padding: {SPACE['lg']}px; "
            f"}}"
        )
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(SPACE["md"])

        # 1. Tiêu đề & Logo
        title_label = QLabel(t("app_name"), card)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(
            f"color: {COLOR['navy']}; font-size: {FONT['h1']}px; font-weight: bold; border: none;"
        )

        subtitle_label = QLabel(t("login_title"), card)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet(
            f"color: {COLOR['muted']}; font-size: {FONT['body']}px; border: none;"
        )

        card_layout.addWidget(title_label)
        card_layout.addWidget(subtitle_label)
        card_layout.addSpacing(SPACE["xs"])

        # 2. Thông báo lỗi (Inline Banner)
        self._error_banner = QLabel("", card)
        self._error_banner.setWordWrap(True)
        self._error_banner.setStyleSheet(
            f"color: {COLOR['red_text']}; background-color: #FEF3F2; "
            f"border: 1px solid #FECDCA; border-radius: {RADIUS['sm']}px; "
            f"padding: {SPACE['sm']}px; font-size: {FONT['caption']}px;"
        )
        self._error_banner.setVisible(False)
        card_layout.addWidget(self._error_banner)

        # 3. Ô nhập tên đăng nhập
        user_label = QLabel(t("username"), card)
        user_label.setStyleSheet(f"font-weight: 600; color: {COLOR['ink']}; border: none;")
        self._username_input = QLineEdit(card)
        self._username_input.setPlaceholderText("Nhập tên đăng nhập")
        self._username_input.returnPressed.connect(self._handle_login)

        card_layout.addWidget(user_label)
        card_layout.addWidget(self._username_input)

        # 4. Ô nhập mật khẩu
        pass_label = QLabel(t("password"), card)
        pass_label.setStyleSheet(f"font-weight: 600; color: {COLOR['ink']}; border: none;")
        self._password_input = QLineEdit(card)
        self._password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._password_input.setPlaceholderText("••••••••")
        self._password_input.returnPressed.connect(self._handle_login)

        card_layout.addWidget(pass_label)
        card_layout.addWidget(self._password_input)
        card_layout.addSpacing(SPACE["sm"])

        # 5. Nút bấm Đăng nhập
        self._login_btn = QPushButton(t("login_btn"), card)
        self._login_btn.setFixedHeight(40)
        self._login_btn.clicked.connect(self._handle_login)
        card_layout.addWidget(self._login_btn)

        # Chân thẻ ghi chú đồ án
        footer_label = QLabel("Đồ án học phần Python — ĐH Thăng Long", card)
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_label.setStyleSheet(
            f"color: {COLOR['muted']}; font-size: {FONT['caption']}px; border: none; margin-top: {SPACE['sm']}px;"
        )
        card_layout.addWidget(footer_label)

        # Đặt card vào giữa màn hình
        self._data_layout.addWidget(card)

    def _show_error(self, message: str) -> None:
        """Hiển thị thông báo lỗi ngay trên form."""
        self._error_banner.setText(message)
        self._error_banner.setVisible(True)

    def _clear_error(self) -> None:
        """Ẩn thông báo lỗi."""
        self._error_banner.setVisible(False)
        self._error_banner.setText("")

    def _handle_login(self) -> None:
        """Kiểm tra hợp lệ dữ liệu và gửi yêu cầu đăng nhập trên luồng nền."""
        username = self._username_input.text().strip()
        password = self._password_input.text()

        # Validate phía giao diện trước khi gửi request (Definition of Ready)
        if not username:
            self._show_error("Vui lòng nhập tên đăng nhập.")
            self._username_input.setFocus()
            return

        if not password:
            self._show_error("Vui lòng nhập mật khẩu.")
            self._password_input.setFocus()
            return

        self._clear_error()
        self._set_loading(True)

        # Gọi API trên luồng nền qua worker (không làm treo UI)
        self.start_worker(
            self.api.login,
            on_success=self._on_login_success,
            on_error=self._on_login_failed,
            username=username,
            password=password,
        )

    def _set_loading(self, is_loading: bool) -> None:
        """Khoá/Mở nút đăng nhập và ô nhập liệu khi đang gửi request."""
        self._login_btn.setEnabled(not is_loading)
        self._username_input.setEnabled(not is_loading)
        self._password_input.setEnabled(not is_loading)
        if is_loading:
            self._login_btn.setText("Đang đăng nhập...")
        else:
            self._login_btn.setText(t("login_btn"))

    def _on_login_success(self, data: Any) -> None:
        """Xử lý khi backend trả về token và thông tin người dùng thành công."""
        self._set_loading(False)
        user_info = data.get("user", {}) if isinstance(data, dict) else {}
        logger.info("Đăng nhập thành công tài khoản: %s (role: %s)", user_info.get("username"), user_info.get("role"))
        self.login_success.emit(user_info)

    def _on_login_failed(self, exc: Exception) -> None:
        """Xử lý khi backend trả về lỗi xác thực."""
        self._set_loading(False)
        if isinstance(exc, ApiClientError):
            self._show_error(exc.message or t("login_failed"))
        else:
            self._show_error(t("login_failed"))
        self._password_input.selectAll()
        self._password_input.setFocus()
