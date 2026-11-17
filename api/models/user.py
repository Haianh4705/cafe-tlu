"""Model bảng users — tài khoản nhân viên."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, UniqueConstraint, func, text
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models.base import Base

if TYPE_CHECKING:
    from api.models.audit_log import AuditLog
    from api.models.invoice import Invoice
    from api.models.order import Order
    from api.models.role import Role


class User(Base):
    """Tài khoản đăng nhập của nhân viên; mật khẩu lưu dưới dạng bcrypt hash."""

    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("username", name="uq_users_username"),
        Index("idx_users_role_id", "role_id"),
    )

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("1"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    role: Mapped[Role] = relationship(back_populates="users")
    orders: Mapped[list[Order]] = relationship(back_populates="creator")
    invoices: Mapped[list[Invoice]] = relationship(back_populates="cashier")
    audit_logs: Mapped[list[AuditLog]] = relationship(back_populates="user")
