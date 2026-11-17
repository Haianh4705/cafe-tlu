"""Model bảng refresh_tokens — refresh token đã phát hành (chỉ lưu hash)."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models.base import Base

if TYPE_CHECKING:
    from api.models.user import User


class RefreshToken(Base):
    """Refresh token đã phát hành; logout/rotate đánh dấu revoked_at."""

    __tablename__ = "refresh_tokens"
    __table_args__ = (
        UniqueConstraint("token_hash", name="uq_refresh_tokens_hash"),
        Index("idx_refresh_tokens_user", "user_id", "revoked_at"),
        Index("idx_refresh_tokens_expires", "expires_at"),
        Index("idx_refresh_tokens_replaced", "replaced_by_id"),
        CheckConstraint("expires_at > created_at", name="chk_refresh_tokens_expires"),
        CheckConstraint(
            "revoked_at IS NULL OR revoked_at >= created_at",
            name="chk_refresh_tokens_revoked",
        ),
    )

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime)
    replaced_by_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("refresh_tokens.id", ondelete="SET NULL")
    )
    user_agent: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    user: Mapped[User] = relationship(back_populates="refresh_tokens")
