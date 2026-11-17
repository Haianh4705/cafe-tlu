"""Model bảng invoices — hoá đơn thanh toán (1-1 với orders)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models.base import Base

if TYPE_CHECKING:
    from api.models.order import Order
    from api.models.user import User


class Invoice(Base):
    """Chứng từ thanh toán; sau khi phát hành thì bất biến."""

    __tablename__ = "invoices"
    __table_args__ = (
        UniqueConstraint("invoice_code", name="uq_invoices_invoice_code"),
        UniqueConstraint("order_id", name="uq_invoices_order_id"),
        Index("idx_invoices_cashier_id", "cashier_id"),
        Index("idx_invoices_paid_at", "paid_at"),
        Index("idx_invoices_paid_at_order", "paid_at", "order_id"),
        CheckConstraint("discount_amount >= 0", name="chk_invoices_discount"),
        CheckConstraint(
            "final_amount = subtotal_amount - discount_amount", name="chk_invoices_final"
        ),
        CheckConstraint("paid_amount >= final_amount", name="chk_invoices_paid"),
        CheckConstraint("change_amount = paid_amount - final_amount", name="chk_invoices_change"),
        CheckConstraint(
            "payment_method IN ('cash','transfer','card')", name="chk_invoices_payment"
        ),
    )

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    invoice_code: Mapped[str] = mapped_column(String(50), nullable=False)
    order_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("orders.id", ondelete="RESTRICT"), nullable=False
    )
    cashier_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    subtotal_amount: Mapped[Decimal] = mapped_column(Numeric(12, 0), nullable=False)
    discount_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 0), nullable=False, server_default=text("0")
    )
    final_amount: Mapped[Decimal] = mapped_column(Numeric(12, 0), nullable=False)
    paid_amount: Mapped[Decimal] = mapped_column(Numeric(12, 0), nullable=False)
    change_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 0), nullable=False, server_default=text("0")
    )
    payment_method: Mapped[str] = mapped_column(String(20), nullable=False, server_default="cash")
    paid_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    order: Mapped[Order] = relationship(back_populates="invoice")
    cashier: Mapped[User] = relationship(back_populates="invoices")
