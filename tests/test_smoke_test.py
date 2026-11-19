"""Unit tests for the local order/payment smoke test, with HTTP fully mocked."""

from typing import Any

import pytest

from scripts.smoke_test import OrderSmokeTest, SmokeTestError


class FakeResponse:
    def __init__(self, body: dict[str, Any], status_code: int = 200) -> None:
        self.body = body
        self.status_code = status_code
        self.ok = status_code < 400

    def json(self) -> dict[str, Any]:
        return self.body


class FakeSession:
    def __init__(self) -> None:
        self.table_reads = 0
        self.calls: list[tuple[str, str, dict[str, Any] | None]] = []

    def get(self, url: str, **_: Any) -> FakeResponse:
        assert url == "http://127.0.0.1:8000/health"
        return FakeResponse({"status": "ok", "database": "ok"})

    def request(
        self,
        method: str,
        url: str,
        *,
        json: dict[str, Any] | None,
        headers: dict[str, str],
        timeout: int,
    ) -> FakeResponse:
        self.calls.append((method, url, json))
        assert timeout == 8
        if url.endswith("/auth/login"):
            return FakeResponse({"data": {"access_token": "test-token", "user": {"role": "staff"}}})
        assert headers == {"Authorization": "Bearer test-token"}
        if url.endswith("/tables"):
            self.table_reads += 1
            return FakeResponse(
                {
                    "data": [
                        {
                            "id": 1,
                            "table_number": "T01",
                            "status": "available",
                            "open_order_id": None,
                        }
                    ]
                }
            )
        if url.endswith("/products/2"):
            return FakeResponse({"data": {"id": 2, "price": 24000, "is_available": True}})
        if url.endswith("/orders") and method == "POST":
            return FakeResponse({"data": {"id": 3}})
        if url.endswith("/orders/3/items") and method == "POST":
            return FakeResponse(
                {
                    "data": {
                        "items": [{"id": 4, "product_id": 2, "unit_price": 24000}],
                        "total_amount": 24000,
                    }
                }
            )
        if url.endswith("/orders/3/items/4") and method == "PATCH":
            return FakeResponse(
                {
                    "data": {
                        "items": [
                            {
                                "id": 4,
                                "product_id": 2,
                                "unit_price": 24000,
                                "quantity": 2,
                                "subtotal": 48000,
                            }
                        ],
                        "total_amount": 48000,
                    }
                }
            )
        if url.endswith("/orders/3/checkout"):
            return FakeResponse(
                {
                    "data": {
                        "order": {"status": "completed"},
                        "invoice": {"invoice_code": "INV-TEST", "final_amount": 48000},
                    }
                }
            )
        raise AssertionError(f"Unexpected request: {method} {url}")


@pytest.fixture
def smoke_env(monkeypatch: pytest.MonkeyPatch) -> None:
    values = {
        "CAFE_TLU_SMOKE_API_URL": "http://127.0.0.1:8000/api/v1",
        "CAFE_TLU_SMOKE_USER": "staff-test",
        "CAFE_TLU_SMOKE_PASSWORD": "test-only",
        "CAFE_TLU_SMOKE_TABLE_ID": "1",
        "CAFE_TLU_SMOKE_PRODUCT_ID": "2",
        "CAFE_TLU_SMOKE_DB_NAME": "cafe_tlu_test",
        "CAFE_TLU_SMOKE_ALLOW_WRITES": "1",
    }
    for name, value in values.items():
        monkeypatch.setenv(name, value)


def test_order_smoke_checks_flow_without_calling_reports(smoke_env: None) -> None:
    session = FakeSession()

    OrderSmokeTest(session=session).run()

    paths = [url for _, url, _ in session.calls]
    assert session.table_reads == 2
    assert any(url.endswith("/orders/3/checkout") for url in paths)
    assert not any("/reports/" in url for url in paths)


def test_order_smoke_refuses_non_local_api(
    smoke_env: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CAFE_TLU_SMOKE_API_URL", "https://api.example.com/api/v1")

    with pytest.raises(SmokeTestError, match="API local"):
        OrderSmokeTest(session=FakeSession()).run()


def test_order_smoke_requires_test_database_confirmation(
    smoke_env: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CAFE_TLU_SMOKE_DB_NAME", "cafe_tlu")

    with pytest.raises(SmokeTestError, match="kết thúc bằng _test"):
        OrderSmokeTest(session=FakeSession()).run()
