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
    "product_out_of_stock": "Tạm hết",
    "product_empty": "Chưa có món nào trong thực đơn",
    "product_add_hint": "Thêm món đầu tiên để bắt đầu bán hàng",
    "product_title_add": "Thêm món mới",
    "product_title_edit": "Chỉnh sửa món",
    "product_all_categories": "Tất cả danh mục",
    "product_search_placeholder": "Tìm theo tên món (Ctrl+F)...",
    "product_delete_warning": "Món ăn này sẽ bị xoá mềm và không còn xuất hiện trong thực đơn bán hàng.",
    "product_err_name_required": "Vui lòng nhập tên món.",
    "product_err_price_invalid": "Đơn giá phải lớn hơn 0 đ.",
    "product_err_unit_required": "Vui lòng nhập đơn vị tính.",
    "confirm_delete_product": "Bạn có chắc chắn muốn xoá món '{name}' không?",
    # Bàn & Đơn hàng
    "table_free": "Bàn trống",
    "table_occupied": "Đang có khách",
    "table_reserved": "Đã đặt trước",
    "table_all": "Tất cả bàn",
    "table_filter_free": "Bàn trống",
    "table_filter_occupied": "Đang có khách",
    "checkout": "Thanh toán",
    "total_amount": "Tổng tiền",
    "invoice": "Hoá đơn",
    "order_title": "Bán hàng & Gọi món tại bàn",
    "order_select_table_hint": "Vui lòng chọn một bàn để bắt đầu gọi món",
    "order_empty_cart": "Chưa có món nào trong đơn hàng",
    "order_add_item_hint": "Bấm vào món ăn trong thực đơn để thêm vào đơn",
    "order_cart_title": "Chi tiết hoá đơn",
    "order_cart_table": "Bàn",
    "order_item_name": "Tên món",
    "order_item_qty": "SL",
    "order_item_price": "Thành tiền",
    "order_subtotal": "Tạm tính",
    "order_discount": "Giảm giá",
    "order_total": "Tổng thanh toán",
    "order_btn_save": "Lưu / Báo bếp",
    "order_btn_checkout": "Thanh toán ngay",
    "order_btn_cancel": "Huỷ đơn",
    "order_confirm_cancel": "Bạn có chắc chắn muốn huỷ toàn bộ đơn hàng của {table_name} không?",
    "checkout_title": "Thanh toán đơn hàng",
    "checkout_payment_method": "Phương thức thanh toán",
    "checkout_method_cash": "Tiền mặt",
    "checkout_method_qr": "Chuyển khoản (VietQR)",
    "checkout_customer_pay": "Tiền khách đưa",
    "checkout_change": "Tiền thối lại",
    "checkout_success": "Thanh toán thành công! Bàn đã được chuyển về trạng thái trống.",
}


def t(key: str, **kwargs: object) -> str:
    """Lấy chuỗi hiển thị theo mã khoá, hỗ trợ định dạng tham số."""
    template = STRINGS.get(key, key)
    if kwargs:
        return template.format(**kwargs)
    return template


def format_currency(amount: int | float) -> str:
    """Định dạng số tiền theo chuẩn VNĐ: 35.000 đ."""
    return f"{int(amount):,} đ".replace(",", ".")
