"""Model bảng tables — bàn phục vụ."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.core.db import Base

if TYPE_CHECKING:
    from api.models.order import Order


class CafeTable(Base):
    """Bàn trong quán; trạng thái available / occupied / reserved."""

    __tablename__ = "tables"
    __table_args__ = (
        UniqueConstraint("table_number", name="uq_tables_table_number"),
        Index("idx_tables_status", "status"),
        CheckConstraint("status IN ('available','occupied','reserved')", name="chk_tables_status"),
        CheckConstraint("seating_capacity > 0", name="chk_tables_capacity"),
    )

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    table_number: Mapped[str] = mapped_column(String(50), nullable=False)
    area: Mapped[str] = mapped_column(String(50), nullable=False, server_default="Tầng 1")
    seating_capacity: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("4"))
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="available")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("1"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    orders: Mapped[list[Order]] = relationship(back_populates="table")
