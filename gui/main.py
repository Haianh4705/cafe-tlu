"""Điểm vào chính của ứng dụng giao diện desktop CafeTLU (PySide6).

Khởi tạo QApplication, nạp theme TLU (gui.theme), quản lý phiên đăng nhập và điều hướng.
Chạy bằng lệnh: python -m gui.main hoặc make gui
"""

import logging
import os
import sys
from typing import Any

from PySide6.QtGui import QFont, QFontDatabase, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from gui.api_client import ApiClient
from gui.theme import COLOR, FONT, GLOBAL_QSS, RADIUS, SPACE
from gui.views.base import BaseView
from gui.views.login_view import LoginView
from gui.views.product_list_view import ProductListView
from shared.paths import resource_path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("gui.main")


class DashboardPlaceholderView(BaseView):
    """Màn hình Tổng quan / Dashboard chính sau khi đăng nhập."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        title = QLabel("Tổng quan hoạt động quán Café", self)
        title.setStyleSheet(
            f"color: {COLOR['navy']}; font-size: {FONT['h1']}px; font-weight: bold;"
        )

        subtitle = QLabel(
            "Chào mừng bạn đến với hệ thống POS CafeTLU.\n"
            "Chọn chức năng ở thanh menu bên trái để bắt đầu thao tác.",
            self,
        )
        subtitle.setStyleSheet(
            f"color: {COLOR['muted']}; font-size: {FONT['body']}px; line-height: 1.5;"
        )

        self._data_layout.addWidget(title)
        self._data_layout.addWidget(subtitle)
        self._data_layout.addStretch()

        self._set_state(self.STATE_DATA)


class MainWindow(QMainWindow):
    """Cửa sổ chính của ứng dụng hỗ trợ phân quyền người dùng và chuyển đổi màn hình."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("CafeTLU — Quản lý quán café")
        self.resize(1280, 720)
        self.setMinimumSize(1024, 600)

        self.api = ApiClient()
        self.current_user: dict[str, Any] | None = None

        self._init_ui()
        self._setup_shortcuts()

    def _init_ui(self) -> None:
        self._root_stack = QStackedWidget(self)
        self.setCentralWidget(self._root_stack)

        # 1. Màn hình Đăng nhập (Index 0)
        self._login_view = LoginView(self.api, self)
        self._login_view.login_success.connect(self._on_login_success)
        self._root_stack.addWidget(self._login_view)

        # 2. Khung làm việc chính của ứng dụng sau đăng nhập (Index 1)
        self._app_shell = self._build_app_shell()
        self._root_stack.addWidget(self._app_shell)

        # Bắt đầu tại màn hình đăng nhập
        self._root_stack.setCurrentWidget(self._login_view)

    def _build_app_shell(self) -> QWidget:
        """Dựng khung làm việc gồm Header Navy + Sidebar Navy + Content."""
        shell = QWidget(self)
        layout = QVBoxLayout(shell)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header (56px)
        self._header = self._build_header()
        layout.addWidget(self._header)

        # Body (Sidebar + Content)
        body = QWidget(shell)
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        self._sidebar = self._build_sidebar()
        body_layout.addWidget(self._sidebar)

        # Vùng chứa các view nghiệp vụ
        self._content_stack = QStackedWidget(body)
        self._content_stack.setStyleSheet(f"background-color: {COLOR['surface']};")

        # Đăng ký các màn hình
        self._dashboard_view = DashboardPlaceholderView(self)
        self._content_stack.addWidget(self._dashboard_view)

        self._product_list_view = ProductListView(self.api, self)
        self._content_stack.addWidget(self._product_list_view)

        body_layout.addWidget(self._content_stack, stretch=1)
        layout.addWidget(body, stretch=1)
        return shell

    def _build_header(self) -> QWidget:
        header = QFrame(self)
        header.setFixedHeight(56)
        header.setStyleSheet(
            f"background-color: {COLOR['navy']}; border: none; padding: 0 {SPACE['md']}px;"
        )

        layout = QHBoxLayout(header)
        layout.setContentsMargins(SPACE["md"], 0, SPACE["md"], 0)
        layout.setSpacing(SPACE["md"])

        logo_label = QLabel("CafeTLU", header)
        logo_label.setStyleSheet(
            f"color: {COLOR['surface']}; font-size: {FONT['title']}px; "
            f"font-weight: bold; background: transparent;"
        )

        badge_label = QLabel("ĐH THĂNG LONG", header)
        badge_label.setStyleSheet(
            f"color: {COLOR['tint_200']}; font-size: {FONT['caption']}px; "
            f"background: transparent; border: 1px solid {COLOR['brand_400']}; "
            f"border-radius: {RADIUS['sm']}px; padding: 2px 6px;"
        )

        self._user_label = QLabel("", header)
        self._user_label.setStyleSheet(
            f"color: {COLOR['tint_100']}; font-size: {FONT['body']}px; background: transparent;"
        )

        logout_btn = QPushButton("Đăng xuất", header)
        logout_btn.setProperty("variant", "secondary")
        logout_btn.setStyleSheet(
            f"background-color: transparent; color: {COLOR['surface']}; "
            f"border: 1px solid {COLOR['tint_200']};"
        )
        logout_btn.clicked.connect(self._handle_logout)

        layout.addWidget(logo_label)
        layout.addWidget(badge_label)
        layout.addStretch()
        layout.addWidget(self._user_label)
        layout.addWidget(logout_btn)
        return header

    def _build_sidebar(self) -> QWidget:
        sidebar = QFrame(self)
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet(
            f"background-color: {COLOR['navy_strong']}; border: none; "
            f"border-right: 1px solid {COLOR['navy_600']};"
        )

        self._sidebar_layout = QVBoxLayout(sidebar)
        self._sidebar_layout.setContentsMargins(SPACE["sm"], SPACE["md"], SPACE["sm"], SPACE["md"])
        self._sidebar_layout.setSpacing(SPACE["xs"])

        self._menu_buttons: dict[str, QPushButton] = {}
        items = [
            ("dashboard", "Tổng quan", ["admin", "staff", "barista"]),
            ("orders", "Bán hàng / Order", ["admin", "staff"]),
            ("products", "Quản lý thực đơn", ["admin"]),
            ("tables", "Quản lý bàn", ["admin", "staff"]),
            ("reports", "Báo cáo doanh thu", ["admin"]),
        ]

        for key, label, roles in items:
            btn = QPushButton(label, sidebar)
            btn.setProperty("required_roles", roles)
            btn.setCheckable(True)
            btn.clicked.connect(lambda _, k=key: self._switch_menu(k))
            self._sidebar_layout.addWidget(btn)
            self._menu_buttons[key] = btn

        self._sidebar_layout.addStretch()

        version_label = QLabel("Phiên bản 1.0", sidebar)
        version_label.setStyleSheet(
            f"color: {COLOR['muted']}; font-size: {FONT['caption']}px; background: transparent;"
        )
        self._sidebar_layout.addWidget(version_label)
        return sidebar

    def _switch_menu(self, key: str) -> None:
        """Chuyển đổi màn hình khi bấm chọn trên Sidebar."""
        for k, btn in self._menu_buttons.items():
            is_active = k == key
            btn.setChecked(is_active)
            if is_active:
                btn.setStyleSheet(
                    f"QPushButton {{ background-color: {COLOR['navy_600']}; color: {COLOR['surface']}; "
                    f"text-align: left; padding: {SPACE['sm']}px {SPACE['md']}px; "
                    f"border-left: 3px solid {COLOR['brand_400']}; border-radius: 0px; }}"
                )
            else:
                btn.setStyleSheet(
                    f"QPushButton {{ background-color: transparent; color: {COLOR['tint_200']}; "
                    f"text-align: left; padding: {SPACE['sm']}px {SPACE['md']}px; "
                    f"border: none; border-radius: {RADIUS['sm']}px; }}"
                    f"QPushButton:hover {{ background-color: {COLOR['navy']}; color: {COLOR['surface']}; }}"
                )

        if key == "dashboard":
            self._content_stack.setCurrentWidget(self._dashboard_view)
            self._dashboard_view.load()
        elif key == "products":
            self._content_stack.setCurrentWidget(self._product_list_view)
            self._product_list_view.load()

    def _update_sidebar_permissions(self, role: str) -> None:
        """Ẩn/Hiện menu theo quyền vai trò người dùng (TC-AUTH-03)."""
        for btn in self._menu_buttons.values():
            allowed_roles = btn.property("required_roles") or []
            btn.setVisible(role in allowed_roles)

    def _on_login_success(self, user_info: dict[str, Any]) -> None:
        """Chuyển vào ứng dụng khi đăng nhập thành công."""
        self.current_user = user_info
        full_name = user_info.get("full_name") or user_info.get("username", "Người dùng")
        role = user_info.get("role", "staff")

        role_display = {
            "admin": "Quản trị viên",
            "staff": "Thu ngân",
            "barista": "Pha chế",
        }.get(role, role)

        self._user_label.setText(f"{full_name} ({role_display})")
        self._update_sidebar_permissions(role)

        self._root_stack.setCurrentWidget(self._app_shell)
        self._switch_menu("dashboard")

    def _handle_logout(self) -> None:
        """Đăng xuất tài khoản và quay về màn hình đăng nhập."""
        self.api.logout()
        self.current_user = None
        self._root_stack.setCurrentWidget(self._login_view)

    def _setup_shortcuts(self) -> None:
        refresh_shortcut = QShortcut(QKeySequence("F5"), self)
        refresh_shortcut.activated.connect(self._on_refresh)

    def _on_refresh(self) -> None:
        current_view = self._content_stack.currentWidget()
        if isinstance(current_view, BaseView):
            current_view.refresh()


def setup_application_font(app: QApplication) -> None:
    """Nạp font Manrope từ assets và cấu hình fallback hệ thống có tiếng Việt."""
    font_path = resource_path("assets/fonts/Manrope[wght].ttf")
    if os.path.exists(font_path):
        QFontDatabase.addApplicationFont(font_path)

    font = QFont()
    font.setFamilies(["Manrope", "Segoe UI", "Arial", "sans-serif"])
    font.setPointSize(int(FONT["body"]))
    app.setFont(font)


def main() -> None:
    app = QApplication(sys.argv)
    setup_application_font(app)
    app.setStyleSheet(GLOBAL_QSS)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
