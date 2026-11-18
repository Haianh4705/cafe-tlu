"""Schema request/response cho bàn, đơn và thanh toán (docs/api-contract.md #13-#19)."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class TableOut(BaseModel):
    """Bàn phục vụ kèm đơn đang mở (nếu có) để GUI khôi phục giỏ hàng."""

    id: int
    table_number: str
    area: str
    seating_capacity: int
    status: str
    open_order_id: int | None = None


class OrderItemOut(BaseModel):
    """Dòng món trong đơn với giá snapshot tại lúc gọi."""

    id: int
    product_id: int
    product_name: str
    unit: str
    quantity: int
    unit_price: int
    subtotal: int
    status: str
    notes: str | None


class OrderOut(BaseModel):
    """Đơn tại bàn kèm danh sách món và tổng tiền do server tính."""

    id: int
    order_code: str
    table_id: int
    table_number: str
    status: str
    total_amount: int
    notes: str | None
    created_at: datetime
    items: list[OrderItemOut]


class OrderCreate(BaseModel):
    """Mở đơn mới cho một bàn đang trống."""

    table_id: int = Field(gt=0)


class OrderItemCreate(BaseModel):
    """Thêm món vào đơn đang mở."""

    product_id: int = Field(gt=0)
    quantity: int = Field(default=1, ge=1, le=50)
    notes: str | None = Field(default=None, max_length=255)


class OrderItemUpdate(BaseModel):
    """Sửa số lượng và/hoặc ghi chú của một dòng món."""

    quantity: int | None = Field(default=None, ge=1, le=50)
    notes: str | None = Field(default=None, max_length=255)


class CheckoutRequest(BaseModel):
    """Thanh toán đơn: server tự tính lại tiền và tạo hoá đơn."""

    payment_method: Literal["cash", "qr", "transfer", "card"] = "cash"
    paid_amount: int | None = Field(default=None, ge=0)
    discount_amount: int = Field(default=0, ge=0)
    notes: str | None = Field(default=None, max_length=500)


class InvoiceOut(BaseModel):
    """Chứng từ thanh toán do server tạo sau khi checkout thành công."""

    id: int
    invoice_code: str
    order_id: int
    cashier_id: int
    subtotal_amount: int
    discount_amount: int
    final_amount: int
    paid_amount: int
    change_amount: int
    payment_method: str
    paid_at: datetime


class CheckoutOut(BaseModel):
    """Kết quả checkout gồm đơn đã đóng và hoá đơn tương ứng."""

    order: OrderOut
    invoice: InvoiceOut
