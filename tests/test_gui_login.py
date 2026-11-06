"""Kiểm thử cho logic giao diện màn hình Đăng nhập (LoginView)."""

from gui.api_client import ApiClient, ApiClientError


def test_login_api_client_error_structure() -> None:
    """Kiểm tra mã lỗi và thông báo khi đăng nhập thất bại."""
    client = ApiClient(base_url="http://127.0.0.1:8000/api/v1")
    assert client.base_url == "http://127.0.0.1:8000/api/v1"
    err = ApiClientError(code="UNAUTHENTICATED", message="Sai mật khẩu")
    assert err.code == "UNAUTHENTICATED"
    assert err.message == "Sai mật khẩu"
