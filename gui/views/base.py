"""Lớp cơ sở (BaseView) và Worker đa luồng cho các màn hình PySide6.

Tuân thủ:
- WORKFLOW.md mục 10 (Quy chuẩn GUI).
- Kỹ năng pyside6-screen (.claude/skills/pyside6-screen/SKILL.md).
- 4 trạng thái bắt buộc: loading, empty, error, data.
- Xử lý gọi API trên luồng nền (Worker), tránh làm treo giao diện.
"""

from collections.abc import Callable
import logging
from typing import Any

from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from gui.theme import COLOR, FONT, RADIUS, SPACE

logger = logging.getLogger(__name__)


class ApiWorker(QThread):
    """Worker chạy tác vụ API trên luồng nền bằng QThread."""

    succeeded = Signal(object)
    failed = Signal(Exception)

    def __init__(
        self,
        func: Callable[..., Any],
        *args: Any,
        parent: QObject | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent)
        self._func = func
        self._args = args
        self._kwargs = kwargs

    def run(self) -> None:
        try:
            result = self._func(*self._args, **self._kwargs)
            self.succeeded.emit(result)
        except Exception as exc:
            logger.exception("ApiWorker gặp lỗi khi thực thi %s", self._func)
            self.failed.emit(exc)


class BaseView(QWidget):
    """Lớp giao diện cơ sở chuẩn cho tất cả các màn hình trong CafeTLU.

    Cung cấp sẵn bộ quản lý 4 trạng thái bắt buộc:
    - 'loading': Hiện chỉ báo đang tải, ngăn thao tác trùng lặp.
    - 'empty': Hiện thông điệp danh sách trống + nút hành động gợi ý.
    - 'error': Hiện thông báo lỗi chi tiết + nút 'Thử lại'.
    - 'data': Hiển thị giao diện dữ liệu chính của màn hình.
    """

    STATE_LOADING = "loading"
    STATE_EMPTY = "empty"
    STATE_ERROR = "error"
    STATE_DATA = "data"

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._active_workers: list[ApiWorker] = []

        self._root_layout = QVBoxLayout(self)
        self._root_layout.setContentsMargins(0, 0, 0, 0)
        self._root_layout.setSpacing(0)

        # Quản lý chuyển đổi 4 trạng thái bằng QStackedWidget
        self._state_stack = QStackedWidget(self)
        self._root_layout.addWidget(self._state_stack)

        # 1. Loading widget
        self._loading_widget = self._build_loading_widget()
        self._state_stack.addWidget(self._loading_widget)

        # 2. Empty widget
        self._empty_label = QLabel("Chưa có dữ liệu", self)
        self._empty_action_btn = QPushButton("Thêm mới", self)
        self._empty_widget = self._build_empty_widget()
        self._state_stack.addWidget(self._empty_widget)

        # 3. Error widget
        self._error_label = QLabel("Đã có lỗi xảy ra", self)
        self._retry_btn = QPushButton("Thử lại", self)
        self._error_widget = self._build_error_widget()
        self._state_stack.addWidget(self._error_widget)

        # 4. Data widget (nơi màn hình con gắn nội dung chính vào)
        self._data_widget = QWidget(self)
        self._data_layout = QVBoxLayout(self._data_widget)
        self._data_layout.setContentsMargins(
            SPACE["md"], SPACE["md"], SPACE["md"], SPACE["md"]
        )
        self._data_layout.setSpacing(SPACE["md"])
        self._state_stack.addWidget(self._data_widget)

        # Mặc định mở ở trạng thái loading
        self._set_state(self.STATE_LOADING)

    # ------------------------------------------------------------------
    # Giao diện con cần cài đặt (Lifecycle methods)
    # ------------------------------------------------------------------
    def load(self) -> None:
        """Được gọi khi mở màn hình để nạp dữ liệu ban đầu."""
        pass

    def refresh(self) -> None:
        """Được gọi khi người dùng bấm F5 hoặc nút làm mới."""
        self.load()

    def on_close(self) -> None:
        """Được gọi khi đóng hoặc rời màn hình, dừng mọi worker đang chạy ngầm."""
        for worker in self._active_workers:
            if worker.isRunning():
                worker.quit()
                worker.wait(1000)
        self._active_workers.clear()

    # ------------------------------------------------------------------
    # Quản lý luồng nền
    # ------------------------------------------------------------------
    def start_worker(
        self,
        func: Callable[..., Any],
        on_success: Callable[[Any], None],
        on_error: Callable[[Exception], None] | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> ApiWorker:
        """Khởi chạy an toàn một worker gọi API trên luồng nền."""
        worker = ApiWorker(func, *args, parent=self, **kwargs)
        worker.succeeded.connect(on_success)
        worker.failed.connect(on_error or self._on_default_error)
        worker.finished.connect(lambda: self._remove_worker(worker))

        self._active_workers.append(worker)
        worker.start()
        return worker

    def _remove_worker(self, worker: ApiWorker) -> None:
        if worker in self._active_workers:
            self._active_workers.remove(worker)

    def _on_default_error(self, exc: Exception) -> None:
        logger.error("Lỗi xảy ra trong màn hình: %s", exc)
        self._set_state(self.STATE_ERROR, str(exc))

    # ------------------------------------------------------------------
    # Chuyển đổi trạng thái (State switching)
    # ------------------------------------------------------------------
    def _set_state(
        self,
        state: str,
        message: str = "",
        action_text: str | None = None,
        on_action: Callable[[], None] | None = None,
    ) -> None:
        """Chuyển giao diện sang 1 trong 4 trạng thái bắt buộc."""
        if state == self.STATE_LOADING:
            self._state_stack.setCurrentWidget(self._loading_widget)
        elif state == self.STATE_EMPTY:
            if message:
                self._empty_label.setText(message)
            if action_text and on_action:
                self._empty_action_btn.setText(action_text)
                self._empty_action_btn.setVisible(True)
                try:
                    self._empty_action_btn.clicked.disconnect()
                except RuntimeError:
                    pass
                self._empty_action_btn.clicked.connect(on_action)
            else:
                self._empty_action_btn.setVisible(False)
            self._state_stack.setCurrentWidget(self._empty_widget)
        elif state == self.STATE_ERROR:
            self._error_label.setText(message or "Không thể tải dữ liệu. Vui lòng thử lại.")
            self._state_stack.setCurrentWidget(self._error_widget)
        elif state == self.STATE_DATA:
            self._state_stack.setCurrentWidget(self._data_widget)

    # ------------------------------------------------------------------
    # Dựng sẵn UI cho các trạng thái phụ
    # ------------------------------------------------------------------
    def _build_loading_widget(self) -> QWidget:
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(SPACE["xl"], SPACE["xl"], SPACE["xl"], SPACE["xl"])
        layout.setSpacing(SPACE["md"])

        label = QLabel("Đang tải dữ liệu...", widget)
        label.setStyleSheet(f"color: {COLOR['muted']}; font-size: {FONT['body']}px;")
        label.setWordWrap(True)

        progress = QProgressBar(widget)
        progress.setRange(0, 0)  # indeterminate spinner style
        progress.setTextVisible(False)
        progress.setFixedHeight(4)
        progress.setStyleSheet(
            f"QProgressBar {{ background: {COLOR['surface_subtle']}; border: none; }}"
            f"QProgressBar::chunk {{ background: {COLOR['navy']}; }}"
        )

        layout.addStretch()
        layout.addWidget(label)
        layout.addWidget(progress)
        layout.addStretch()
        return widget

    def _build_empty_widget(self) -> QWidget:
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(SPACE["xl"], SPACE["xl"], SPACE["xl"], SPACE["xl"])
        layout.setSpacing(SPACE["md"])

        self._empty_label.setStyleSheet(
            f"color: {COLOR['muted']}; font-size: {FONT['title']}px; font-weight: 500;"
        )
        self._empty_label.setWordWrap(True)

        self._empty_action_btn.setStyleSheet(
            f"background-color: {COLOR['navy']}; color: {COLOR['surface']}; "
            f"border-radius: {RADIUS['sm']}px; padding: {SPACE['sm']}px {SPACE['md']}px;"
        )

        layout.addStretch()
        layout.addWidget(self._empty_label)
        layout.addWidget(self._empty_action_btn)
        layout.addStretch()
        return widget

    def _build_error_widget(self) -> QWidget:
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(SPACE["xl"], SPACE["xl"], SPACE["xl"], SPACE["xl"])
        layout.setSpacing(SPACE["md"])

        self._error_label.setStyleSheet(
            f"color: {COLOR['red_text']}; font-size: {FONT['body']}px; font-weight: 500;"
        )
        self._error_label.setWordWrap(True)

        self._retry_btn.setProperty("variant", "secondary")
        self._retry_btn.clicked.connect(self.refresh)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self._retry_btn)
        btn_layout.addStretch()

        layout.addStretch()
        layout.addWidget(self._error_label)
        layout.addLayout(btn_layout)
        layout.addStretch()
        return widget

