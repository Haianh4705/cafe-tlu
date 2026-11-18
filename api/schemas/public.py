"""Schema request/response cho Kiosk khách hàng tự gọi món (public)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from api.schemas.category import CategoryOut
from api.schemas.product import ProductOut


class PublicTableOut(BaseModel):
    """Thông tin bàn công khai cho màn Kiosk."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    table_number: str
    area: str
    seating_capacity: int
    status: str


class PublicMenuOut(BaseModel):
    """Gói dữ liệu thực đơn + bàn cho màn Kiosk."""

    categories: list[CategoryOut]
    tables: list[PublicTableOut]
    products: list[ProductOut]


class PublicOrderItemCreate(BaseModel):
    """Mỗi món khách chọn kèm số lượng và ghi chú đường/đá."""

    product_id: int = Field(gt=0)
    quantity: int = Field(ge=1, le=50)
    notes: str | None = Field(default=None, max_length=255)


class PublicOrderCreate(BaseModel):
    """Payload tạo đơn công khai từ Kiosk khách hàng."""

    table_id: int = Field(gt=0)
    notes: str | None = Field(default=None, max_length=500)
    items: list[PublicOrderItemCreate] = Field(min_length=1, max_length=50)


class PublicOrderItemOut(BaseModel):
    """Chi tiết dòng món trong đơn đã tạo."""

    id: int
    product_id: int
    product_name: str
    unit: str
    quantity: int
    unit_price: int
    subtotal: int
    notes: str | None


class PublicOrderOut(BaseModel):
    """Đơn gọi món trả về cho Kiosk kèm payload mã QR thanh toán."""

    id: int
    order_code: str
    table_id: int
    table_number: str
    status: str
    total_amount: int
    notes: str | None
    qr_payload: str
    created_at: datetime
    items: list[PublicOrderItemOut]
