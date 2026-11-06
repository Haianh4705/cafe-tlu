"""Quản lý tập trung toàn bộ chuỗi ký tự hiển thị (tiếng Việt có dấu, UTF-8).

Tuân thủ:
- WORKFLOW.md mục 10 (Quy chuẩn GUI).
- Không hardcode chuỗi ký tự trong các file View.
- Dễ dàng kiểm soát chính tả, thuật ngữ và mở rộng đa ngôn ngữ nếu cần.
"""

from typing import Final

# ---------------------------------------------------------------------------
# Chuỗi hiển thị giao diện tiếng Việt (i18n)
# ---------------------------------------------------------------------------
STRINGS: Final[dict[str, str]] = {
    # Chung
    "app_name": "CafeTLU",
    "app_title": "CafeTLU — Quản lý quán café",
    "app_subtitle": "BTL Học phần Python 2026 — Đề tài 5 (ĐH Thăng Long)",
    "confirm": "Xác nhận",
    "cancel": "Huỷ bỏ",
    "save": "Lưu thay đổi",
    "delete": "Xoá",
    "edit": "Chỉnh sửa",
    "add_new": "Thêm mới",
    "search": "Tìm kiếm...",
    "retry": "Thử lại",
    "close": "Đóng",
    "loading": "Đang tải dữ liệu...",
    "refresh": "Làm mới (F5)",
    "no_data": "Chưa có dữ liệu",
    # Đăng nhập / Xác thực
    "login_title": "Đăng nhập hệ thống",
    "username": "Tên đăng nhập",
    "password": "Mật khẩu",
    "login_btn": "Đăng nhập",
    "logout_btn": "Đăng xuất",
    "login_failed": "Tên đăng nhập hoặc mật khẩu không chính xác.",
    # Menu điều hướng
    "nav_dashboard": "Tổng quan",
    "nav_orders": "Bán hàng / Order",
    "nav_products": "Quản lý thực đơn",
    "nav_tables": "Quản lý bàn",
    "nav_reports": "Báo cáo doanh thu",
    # Món ăn & Thực đơn
    "product_name": "Tên món",
    "product_category": "Danh mục",
    "product_price": "Đơn giá",
    "product_unit": "Đơn vị tính",
    "product_status": "Trạng thái",
    "product_available": "Còn bán",
    "product_out_of_stock": "Hết hàng",
    "product_empty": "Chưa có món nào trong thực đơn",
    "product_add_hint": "Thêm món đầu tiên để bắt đầu bán hàng",
    "confirm_delete_product": "Bạn có chắc chắn muốn xoá món '{name}' không?",
    # Bàn & Đơn hàng
    "table_free": "Bàn trống",
    "table_occupied": "Đang có khách",
    "table_reserved": "Đã đặt trước",
    "checkout": "Thanh toán",
    "total_amount": "Tổng tiền",
    "invoice": "Hoá đơn",
}


def t(key: str, **kwargs: object) -> str:
    """Lấy chuỗi hiển thị theo mã khoá, hỗ trợ định dạng tham số."""
    template = STRINGS.get(key, key)
    if kwargs:
        return template.format(**kwargs)
    return template
