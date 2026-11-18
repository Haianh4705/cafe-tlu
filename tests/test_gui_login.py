"""Kiểm thử logic giao diện màn hình Đăng nhập (LoginView)."""

from typing import Any

import pytest

from gui.api_client import ApiClient, ApiClientError
from gui.i18n import t
from gui.main import MainWindow
from gui.views.login_view import LoginView


def _capture_workers(monkeypatch: Any, view: LoginView) -> list[dict[str, Any]]:
    workers: list[dict[str, Any]] = []

    def start_worker(
        func: Any,
        on_success: Any,
        on_error: Any = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        workers.append(
            {
                "func": func,
                "on_success": on_success,
                "on_error": on_error,
                "args": args,
                "kwargs": kwargs,
            }
        )

    monkeypatch.setattr(view, "start_worker", start_worker)
    return workers


def test_login_api_client_error_structure() -> None:
    """Kiểm tra mã lỗi và thông báo chuẩn hóa của ApiClient."""
    client = ApiClient(base_url="http://127.0.0.1:8000/api/v1")
    assert client.base_url == "http://127.0.0.1:8000/api/v1"
    err = ApiClientError(code="UNAUTHENTICATED", message="Sai mật khẩu")
    assert err.code == "UNAUTHENTICATED"
    assert err.message == "Sai mật khẩu"


def test_login_success_uses_auth_me_as_authoritative_user(qapp: Any, monkeypatch: Any) -> None:
    """Token được lưu và tín hiệu đăng nhập mang danh tính từ GET /auth/me."""
    api = ApiClient()
    me = {"id": 1, "username": "admin", "full_name": "Quản trị viên", "role": "admin"}

    def request(method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        if method == "POST" and path == "/auth/login":
            return {
                "access_token": "access-token",
                "refresh_token": "refresh-token",
                "user": {"username": "stale-user", "role": "staff"},
            }
        assert method == "GET" and path == "/auth/me"
        return me

    monkeypatch.setattr(api, "_request", request)
    view = LoginView(api)
    workers = _capture_workers(monkeypatch, view)
    emitted: list[dict[str, Any]] = []
    view.login_success.connect(emitted.append)
    view._username_input.setText("admin")
    view._password_input.setText("123456")

    view._handle_login()
    login_worker = workers.pop()
    login_response = login_worker["func"](*login_worker["args"], **login_worker["kwargs"])
    assert api.access_token == "access-token"
    assert api.refresh_token == "refresh-token"

    login_worker["on_success"](login_response)
    assert len(workers) == 1
    me_worker = workers.pop()
    assert me_worker["func"] == api.get_me
    me_worker["on_success"](me_worker["func"]())

    assert emitted == [me]
    assert view._login_btn.isEnabled()


def test_login_failure_is_shown_inline(qapp: Any) -> None:
    """Lỗi đăng nhập hiển thị trên form, không dùng hộp thoại modal."""
    view = LoginView(ApiClient())

    view._on_login_failed(ApiClientError("UNAUTHENTICATED", "Đăng nhập thất bại."))

    assert view._error_banner.text() == "Đăng nhập thất bại."
    assert not view._error_banner.isHidden()
    assert view._login_btn.isEnabled()


@pytest.mark.parametrize(
    ("username", "password", "expected"),
    [
        ("   ", "123456", "Vui lòng nhập tên đăng nhập."),
        ("admin", "", "Vui lòng nhập mật khẩu."),
    ],
)
def test_empty_input_does_not_call_login(
    qapp: Any,
    monkeypatch: Any,
    username: str,
    password: str,
    expected: str,
) -> None:
    """Thiếu tên đăng nhập hoặc mật khẩu bị chặn trước khi tạo worker gọi API."""
    api = ApiClient()
    view = LoginView(api)
    workers = _capture_workers(monkeypatch, view)
    view._username_input.setText(username)
    view._password_input.setText(password)

    view._handle_login()

    assert workers == []
    assert api.access_token is None
    assert view._error_banner.text() == expected


def test_loading_disables_form_and_uses_loading_label(qapp: Any, monkeypatch: Any) -> None:
    """Trong khi API chạy, nút và ô nhập bị khoá với nhãn đang đăng nhập."""
    api = ApiClient()
    view = LoginView(api)
    workers = _capture_workers(monkeypatch, view)
    view._username_input.setText("admin")
    view._password_input.setText("123456")

    view._handle_login()

    assert len(workers) == 1
    assert workers[0]["func"] == api.login
    assert workers[0]["kwargs"] == {"username": "admin", "password": "123456"}
    assert not view._login_btn.isEnabled()
    assert not view._username_input.isEnabled()
    assert not view._password_input.isEnabled()
    assert view._login_btn.text() == "Đang đăng nhập..."


def test_expired_session_returns_to_login_form(qapp: Any, monkeypatch: Any) -> None:
    """401 từ /auth/me xoá token, mở lại form và báo phiên hết hạn."""
    api = ApiClient()
    api.set_tokens("expired-access", "refresh-token")
    view = LoginView(api)
    workers = _capture_workers(monkeypatch, view)
    view._set_loading(True)

    view._on_login_success({"user": {"role": "admin"}})
    assert len(workers) == 1
    assert workers[0]["func"] == api.get_me
    workers[0]["on_error"](ApiClientError("UNAUTHENTICATED", "Vui lòng đăng nhập lại"))

    assert api.access_token is None
    assert api.refresh_token is None
    assert view._login_btn.isEnabled()
    assert view._error_banner.text() == "Phiên đã hết hạn, vui lòng đăng nhập lại"
    assert not view._error_banner.isHidden()


def test_logout_success_sends_refresh_token_and_resets_state(qapp: Any, monkeypatch: Any) -> None:
    """Đăng xuất thành công gửi đúng refresh_token trong body, xoá phiên và trở về form đăng nhập."""
    api = ApiClient()
    api.set_tokens(access_token="test-access", refresh_token="test-refresh")

    captured_requests: list[dict[str, Any]] = []

    def fake_request(method: str, path: str, **kwargs: Any) -> Any:
        captured_requests.append({"method": method, "path": path, "kwargs": kwargs})
        return {"message": "Đã đăng xuất"}

    monkeypatch.setattr(api, "_request", fake_request)

    win = MainWindow(api)
    monkeypatch.setattr(win._kiosk_view, "load", lambda: None)
    monkeypatch.setattr(win._dashboard_view, "load", lambda: None)
    win._on_login_success({"id": 1, "username": "admin", "full_name": "Admin", "role": "admin"})

    assert win._root_stack.currentWidget() is win._app_shell
    assert win.current_user is not None
    win._login_view._password_input.setText("secret")

    win._handle_logout()
    assert win._logout_worker is not None
    win._logout_worker.wait(3000)
    qapp.processEvents()

    assert len(captured_requests) == 1
    req = captured_requests[0]
    assert req["method"] == "POST"
    assert req["path"] == "/auth/logout"
    assert req["kwargs"].get("json_data") == {"refresh_token": "test-refresh"}

    assert api.access_token is None
    assert api.refresh_token is None
    assert win.current_user is None
    assert win._root_stack.currentWidget() is win._login_view
    assert win._login_view._password_input.text() == ""
    assert win._logout_btn.isEnabled()
    assert win._logout_btn.text() == t("logout_btn")
    assert not win._login_view._error_banner.isVisible()
    win.close()


def test_logout_network_error_still_clears_session_and_navigates(
    qapp: Any, monkeypatch: Any
) -> None:
    """Khi mất kết nối, đăng xuất vẫn giải phóng phiên cục bộ, đưa về form và báo trạng thái."""
    api = ApiClient()
    api.set_tokens(access_token="test-access", refresh_token="test-refresh")

    def fake_logout() -> None:
        api.clear_tokens()
        raise ApiClientError("NETWORK_ERROR", "Không thể kết nối đến máy chủ API.")

    monkeypatch.setattr(api, "logout", fake_logout)

    win = MainWindow(api)
    monkeypatch.setattr(win._kiosk_view, "load", lambda: None)
    monkeypatch.setattr(win._dashboard_view, "load", lambda: None)
    win._on_login_success(
        {"id": 1, "username": "staff01", "full_name": "Thu ngân", "role": "staff"}
    )

    win._handle_logout()
    assert win._logout_worker is not None
    win._logout_worker.wait(3000)
    qapp.processEvents()

    assert api.access_token is None
    assert api.refresh_token is None
    assert win.current_user is None
    assert win._root_stack.currentWidget() is win._login_view
    assert not win._login_view._error_banner.isHidden()
    assert win._login_view._error_banner.text() == t("logout_server_unreachable")
    assert win._logout_btn.isEnabled()
    assert win._logout_btn.text() == t("logout_btn")
    win.close()


def test_logout_unauthenticated_error_clears_session_and_shows_expired(
    qapp: Any, monkeypatch: Any
) -> None:
    """Khi access token đã hết hạn lúc đăng xuất, vẫn trở về form và thông báo phiên hết hạn."""
    api = ApiClient()
    api.set_tokens(access_token="expired-access", refresh_token="test-refresh")

    def fake_logout() -> None:
        api.clear_tokens()
        raise ApiClientError("UNAUTHENTICATED", "Token đã hết hạn hoặc không hợp lệ")

    monkeypatch.setattr(api, "logout", fake_logout)

    win = MainWindow(api)
    monkeypatch.setattr(win._kiosk_view, "load", lambda: None)
    monkeypatch.setattr(win._dashboard_view, "load", lambda: None)
    win._on_login_success(
        {"id": 1, "username": "staff01", "full_name": "Thu ngân", "role": "staff"}
    )

    win._handle_logout()
    assert win._logout_worker is not None
    win._logout_worker.wait(3000)
    qapp.processEvents()

    assert api.access_token is None
    assert api.refresh_token is None
    assert win.current_user is None
    assert win._root_stack.currentWidget() is win._login_view
    assert not win._login_view._error_banner.isHidden()
    assert win._login_view._error_banner.text() == t("session_expired")
    win.close()


def test_session_expired_in_app_redirects_to_login_and_allows_relogin(
    qapp: Any, monkeypatch: Any
) -> None:
    """Khi phiên hết hạn trong màn nghiệp vụ, ứng dụng tự đưa về login và cho phép đăng nhập lại."""
    api = ApiClient()
    api.set_tokens(access_token="valid-access", refresh_token="valid-refresh")

    win = MainWindow(api)
    monkeypatch.setattr(win._kiosk_view, "load", lambda: None)
    monkeypatch.setattr(win._dashboard_view, "load", lambda: None)
    win._on_login_success(
        {"id": 1, "username": "admin", "full_name": "Quản trị viên", "role": "admin"}
    )

    assert win._root_stack.currentWidget() is win._app_shell

    # Mô phỏng nhận 401 qua on_unauthenticated
    assert api.on_unauthenticated is not None
    api.on_unauthenticated()
    qapp.processEvents()

    assert win._root_stack.currentWidget() is win._login_view
    assert api.access_token is None
    assert api.refresh_token is None
    assert win.current_user is None
    assert not win._login_view._error_banner.isHidden()
    assert win._login_view._error_banner.text() == t("session_expired")

    # Người dùng có thể đăng nhập lại bình thường
    workers = _capture_workers(monkeypatch, win._login_view)
    win._login_view._username_input.setText("admin")
    win._login_view._password_input.setText("123456")

    def fake_login(username: str, password: str) -> dict[str, Any]:
        api.set_tokens("new-access", "new-refresh")
        return {"access_token": "new-access", "refresh_token": "new-refresh"}

    def fake_get_me() -> dict[str, Any]:
        return {"id": 1, "username": "admin", "full_name": "Quản trị viên", "role": "admin"}

    monkeypatch.setattr(api, "login", fake_login)
    monkeypatch.setattr(api, "get_me", fake_get_me)

    win._login_view._handle_login()
    assert len(workers) == 1
    login_w = workers.pop()
    login_res = login_w["func"](*login_w["args"], **login_w["kwargs"])
    login_w["on_success"](login_res)

    assert len(workers) == 1
    me_w = workers.pop()
    me_res = me_w["func"]()
    me_w["on_success"](me_res)
    qapp.processEvents()

    assert win._root_stack.currentWidget() is win._app_shell
    assert win.current_user["username"] == "admin"
    assert api.access_token == "new-access"
    win.close()
