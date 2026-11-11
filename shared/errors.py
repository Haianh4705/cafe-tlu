"""Định nghĩa exception nghiệp vụ dùng chung.

Tuân thủ WORKFLOW.md mục 7.3:
- Lỗi nghiệp vụ kế thừa AppError, có code + message tiếng Việt thân thiện.
- Không lộ stack trace ra ngoài.
"""

from typing import Any


class AppError(Exception):
    """Exception cơ sở cho mọi lỗi nghiệp vụ trong hệ thống."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
