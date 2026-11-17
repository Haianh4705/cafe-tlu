"""Model bảng products — món ăn, đồ uống trong thực đơn."""

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
    Numeric,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models.base import Base

if TYPE_CHECKING:
    from api.models.category import Category
    from api.models.order import OrderItem


class Product(Base):
    """Món trong thực đơn; xoá mềm bằng deleted_at, tên unique trong các món chưa xoá."""

    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("active_name", name="uq_products_active_name"),
        Index("idx_products_category_id", "category_id"),
        Index("idx_products_is_available", "is_available"),
        Index("idx_products_deleted_at", "deleted_at"),
        CheckConstraint("price >= 0", name="chk_products_price"),
    )

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    category_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False
    )
    price: Mapped[Decimal] = mapped_column(Numeric(12, 0), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False, server_default="ly")
    image_url: Mapped[str | None] = mapped_column(String(255))
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("1"))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime)
    active_name: Mapped[str | None] = mapped_column(
        String(150),
        Computed("IF(deleted_at IS NULL, name, NULL)", persisted=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    category: Mapped[Category] = relationship(back_populates="products")
    order_items: Mapped[list[OrderItem]] = relationship(back_populates="product")
