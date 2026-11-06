"""Điểm vào chính của ứng dụng giao diện desktop CafeTLU (PySide6).

Khởi tạo QApplication, nạp theme TLU (gui.theme), thiết lập cửa sổ chính và điều hướng.
Chạy bằng lệnh: python -m gui.main hoặc make gui
"""

import logging
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QKeySequence, QShortcut
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

from gui.theme import COLOR, FONT, GLOBAL_QSS, RADIUS, SPACE
from gui.views.base import BaseView

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("gui.main")


class PlaceholderWelcomeView(BaseView):
    """Màn hình hiển thị mẫu cho tuần 1 để kiểm tra hoạt động của BaseView."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        title = QLabel("Hệ thống Quản lý Quán Café TLU", self)
        title.setStyleSheet(
            f"color: {COLOR['navy']}; font-size: {FONT['h1']}px; font-weight: bold;"
        )

        subtitle = QLabel(
            "BTL Học phần Python 2026 — Trường Đại học Thăng Long\n"
            "Giao diện đã tích hợp Palette TLU, chuẩn 4 trạng thái và sẵn sàng kết nối API.",
            self,
        )
        subtitle.setStyleSheet(
            f"color: {COLOR['muted']}; font-size: {FONT['body']}px; line-height: 1.5;"
        )

        btn_box = QHBoxLayout()
        test_loading_btn = QPushButton("Xem Loading", self)
        test_loading_btn.clicked.connect(lambda: self._set_state(self.STATE_LOADING))

        test_empty_btn = QPushButton("Xem Empty", self)
        test_empty_btn.setProperty("variant", "secondary")
        test_empty_btn.clicked.connect(
            lambda: self._set_state(
                self.STATE_EMPTY,
                message="Chưa có món nào trong thực đơn",
                action_text="Thêm món đầu tiên",
                on_action=lambda: self._set_state(self.STATE_DATA),
            )
        )

        test_error_btn = QPushButton("Xem Error", self)
        test_error_btn.setProperty("variant", "danger")
        test_error_btn.clicked.connect(
            lambda: self._set_state(self.STATE_ERROR, "Không thể kết nối đến máy chủ API")
        )

        btn_box.addWidget(test_loading_btn)
        btn_box.addWidget(test_empty_btn)
        btn_box.addWidget(test_error_btn)
        btn_box.addStretch()

        self._data_layout.addWidget(title)
        self._data_layout.addWidget(subtitle)
        self._data_layout.addSpacing(SPACE["md"])
        self._data_layout.addLayout(btn_box)
        self._data_layout.addStretch()

        # Hiển thị dữ liệu
        self._set_state(self.STATE_DATA)


class MainWindow(QMainWindow):
    """Cửa sổ chính của ứng dụng theo bố cục Header Navy + Sidebar Navy + Content."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("CafeTLU — Quản lý quán café")
        self.resize(1280, 720)
        self.setMinimumSize(1024, 600)

        self._init_ui()
        self._setup_shortcuts()

    def _init_ui(self) -> None:
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Header (Navy #000066, cao 56px)
        header = self._build_header()
        main_layout.addWidget(header)

        # 2. Body: Sidebar (Navy) + Content (Trắng)
        body_widget = QWidget(self)
        body_layout = QHBoxLayout(body_widget)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        sidebar = self._build_sidebar()
        body_layout.addWidget(sidebar)

        # Content area (QStackedWidget)
        self._content_stack = QStackedWidget(self)
        self._content_stack.setStyleSheet(f"background-color: {COLOR['surface']};")

        # Gắn view mặc định
        self._welcome_view = PlaceholderWelcomeView(self)
        self._content_stack.addWidget(self._welcome_view)

        body_layout.addWidget(self._content_stack, stretch=1)
        main_layout.addWidget(body_widget, stretch=1)

    def _build_header(self) -> QWidget:
        header = QFrame(self)
        header.setFixedHeight(56)
        header.setStyleSheet(
            f"background-color: {COLOR['navy']}; border: none; padding: 0 {SPACE['md']}px;"
        )

        layout = QHBoxLayout(header)
        layout.setContentsMargins(SPACE["md"], 0, SPACE["md"], 0)
        layout.setSpacing(SPACE["md"])

        # Logo / Title
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

        user_info = QLabel("Nhân viên thu ngân", header)
        user_info.setStyleSheet(
            f"color: {COLOR['tint_100']}; font-size: {FONT['body']}px; background: transparent;"
        )

        logout_btn = QPushButton("Đăng xuất", header)
        logout_btn.setProperty("variant", "secondary")
        logout_btn.setStyleSheet(
            f"background-color: transparent; color: {COLOR['surface']}; "
            f"border: 1px solid {COLOR['tint_200']};"
        )

        layout.addWidget(logo_label)
        layout.addWidget(badge_label)
        layout.addStretch()
        layout.addWidget(user_info)
        layout.addWidget(logout_btn)
        return header

    def _build_sidebar(self) -> QWidget:
        sidebar = QFrame(self)
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet(
            f"background-color: {COLOR['navy_strong']}; border: none; "
            f"border-right: 1px solid {COLOR['navy_600']};"
        )

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(SPACE["sm"], SPACE["md"], SPACE["sm"], SPACE["md"])
        layout.setSpacing(SPACE["xs"])

        menu_items = [
            ("Tổng quan", True),
            ("Bán hàng / Order", False),
            ("Quản lý thực đơn", False),
            ("Quản lý bàn", False),
            ("Báo cáo doanh thu", False),
        ]

        for text, is_active in menu_items:
            btn = QPushButton(text, sidebar)
            btn.setCheckable(True)
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
            layout.addWidget(btn)

        layout.addStretch()

        version_label = QLabel("Phiên bản 1.0 (Dev)", sidebar)
        version_label.setStyleSheet(
            f"color: {COLOR['muted']}; font-size: {FONT['caption']}px; background: transparent;"
        )
        layout.addWidget(version_label)
        return sidebar

    def _setup_shortcuts(self) -> None:
        """Thiết lập các phím tắt phổ biến theo quy chuẩn."""
        refresh_shortcut = QShortcut(QKeySequence("F5"), self)
        refresh_shortcut.activated.connect(self._on_refresh)

    def _on_refresh(self) -> None:
        current_view = self._content_stack.currentWidget()
        if isinstance(current_view, BaseView):
            current_view.refresh()


def main() -> None:
    """Hàm khởi động chính."""
    app = QApplication(sys.argv)

    # Cài đặt font ứng dụng
    font = QFont(str(FONT["family"]), int(FONT["body"]))
    app.setFont(font)

    # Nạp toàn bộ stylesheet TLU
    app.setStyleSheet(GLOBAL_QSS)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
