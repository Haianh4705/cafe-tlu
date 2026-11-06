"""Design tokens và kiểu dáng giao diện cho CafeTLU.

Nguồn:
- Bảng màu nhận diện Trường Đại học Thăng Long (thanglong.edu.vn + logo chính thức).
- Kỹ năng ui-design (.claude/skills/ui-design/SKILL.md).
- Lưới khoảng cách 8pt.
"""

from typing import Final

# ---------------------------------------------------------------------------
# 1. Bảng màu TLU (Design Tokens)
# ---------------------------------------------------------------------------
COLOR: Final[dict[str, str]] = {
    # Nhận diện thương hiệu TLU
    "navy": "#000066",  # Màu thương hiệu chính: Header, sidebar, nút chính, tiêu đề
    "navy_strong": "#050C56",  # Nền tối hơn của logo
    "navy_600": "#0624A5",  # Hover/active của nút navy
    "brand_400": "#4C7BFE",  # Chỉ dùng cho focus ring, viền active, chỉ báo đồ hoạ
    "tint_100": "#F1F5FF",  # Nền hàng đang chọn trong bảng, vùng nhấn
    "tint_200": "#CCDAFF",  # Viền nhấn, badge nhạt
    # Màu cảnh báo / nguy hiểm (Swoosh đỏ trong logo TLU)
    "red": "#F32409",  # CHỈ dùng cho hành động nguy hiểm: xoá, huỷ đơn, cảnh báo nặng
    "red_text": "#B42318",  # Chữ đỏ nhỏ (< 18px) đảm bảo tương phản AA (>= 4.5:1)
    # Trung tính / Nội dung
    "ink": "#0C0A09",  # Chữ nội dung chính (19.8:1 trên trắng - AAA)
    "muted": "#6B7280",  # Nhãn phụ, mô tả, placeholder
    "border": "#E7E5E4",  # Đường kẻ phân cách, viền bảng
    "surface": "#FFFFFF",  # Nền nội dung, nền thẻ
    "surface_subtle": "#F9FAFB",  # Nền phụ, header của bảng
    # Trạng thái
    "success": "#1E7B45",  # Thành công, bàn trống
    "warning": "#A16207",  # Chờ pha chế, cảnh báo nhẹ
}

# ---------------------------------------------------------------------------
# 2. Lưới khoảng cách 8pt (Spacing Grid)
# ---------------------------------------------------------------------------
SPACE: Final[dict[str, int]] = {
    "xs": 4,
    "sm": 8,
    "md": 16,
    "lg": 24,
    "xl": 32,
}

# ---------------------------------------------------------------------------
# 3. Bo góc (Radius - chỉ 2 mức theo chuẩn)
# ---------------------------------------------------------------------------
RADIUS: Final[dict[str, int]] = {
    "sm": 6,
    "md": 10,
}

# ---------------------------------------------------------------------------
# 4. Kiểu chữ (Typography)
# ---------------------------------------------------------------------------
FONT: Final[dict[str, object]] = {
    "family": "Manrope",
    "fallback": "Be Vietnam Pro, Inter, Segoe UI, sans-serif",
    "caption": 12,
    "body": 14,
    "label": 14,
    "title": 18,
    "h1": 24,
}

# ---------------------------------------------------------------------------
# 5. Global Stylesheet (QSS) cho toàn ứng dụng
# ---------------------------------------------------------------------------
GLOBAL_QSS: Final[str] = f"""
* {{
    font-family: "{FONT['family']}", {FONT['fallback']};
    font-size: {FONT['body']}px;
    color: {COLOR['ink']};
}}

QWidget {{
    background-color: {COLOR['surface']};
}}

/* Nút bấm mặc định: Hành động chính Navy */
QPushButton {{
    background-color: {COLOR['navy']};
    color: {COLOR['surface']};
    border: none;
    border-radius: {RADIUS['sm']}px;
    padding: {SPACE['sm']}px {SPACE['md']}px;
    font-weight: 600;
    min-height: 20px;
}}

QPushButton:hover {{
    background-color: {COLOR['navy_600']};
}}

QPushButton:pressed {{
    background-color: {COLOR['navy_strong']};
}}

QPushButton:disabled {{
    background-color: {COLOR['border']};
    color: {COLOR['muted']};
}}

/* Nút phụ / Secondary Button */
QPushButton[variant="secondary"] {{
    background-color: {COLOR['surface']};
    color: {COLOR['navy']};
    border: 1px solid {COLOR['navy']};
}}

QPushButton[variant="secondary"]:hover {{
    background-color: {COLOR['tint_100']};
}}

/* Nút nguy hiểm (Xoá, Huỷ đơn) */
QPushButton[variant="danger"] {{
    background-color: {COLOR['red']};
    color: {COLOR['surface']};
}}

QPushButton[variant="danger"]:hover {{
    background-color: #D91D04;
}}

/* Ô nhập liệu */
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    background-color: {COLOR['surface']};
    border: 1px solid {COLOR['border']};
    border-radius: {RADIUS['sm']}px;
    padding: {SPACE['sm']}px {SPACE['sm']}px;
    color: {COLOR['ink']};
    selection-background-color: {COLOR['tint_200']};
    selection-color: {COLOR['ink']};
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
    border: 1.5px solid {COLOR['brand_400']};
}}

/* Bảng dữ liệu */
QTableWidget, QTableView {{
    background-color: {COLOR['surface']};
    border: 1px solid {COLOR['border']};
    border-radius: {RADIUS['sm']}px;
    gridline-color: {COLOR['border']};
    selection-background-color: {COLOR['tint_100']};
    selection-color: {COLOR['ink']};
}}

QHeaderView::section {{
    background-color: {COLOR['surface_subtle']};
    color: {COLOR['muted']};
    font-weight: 600;
    padding: {SPACE['sm']}px;
    border: none;
    border-bottom: 1px solid {COLOR['border']};
}}

/* Thanh cuộn */
QScrollBar:vertical {{
    border: none;
    background: {COLOR['surface_subtle']};
    width: 8px;
    margin: 0px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical {{
    background: {COLOR['border']};
    min-height: 20px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical:hover {{
    background: {COLOR['muted']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
"""
