"""Model bảng orders và order_items — đơn gọi món tại bàn."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Computed,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.core.db import Base

if TYPE_CHECKING:
    from api.models.invoice import Invoice
    from api.models.product import Product
    from api.models.table import CafeTable
    from api.models.user import User


class Order(Base):
    """Đơn tại bàn; mỗi bàn chỉ có một đơn đang mở (open_table_id UNIQUE)."""

    __tablename__ = "orders"
    __table_args__ = (
        UniqueConstraint("order_code", name="uq_orders_order_code"),
        UniqueConstraint("open_table_id", name="uq_orders_open_table"),
        Index("idx_orders_table_id", "table_id"),
        Index("idx_orders_created_by", "created_by"),
        Index("idx_orders_status", "status"),
        Index("idx_orders_created_at", "created_at"),
        Index("idx_orders_status_created_at", "status", "created_at"),
        CheckConstraint(
            "status IN ('pending','serving','completed','cancelled')",
            name="chk_orders_status",
        ),
        CheckConstraint("total_amount >= 0", name="chk_orders_total"),
    )

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    order_code: Mapped[str] = mapped_column(String(50), nullable=False)
    table_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("tables.id", ondelete="RESTRICT"), nullable=False
    )
    created_by: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="pending")
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 0), nullable=False, server_default=text("0")
    )
    notes: Mapped[str | None] = mapped_column(Text)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("0"))
    open_table_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True),
        Computed("IF(status IN ('pending','serving'), table_id, NULL)", persisted=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    table: Mapped[CafeTable] = relationship(back_populates="orders")
    creator: Mapped[User] = relationship(back_populates="orders")
    items: Mapped[list[OrderItem]] = relationship(back_populates="order", passive_deletes=True)
    invoice: Mapped[Invoice | None] = relationship(back_populates="order", uselist=False)


class OrderItem(Base):
    """Dòng món trong đơn; unit_price là snapshot giá tại lúc gọi."""

    __tablename__ = "order_items"
    __table_args__ = (
        Index("idx_order_items_order_id", "order_id"),
        Index("idx_order_items_product_id", "product_id"),
        Index("idx_order_items_order_status", "order_id", "status"),
        CheckConstraint("quantity > 0", name="chk_order_items_quantity"),
        CheckConstraint("unit_price >= 0", name="chk_order_items_price"),
        CheckConstraint("subtotal = quantity * unit_price", name="chk_order_items_subtotal"),
        CheckConstraint(
            "status IN ('pending','preparing','served','cancelled')",
            name="chk_order_items_status",
        ),
    )

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("products.id", ondelete="RESTRICT"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 0), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 0), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="pending")
    notes: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    order: Mapped[Order] = relationship(back_populates="items")
    product: Mapped[Product] = relationship(back_populates="order_items")
