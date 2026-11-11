"""Mã lỗi chuẩn dùng chung cho Backend và GUI.

Quy ước:
- Tên hằng số và giá trị là UPPER_SNAKE.
- Không thay đổi mã lỗi sau khi đã phát hành (để bảo đảm tương thích client).
- docs/api-contract.md mục 3 là nguồn tham chiếu.
"""


class ErrorCode:
    """Tập hợp hằng số mã lỗi API theo docs/api-contract.md."""

    # 422 Unprocessable Entity
    VALIDATION_ERROR = "VALIDATION_ERROR"

    # 401 Unauthorized
    UNAUTHENTICATED = "UNAUTHENTICATED"

    # 403 Forbidden
    FORBIDDEN = "FORBIDDEN"

    # 404 Not Found
    NOT_FOUND = "NOT_FOUND"

    # 409 Conflict
    CONFLICT = "CONFLICT"
    PRODUCT_NAME_DUPLICATED = "PRODUCT_NAME_DUPLICATED"
    ORDER_ALREADY_PAID = "ORDER_ALREADY_PAID"
    INSUFFICIENT_STOCK = "INSUFFICIENT_STOCK"

    # 500 / 503 Server Error
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
