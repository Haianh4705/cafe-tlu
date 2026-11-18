"""Điểm vào chính của ứng dụng giao diện desktop CafeTLU (PySide6).

Khởi tạo QApplication, nạp theme TLU (gui.theme), quản lý phiên đăng nhập và điều hướng.
Chạy bằng lệnh: python -m gui.main hoặc make gui
"""

import logging
import os
import sys
from typing import Any

from PySide6.QtCore import Signal
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

from gui.api_client import ApiClient, ApiClientError
from gui.i18n import t
from gui.theme import COLOR, FONT, GLOBAL_QSS, RADIUS, SPACE
from gui.views.base import ApiWorker, BaseView
from gui.views.customer_kiosk_view import CustomerKioskView
from gui.views.dashboard_view import DashboardView
from gui.views.login_view import LoginView
from gui.views.order_view import OrderView
from gui.views.product_list_view import ProductListView
from shared.paths import resource_path
from shared.version import __version__

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("gui.main")


def _header_btn_qss() -> str:
    return (
        f"QPushButton {{ background-color: transparent; color: {COLOR['surface']}; "
        f"border: 1px solid {COLOR['tint_200']}; border-radius: {RADIUS['sm']}px; "
        f"padding: {SPACE['xs']}px {SPACE['md']}px; }} "
        f"QPushButton:hover {{ background-color: {COLOR['navy_600']}; color: {COLOR['surface']}; }} "
        f"QPushButton:disabled {{ background-color: {COLOR['navy_strong']}; color: {COLOR['muted']}; "
        f"border-color: {COLOR['muted']}; }}"
    )


