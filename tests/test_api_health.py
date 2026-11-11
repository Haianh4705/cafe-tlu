"""Kiểm thử cho endpoint /health và cơ chế xử lý lỗi chung của FastAPI.

Tuân thủ:
- Issue #19: Kiểm thử GET /health và schema trả về.
- Issue #20: Kiểm thử trạng thái kết nối DB (200 / 503).
"""

from unittest.mock import patch

from fastapi.testclient import TestClient

from api.main import app
from shared.error_codes import ErrorCode
from shared.errors import AppError
from shared.version import __version__

client = TestClient(app)


def test_health_check_endpoint_connected() -> None:
    """Kiểm tra GET /health khi DB kết nối thành công."""
    with patch("api.routers.health.check_db_connection", return_value=True):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["version"] == __version__
        assert data["database"] == "connected"


def test_health_check_endpoint_api_v1_connected() -> None:
    """Kiểm tra GET /api/v1/health khi DB kết nối thành công."""
    with patch("api.routers.health.check_db_connection", return_value=True):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["version"] == __version__
        assert data["database"] == "connected"


def test_health_check_endpoint_db_disconnected() -> None:
    """Kiểm tra GET /health khi DB mất kết nối trả về 503."""
    with patch("api.routers.health.check_db_connection", return_value=False):
        response = client.get("/health")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "degraded"
        assert data["database"] == "disconnected"


def test_app_error_handler_format() -> None:
    """Kiểm tra AppError được bọc đúng định dạng envelope theo WORKFLOW mục 9.3."""

    @app.get("/test-app-error")
    def trigger_app_error() -> None:
        raise AppError(
            code=ErrorCode.PRODUCT_NAME_DUPLICATED,
            message="Tên món đã tồn tại",
            status_code=409,
            details={"field": "name"},
        )

    response = client.get("/test-app-error")
    assert response.status_code == 409
    body = response.json()
    assert "error" in body
    assert body["error"]["code"] == ErrorCode.PRODUCT_NAME_DUPLICATED
    assert body["error"]["message"] == "Tên món đã tồn tại"
    assert body["error"]["details"] == {"field": "name"}


def test_general_exception_handler_does_not_leak_stack_trace() -> None:
    """Kiểm tra lỗi hệ thống 500 không để lộ stack trace ra ngoài."""

    @app.get("/test-unhandled-error")
    def trigger_unhandled_error() -> None:
        raise RuntimeError("Secret DB crash detail")

    safe_client = TestClient(app, raise_server_exceptions=False)
    response = safe_client.get("/test-unhandled-error")
    assert response.status_code == 500
    body = response.json()
    assert "error" in body
    assert body["error"]["code"] == ErrorCode.INTERNAL_SERVER_ERROR
    assert "Secret DB crash detail" not in response.text
