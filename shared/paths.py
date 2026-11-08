"""Xử lý đường dẫn tài nguyên tĩnh cho môi trường dev và PyInstaller."""

import sys
from pathlib import Path


def resource_path(relative_path: str) -> str:
    """Lấy đường dẫn tuyệt đối đến tài nguyên tĩnh.

    Hỗ trợ cả môi trường phát triển (dev) lẫn khi đã được đóng gói thành
    file thực thi bằng PyInstaller (sử dụng thư mục tạm _MEIPASS).
    """
    if hasattr(sys, "_MEIPASS"):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parents[1]
    return str(base_path / relative_path)
