"""Client HTTP duy nhất trong tầng giao diện để giao tiếp với FastAPI backend.

Tuân thủ:
- WORKFLOW.md mục 4.1 & 10: GUI không nối DB, chỉ đi qua ApiClient.
- docs/api-contract.md: Chuẩn hóa toàn bộ 23 endpoint và xử lý mã lỗi JSON.
- Response format chuẩn: {"data": ..., "meta": ..., "error": ...}
"""

import logging
import os
from typing import Any

import requests

logger = logging.getLogger(__name__)


class ApiClientError(Exception):
    """Lỗi sinh ra khi gọi API thất bại."""

    def __init__(self, code: str, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}


class ApiClient:
    """Lớp quản lý các yêu cầu HTTP từ giao diện tới Backend."""

    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = (
            base_url or os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api/v1")
        ).rstrip("/")
        self.access_token: str | None = None
        self.refresh_token: str | None = None
        self._session = requests.Session()

    def set_tokens(self, access_token: str, refresh_token: str | None = None) -> None:
        """Lưu token xác thực sau khi đăng nhập thành công."""
        self.access_token = access_token
        self.refresh_token = refresh_token

    def clear_tokens(self) -> None:
        """Xoá token khi đăng xuất."""
        self.access_token = None
        self.refresh_token = None

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        timeout: float = 10.0,
    ) -> Any:
        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            response = self._session.request(
                method=method,
                url=url,
                headers=self._headers(),
                params=params,
                json=json_data,
                timeout=timeout,
            )
        except requests.exceptions.RequestException as exc:
            logger.error("Lỗi kết nối mạng tới %s: %s", url, exc)
            raise ApiClientError(
                code="NETWORK_ERROR",
                message="Không thể kết nối đến máy chủ API. Vui lòng kiểm tra lại dịch vụ.",
            ) from exc

        try:
            body = response.json()
        except ValueError:
            body = {}

        if not response.ok:
            error_data = body.get("error", {})
            code = error_data.get("code", f"HTTP_{response.status_code}")
            message = error_data.get("message", "Đã có lỗi xảy ra từ máy chủ.")
            details = error_data.get("details", {})
            raise ApiClientError(code=code, message=message, details=details)

        return body.get("data")

    # ------------------------------------------------------------------
    # 1. Xác thực & Tài khoản
    # ------------------------------------------------------------------
    def login(self, username: str, password: str) -> dict[str, Any]:
        """POST /auth/login - Đăng nhập lấy access_token."""
        data = self._request(
            "POST", "/auth/login", json_data={"username": username, "password": password}
        )
        if isinstance(data, dict):
            self.set_tokens(
                access_token=data.get("access_token", ""),
                refresh_token=data.get("refresh_token"),
            )
        return data

    def logout(self) -> None:
        """POST /auth/logout - Thu hồi token và đăng xuất."""
        try:
            self._request("POST", "/auth/logout")
        finally:
            self.clear_tokens()

    def get_me(self) -> dict[str, Any]:
        """GET /auth/me - Lấy thông tin tài khoản đang đăng nhập."""
        return self._request("GET", "/auth/me")

    # ------------------------------------------------------------------
    # 2. Danh mục & Món ăn (Products & Categories)
    # ------------------------------------------------------------------
    def get_categories(self) -> list[dict[str, Any]]:
        """GET /categories - Lấy danh sách danh mục món."""
        return self._request("GET", "/categories")

    def get_products(
        self,
        search: str | None = None,
        category_id: int | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> list[dict[str, Any]]:
        """GET /products - Tìm kiếm và lọc danh sách món ăn."""
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        if search:
            params["search"] = search
        if category_id is not None:
            params["category_id"] = category_id
        return self._request("GET", "/products", params=params)

    def get_product(self, product_id: int) -> dict[str, Any]:
        """GET /products/{id} - Lấy chi tiết món ăn."""
        return self._request("GET", f"/products/{product_id}")

    def create_product(self, payload: dict[str, Any]) -> dict[str, Any]:
        """POST /products - Thêm món ăn mới (Admin)."""
        return self._request("POST", "/products", json_data=payload)

    def update_product(self, product_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        """PATCH /products/{id} - Cập nhật món ăn (Admin)."""
        return self._request("PATCH", f"/products/{product_id}", json_data=payload)

    def delete_product(self, product_id: int) -> None:
        """DELETE /products/{id} - Xoá mềm món ăn (Admin)."""
        self._request("DELETE", f"/products/{product_id}")

    # ------------------------------------------------------------------
    # 3. Bàn & Đơn hàng (Tables & Orders)
    # ------------------------------------------------------------------
    def get_tables(self) -> list[dict[str, Any]]:
        """GET /tables - Lấy danh sách bàn và trạng thái."""
        return self._request("GET", "/tables")

    def create_order(self, table_id: int) -> dict[str, Any]:
        """POST /orders - Tạo đơn hàng tại bàn."""
        return self._request("POST", "/orders", json_data={"table_id": table_id})

    def get_order(self, order_id: int) -> dict[str, Any]:
        """GET /orders/{id} - Lấy chi tiết đơn hàng."""
        return self._request("GET", f"/orders/{order_id}")

    def add_order_item(
        self, order_id: int, product_id: int, quantity: int = 1, note: str = ""
    ) -> dict[str, Any]:
        """POST /orders/{id}/items - Thêm món vào đơn."""
        return self._request(
            "POST",
            f"/orders/{order_id}/items",
            json_data={"product_id": product_id, "quantity": quantity, "note": note},
        )

    def update_order_item(
        self, order_id: int, item_id: int, quantity: int, note: str = ""
    ) -> dict[str, Any]:
        """PATCH /orders/{id}/items/{item_id} - Sửa số lượng hoặc ghi chú món."""
        return self._request(
            "PATCH",
            f"/orders/{order_id}/items/{item_id}",
            json_data={"quantity": quantity, "note": note},
        )

    def remove_order_item(self, order_id: int, item_id: int) -> None:
        """DELETE /orders/{id}/items/{item_id} - Bỏ món khỏi đơn."""
        self._request("DELETE", f"/orders/{order_id}/items/{item_id}")

    def checkout_order(self, order_id: int, payment_method: str = "cash") -> dict[str, Any]:
        """POST /orders/{id}/checkout - Thanh toán và xuất hoá đơn."""
        return self._request(
            "POST",
            f"/orders/{order_id}/checkout",
            json_data={"payment_method": payment_method},
        )

    # ------------------------------------------------------------------
    # 4. Báo cáo (Reports)
    # ------------------------------------------------------------------
    def get_revenue_report(self, start_date: str, end_date: str) -> dict[str, Any]:
        """GET /reports/revenue - Lấy doanh thu theo khoảng thời gian."""
        return self._request(
            "GET",
            "/reports/revenue",
            params={"start_date": start_date, "end_date": end_date},
        )

    def get_top_products_report(self, limit: int = 10) -> list[dict[str, Any]]:
        """GET /reports/top-products - Lấy danh sách món bán chạy nhất."""
        return self._request("GET", "/reports/top-products", params={"limit": limit})
