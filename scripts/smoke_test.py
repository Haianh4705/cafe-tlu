"""Smoke test local flow bàn → gọi món → thanh toán, chưa kiểm tra báo cáo.
Chạy từ repo root với CAFE_TLU_SMOKE_* đã đặt và `python scripts/smoke_test.py`.
"""

import os
import sys
from typing import Any
from urllib.parse import urlparse

import requests


class SmokeTestError(RuntimeError):
    """Lỗi smoke test có thông tin ngắn để xử lý tại chỗ."""


class OrderSmokeTest:
    """Chạy phần API bàn/đơn/thanh toán trên API local và DB test dùng một lần."""

    def __init__(self, session: requests.Session | None = None) -> None:
        self.base_url = os.getenv("CAFE_TLU_SMOKE_API_URL", "http://127.0.0.1:8000/api/v1").rstrip(
            "/"
        )
        self.username = os.getenv("CAFE_TLU_SMOKE_USER", "").strip()
        self.password = os.getenv("CAFE_TLU_SMOKE_PASSWORD", "")
        self.table_id = self._int_env("CAFE_TLU_SMOKE_TABLE_ID")
        self.product_id = self._int_env("CAFE_TLU_SMOKE_PRODUCT_ID")
        self.database_name = os.getenv("CAFE_TLU_SMOKE_DB_NAME", "").strip()
        self.allow_writes = os.getenv("CAFE_TLU_SMOKE_ALLOW_WRITES") == "1"
        self.session = session or requests.Session()
        self.token: str | None = None
        self.order_id: int | None = None

    @staticmethod
    def _int_env(name: str) -> int | None:
        value = os.getenv(name, "").strip()
        try:
            parsed = int(value)
        except ValueError:
            return None
        return parsed if parsed > 0 else None

    def validate_config(self) -> None:
        host = urlparse(self.base_url).hostname
        if host not in {"localhost", "127.0.0.1", "::1"}:
            raise SmokeTestError("Chỉ cho phép ghi dữ liệu vào API local (localhost).")
        if not self.base_url.endswith("/api/v1"):
            raise SmokeTestError("CAFE_TLU_SMOKE_API_URL phải kết thúc bằng /api/v1.")
        if not self.allow_writes or not self.database_name.endswith("_test"):
            raise SmokeTestError(
                "Tác vụ ghi cần CAFE_TLU_SMOKE_ALLOW_WRITES=1 và "
                "CAFE_TLU_SMOKE_DB_NAME kết thúc bằng _test. Hãy xác nhận API cũng dùng DB test."
            )
        if not self.username or not self.password or not self.table_id or not self.product_id:
            raise SmokeTestError(
                "Cần CAFE_TLU_SMOKE_USER, CAFE_TLU_SMOKE_PASSWORD, "
                "CAFE_TLU_SMOKE_TABLE_ID và CAFE_TLU_SMOKE_PRODUCT_ID hợp lệ."
            )

    def request(
        self, method: str, path: str, *, json: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        try:
            response = self.session.request(
                method, f"{self.base_url}/{path.lstrip('/')}", json=json, headers=headers, timeout=8
            )
        except requests.RequestException as exc:
            raise SmokeTestError(f"{method} {path}: không kết nối được API ({exc}).") from exc

        try:
            body = response.json()
        except ValueError:
            body = {}
        if not response.ok:
            error = body.get("error") or {}
            message = error.get("message") or f"HTTP {response.status_code}"
            raise SmokeTestError(f"{method} {path}: {message}")
        return body

    @staticmethod
    def data(response: dict[str, Any]) -> Any:
        return response.get("data")

    def run(self) -> None:
        self.validate_config()
        health_url = self.base_url.removesuffix("/api/v1") + "/health"
        try:
            health = self.session.get(health_url, timeout=5)
        except requests.RequestException as exc:
            raise SmokeTestError(f"GET /health: không kết nối được API ({exc}).") from exc
        try:
            health_data = health.json()
        except ValueError:
            health_data = {}
        if not health.ok or health_data.get("status") != "ok":
            raise SmokeTestError("GET /health chưa sẵn sàng hoặc database đang degraded.")
        print("PASS /health: API và database sẵn sàng")

        login = self.data(
            self.request(
                "POST", "/auth/login", json={"username": self.username, "password": self.password}
            )
        )
        self.token = login.get("access_token") if login else None
        if not self.token or not login.get("user"):
            raise SmokeTestError("Đăng nhập không trả access token.")
        print("PASS đăng nhập")

        tables = self.data(self.request("GET", "/tables")) or []
        table = next((item for item in tables if item["id"] == self.table_id), None)
        if not table or table["status"] != "available" or table["open_order_id"] is not None:
            raise SmokeTestError("Bàn test không tồn tại hoặc chưa trống; chưa tạo đơn.")

        product = self.data(self.request("GET", f"/products/{self.product_id}"))
        if not product or not product.get("is_available"):
            raise SmokeTestError("Món test không tồn tại hoặc đang hết hàng; chưa tạo đơn.")

        order = self.data(self.request("POST", "/orders", json={"table_id": self.table_id}))
        self.order_id = order["id"]
        print(f"PASS tạo đơn #{self.order_id} cho bàn {table['table_number']}")

        order = self.data(
            self.request(
                "POST",
                f"/orders/{self.order_id}/items",
                json={"product_id": self.product_id, "quantity": 1},
            )
        )
        item = next((row for row in order["items"] if row["product_id"] == self.product_id), None)
        if not item or item["unit_price"] != product["price"]:
            raise SmokeTestError("Giá dòng món không khớp giá do server trả về.")
        print("PASS thêm món, giá lấy từ API server")

        order = self.data(
            self.request(
                "PATCH",
                f"/orders/{self.order_id}/items/{item['id']}",
                json={"quantity": 2},
            )
        )
        item = next(row for row in order["items"] if row["id"] == item["id"])
        expected_total = item["unit_price"] * 2
        if item["quantity"] != 2 or item["subtotal"] != expected_total:
            raise SmokeTestError("Sửa số lượng không cập nhật đúng thành tiền.")
        if order["total_amount"] != expected_total:
            raise SmokeTestError("Tổng đơn do server tính không khớp dòng món.")
        print("PASS sửa số lượng và tính lại tổng đơn")

        checkout = self.data(
            self.request(
                "POST",
                f"/orders/{self.order_id}/checkout",
                json={"payment_method": "cash", "paid_amount": expected_total},
            )
        )
        invoice = checkout["invoice"]
        if checkout["order"]["status"] != "completed" or invoice["final_amount"] != expected_total:
            raise SmokeTestError("Thanh toán không chốt đơn hoặc số tiền hoá đơn sai.")
        final_tables = self.data(self.request("GET", "/tables")) or []
        final_table = next((item for item in final_tables if item["id"] == self.table_id), None)
        if not final_table or final_table["status"] != "available":
            raise SmokeTestError("Thanh toán xong nhưng bàn chưa trở về trạng thái trống.")
        print(
            f"PASS checkout {invoice['invoice_code']}: {invoice['final_amount']:,} VND; bàn đã trống"
        )
        print(
            "PARTIAL PASS: luồng bàn → gọi món → thanh toán đạt; báo cáo và nghiệm thu toàn luồng đang chờ #95/#96."
        )


def main() -> int:
    """Chạy kiểm tra có ghi trên DB test; lỗi trả mã khác 0."""
    smoke_test = OrderSmokeTest()
    try:
        smoke_test.run()
    except SmokeTestError as exc:
        print(f"FAIL smoke test: {exc}", file=sys.stderr)
        if smoke_test.order_id:
            print(
                f"Đơn test #{smoke_test.order_id} đã được tạo; hãy dọn DB test trước lần chạy sau.",
                file=sys.stderr,
            )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