class MainWindow(QMainWindow):
    """Cửa sổ chính của ứng dụng hỗ trợ phân quyền người dùng và chuyển đổi màn hình."""

    session_expired = Signal()

    def __init__(self, api_client: ApiClient | None = None) -> None:
        super().__init__()
        self.setWindowTitle(t("app_title"))
        self.resize(1280, 720)
        self.setMinimumSize(1024, 600)

        self.api = api_client or ApiClient()
        self.api.on_unauthenticated = self.session_expired.emit
        self.current_user: dict[str, Any] | None = None
        self._logout_worker: ApiWorker | None = None

        self.session_expired.connect(self._handle_session_expired)
        self._init_ui()
        self._setup_shortcuts()

    def _init_ui(self) -> None:
        self._root_stack = QStackedWidget(self)
        self.setCentralWidget(self._root_stack)

        # 1. Màn hình Đăng nhập (Index 0)
        self._login_view = LoginView(self.api, self)
        self._login_view.login_success.connect(self._on_login_success)
        self._login_view.open_kiosk_requested.connect(self._open_kiosk)
        self._root_stack.addWidget(self._login_view)

        # 2. Khung làm việc chính sau đăng nhập (Index 1)
        self._app_shell = self._build_app_shell()
        self._root_stack.addWidget(self._app_shell)

        # 3. Màn hình Kiosk khách tự chọn món (Index 2)
        self._kiosk_view = CustomerKioskView(self.api, self)
        self._kiosk_view.exit_kiosk_requested.connect(self._close_kiosk)
        self._root_stack.addWidget(self._kiosk_view)

        self._root_stack.setCurrentWidget(self._login_view)

    def _build_app_shell(self) -> QWidget:
        """Dựng khung làm việc gồm Header Navy + Sidebar Navy + Content."""
        shell = QWidget(self)
        layout = QVBoxLayout(shell)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._header = self._build_header()
        layout.addWidget(self._header)

        body = QWidget(shell)
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        self._sidebar = self._build_sidebar()
        body_layout.addWidget(self._sidebar)

        self._content_stack = QStackedWidget(body)
        self._content_stack.setStyleSheet(f"background-color: {COLOR['surface']};")

        self._dashboard_view = DashboardView(self.api, self)
        self._content_stack.addWidget(self._dashboard_view)

        self._order_view = OrderView(self.api, self)
        self._content_stack.addWidget(self._order_view)

        self._product_list_view = ProductListView(self.api, self)
        self._content_stack.addWidget(self._product_list_view)

        body_layout.addWidget(self._content_stack, stretch=1)
        layout.addWidget(body, stretch=1)
        return shell

    def _build_header(self) -> QWidget:
        header = QFrame(self)
        header.setObjectName("appHeader")
        header.setFixedHeight(56)
        header.setStyleSheet(
            f"QFrame#appHeader {{ background-color: {COLOR['navy']}; border: none; }}"
        )

        layout = QHBoxLayout(header)
        layout.setContentsMargins(SPACE["md"], 0, SPACE["md"], 0)
        layout.setSpacing(SPACE["md"])

        logo_label = QLabel(t("app_name"), header)
        logo_label.setStyleSheet(
            f"color: {COLOR['surface']}; font-size: {FONT['title']}px; "
            f"font-weight: bold; background: transparent; border: none;"
        )

        badge_label = QLabel(t("header_university_badge"), header)
        badge_label.setObjectName("universityBadge")
        badge_label.setFixedHeight(24)
        badge_label.setStyleSheet(
            f"color: {COLOR['tint_100']}; font-size: {FONT['caption']}px; "
            f"background: transparent; border: 1px solid {COLOR['brand_400']}; "
            f"border-radius: {RADIUS['sm']}px; padding: 2px {SPACE['sm']}px;"
        )

        self._user_label = QLabel("", header)
        self._user_label.setStyleSheet(
            f"color: {COLOR['tint_100']}; font-size: {FONT['body']}px; "
            f"background: transparent; border: none;"
        )

        kiosk_btn = QPushButton(t("kiosk_switch_btn"), header)
        kiosk_btn.setProperty("variant", "secondary")
        kiosk_btn.setStyleSheet(_header_btn_qss())
        kiosk_btn.clicked.connect(self._open_kiosk)

        self._logout_btn = QPushButton(t("logout_btn"), header)
        self._logout_btn.setProperty("variant", "secondary")
        self._logout_btn.setStyleSheet(_header_btn_qss())
        self._logout_btn.clicked.connect(self._handle_logout)

        layout.addWidget(logo_label)
        layout.addWidget(badge_label)
        layout.addStretch()
        layout.addWidget(self._user_label)
        layout.addWidget(kiosk_btn)
        layout.addWidget(self._logout_btn)
        return header

    def _build_sidebar(self) -> QWidget:
        sidebar = QFrame(self)
        sidebar.setObjectName("appSidebar")
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet(
            f"QFrame#appSidebar {{ background-color: {COLOR['navy_strong']}; border: none; "
            f"border-right: 1px solid {COLOR['navy_600']}; }}"
        )

        self._sidebar_layout = QVBoxLayout(sidebar)
        self._sidebar_layout.setContentsMargins(SPACE["sm"], SPACE["md"], SPACE["sm"], SPACE["md"])
        self._sidebar_layout.setSpacing(SPACE["xs"])

        self._menu_buttons: dict[str, QPushButton] = {}
        items = [
            ("dashboard", t("nav_dashboard"), ["admin", "staff", "barista"]),
            ("orders", t("nav_orders"), ["admin", "staff"]),
            ("products", t("nav_products"), ["admin"]),
            ("tables", t("nav_tables"), ["admin", "staff"]),
            ("reports", t("nav_reports"), ["admin"]),
        ]

        for key, label, roles in items:
            btn = QPushButton(label, sidebar)
            btn.setProperty("required_roles", roles)
            btn.setCheckable(True)
            btn.clicked.connect(lambda _, k=key: self._switch_menu(k))
            self._sidebar_layout.addWidget(btn)
            self._menu_buttons[key] = btn

        self._sidebar_layout.addStretch()

        version_label = QLabel(t("version_prefix", version=__version__), sidebar)
        version_label.setStyleSheet(
            f"color: {COLOR['tint_200']}; font-size: {FONT['caption']}px; "
            f"background: transparent; border: none;"
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
                    f"border: none; border-left: 3px solid {COLOR['brand_400']}; border-radius: 0px; }}"
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
        elif key == "orders":
            self._content_stack.setCurrentWidget(self._order_view)
            self._order_view.load()
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
        full_name = user_info.get("full_name") or user_info.get("username", "")
        role = user_info.get("role", "staff")

        role_display = {
            "admin": t("role_admin"),
            "staff": t("role_staff"),
            "barista": t("role_barista"),
        }.get(role, role)

        self._user_label.setText(f"{full_name} ({role_display})")
        self._update_sidebar_permissions(role)
        self._product_list_view.set_user_role(role)
        if hasattr(self, "_order_view"):
            self._order_view.cashier_name = full_name

        self._root_stack.setCurrentWidget(self._app_shell)
        self._switch_menu("dashboard")

    def _handle_logout(self) -> None:
        """Đăng xuất trên luồng nền; luôn xoá phiên cục bộ và quay về form đăng nhập."""
        if self._logout_worker is not None and self._logout_worker.isRunning():
            return
        self._logout_btn.setEnabled(False)
        self._logout_btn.setText(t("logout_loading"))
        worker = ApiWorker(self.api.logout, parent=self)
        worker.succeeded.connect(self._finish_logout)
        worker.failed.connect(self._finish_logout)
        self._logout_worker = worker
        worker.start()

    def _finish_logout(self, result: object = None) -> None:
        self._logout_btn.setEnabled(True)
        self._logout_btn.setText(t("logout_btn"))
        self.api.clear_tokens()
        self.current_user = None
        self._login_view._password_input.clear()
        self._root_stack.setCurrentWidget(self._login_view)
        if isinstance(result, Exception):
            logger.warning("Đăng xuất gặp lỗi hoặc mất kết nối: %s", result)
            if isinstance(result, ApiClientError) and result.code == "NETWORK_ERROR":
                self._login_view._show_error(t("logout_server_unreachable"))
            elif isinstance(result, ApiClientError) and result.code == "UNAUTHENTICATED":
                self._login_view._show_error(t("session_expired"))
        else:
            self._login_view._clear_error()

    def _handle_session_expired(self) -> None:
        """Đưa người dùng về màn đăng nhập khi phiên hết hạn trong lúc làm việc."""
        if self._root_stack.currentWidget() is self._login_view:
            return
        self.api.clear_tokens()
        self.current_user = None
        self._login_view._password_input.clear()
        self._root_stack.setCurrentWidget(self._login_view)
        self._login_view._show_error(t("session_expired"))
        self._login_view._password_input.setFocus()

    def _open_kiosk(self) -> None:
        self._root_stack.setCurrentWidget(self._kiosk_view)
        self._kiosk_view.load()

    def _close_kiosk(self) -> None:
        self._kiosk_view.on_close()
        if self.current_user is not None:
            self._root_stack.setCurrentWidget(self._app_shell)
        else:
            self._root_stack.setCurrentWidget(self._login_view)

    def _setup_shortcuts(self) -> None:
        refresh_shortcut = QShortcut(QKeySequence("F5"), self)
        refresh_shortcut.activated.connect(self._on_refresh)

    def _on_refresh(self) -> None:
        current_root = self._root_stack.currentWidget()
        if current_root is self._kiosk_view:
            self._kiosk_view.refresh()
            return
        current_view = self._content_stack.currentWidget()
        if isinstance(current_view, BaseView):
            current_view.refresh()


def setup_application_font(app: QApplication) -> None:
    """Nạp font Manrope từ assets và cấu hình fallback hệ thống có tiếng Việt."""
    font_path = resource_path("assets/fonts/Manrope[wght].ttf")
    if os.path.exists(font_path):
        QFontDatabase.addApplicationFont(font_path)

    font = QFont()
    font.setFamilies(["Manrope", "Be Vietnam Pro", "Inter", "Segoe UI", "sans-serif"])
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
