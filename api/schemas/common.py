"""Schema response dùng chung theo WORKFLOW.md mục 9.3."""

from typing import Any

from pydantic import BaseModel


class Envelope[T](BaseModel):
    """Bọc mọi response thành công trong `data` + `meta`."""

    data: T
    meta: dict[str, Any] | None = None


class MessageData(BaseModel):
    """Payload cho hành động không trả tài nguyên."""

    message: str
