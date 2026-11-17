"""Endpoint kiểm tra trạng thái hoạt động (healthcheck).

Tuân thủ:
- docs/api-contract.md #1: GET /health.
- docs/decisions.md ADR-011: /health là ngoại lệ duy nhất của envelope, trả phẳng.
- Issue #19 & #20: Trả về trạng thái app và kiểm tra kết nối DB.
"""

from typing import Any

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from api.core.db import check_db_connection
from shared.version import __version__

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> Any:
    """Kiểm tra tình trạng sống của ứng dụng và kết nối DB."""
    db_ok = check_db_connection()
    payload = {
        "status": "ok" if db_ok else "degraded",
        "version": __version__,
        "database": "ok" if db_ok else "error",
    }
    if not db_ok:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=payload,
        )
    return payload
