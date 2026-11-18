"""Widget hiển thị một thẻ bàn trong sơ đồ bàn CafeTLU.

Tuân thủ:
- docs/api-contract.md: Endpoint 13 GET /tables.
- .claude/skills/ui-design/SKILL.md: Palette TLU, badge trạng thái bo góc sm.
"""

from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
)

from gui.i18n import t
from gui.theme import COLOR, FONT, RADIUS, SPACE


class TableCardWidget(QFrame):
    """Thẻ bàn trực quan hỗ trợ chọn bàn và hiển thị trạng thái."""

    selected = Signal(dict)

    def __init__(
        self,
        table_data: dict[str, Any],
        is_active: bool = False,
        parent: QFrame | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("tableCard")
        self.table_data = table_data
        self._is_active = is_active
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(84)

        self._init_ui()
        self.update_style()

    def _table_name(self, data: dict[str, Any]) -> str:
        return str(data.get("table_number") or data.get("name") or t("order_cart_table"))

    def _table_capacity(self, data: dict[str, Any]) -> int:
        return int(data.get("seating_capacity") or data.get("capacity") or 4)

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE["md"], SPACE["sm"], SPACE["md"], SPACE["sm"])
        layout.setSpacing(SPACE["xs"])

        top_row = QHBoxLayout()
        self._name_label = QLabel(self._table_name(self.table_data), self)
        self._name_label.setStyleSheet(
            f"font-size: {FONT['title']}px; font-weight: bold; "
            f"color: {COLOR['navy']}; background: transparent; border: none;"
        )
        top_row.addWidget(self._name_label)
        top_row.addStretch()

        self._capacity_label = QLabel(
            t("table_capacity_unit", capacity=self._table_capacity(self.table_data)), self
        )
        self._capacity_label.setStyleSheet(
            f"font-size: {FONT['caption']}px; color: {COLOR['muted']}; "
            f"background: transparent; border: none;"
        )
        top_row.addWidget(self._capacity_label)
        layout.addLayout(top_row)

        bottom_row = QHBoxLayout()
        self._status_badge = QLabel(self)
        self._status_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_badge.setFixedHeight(22)
        bottom_row.addWidget(self._status_badge)
        bottom_row.addStretch()
        layout.addLayout(bottom_row)

    def set_active(self, is_active: bool) -> None:
        """Cập nhật trạng thái đang được chọn."""
        self._is_active = is_active
        self.update_style()

    def update_data(self, table_data: dict[str, Any]) -> None:
        """Cập nhật dữ liệu bàn mới."""
        self.table_data = table_data
        self._name_label.setText(self._table_name(table_data))
        self._capacity_label.setText(
            t("table_capacity_unit", capacity=self._table_capacity(table_data))
        )
        self.update_style()

    def update_style(self) -> None:
        """Cập nhật màu sắc viền và badge theo trạng thái bàn."""
        status = self.table_data.get("status", "free")

        if status == "occupied":
            badge_text = t("table_occupied")
            badge_bg = COLOR["tint_200"]
            badge_color = COLOR["navy"]
            border_color = COLOR["brand_400"] if self._is_active else COLOR["border"]
        elif status == "reserved":
            badge_text = t("table_reserved")
            badge_bg = COLOR["warning_bg"]
            badge_color = COLOR["warning"]
            border_color = COLOR["warning"] if self._is_active else COLOR["border"]
        else:
            badge_text = t("table_free")
            badge_bg = COLOR["success_bg"]
            badge_color = COLOR["success"]
            border_color = COLOR["navy"] if self._is_active else COLOR["border"]

        self._status_badge.setText(badge_text)
        self._status_badge.setStyleSheet(
            f"background-color: {badge_bg}; color: {badge_color}; "
            f"font-size: {FONT['caption']}px; font-weight: 600; "
            f"border-radius: {RADIUS['sm']}px; padding: 2px {SPACE['sm']}px; border: none;"
        )

        bg_color = COLOR["tint_100"] if self._is_active else COLOR["surface"]
        border_width = 2 if self._is_active else 1
        active_border = COLOR["navy"] if self._is_active else border_color

        self.setStyleSheet(
            f"QFrame#tableCard {{ background-color: {bg_color}; "
            f"border: {border_width}px solid {active_border}; "
            f"border-radius: {RADIUS['md']}px; }} "
            f"QFrame#tableCard:hover {{ border-color: {COLOR['brand_400']}; "
            f"background-color: {COLOR['surface_subtle']}; }}"
        )

    def mousePressEvent(self, event: Any) -> None:  # noqa: N802
        super().mousePressEvent(event)
        self.selected.emit(self.table_data)
