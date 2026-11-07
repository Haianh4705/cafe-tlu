"""Xử lý đường dẫn tài nguyên tĩnh cho môi trường dev và PyInstaller."""

import os
import sys


def resource_path(relative_path: str) -> str:
    """Lấy đường dẫn tuyệt đối đến tài nguyên tĩnh.

    Hỗ trợ cả môi trường phát triển (dev) lẫn khi đã được đóng gói thành
    file thực thi bằng PyInstaller (sử dụng thư mục tạm _MEIPASS).
    """
    base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base_path, relative_path)
