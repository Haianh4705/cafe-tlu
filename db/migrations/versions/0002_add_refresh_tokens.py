"""Thêm bảng refresh_tokens theo ADR-013 (#69) cho volume MySQL cũ (#78).

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-18
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | Sequence[str] | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_DDL = """CREATE TABLE refresh_tokens (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT, user_id BIGINT UNSIGNED NOT NULL,
    token_hash CHAR(64) NOT NULL, expires_at DATETIME NOT NULL, revoked_at DATETIME NULL,
    replaced_by_id BIGINT UNSIGNED NULL, user_agent VARCHAR(255) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id), UNIQUE KEY uq_refresh_tokens_hash (token_hash),
    KEY idx_refresh_tokens_user (user_id, revoked_at), KEY idx_refresh_tokens_expires (expires_at), KEY idx_refresh_tokens_replaced (replaced_by_id),
    CONSTRAINT fk_refresh_tokens_users FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT fk_refresh_tokens_replaced FOREIGN KEY (replaced_by_id) REFERENCES refresh_tokens (id) ON DELETE SET NULL,
    CONSTRAINT chk_refresh_tokens_expires CHECK (expires_at > created_at),
    CONSTRAINT chk_refresh_tokens_revoked CHECK (revoked_at IS NULL OR revoked_at >= created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"""


def upgrade() -> None:
    """Tạo bảng refresh_tokens nếu volume cũ chưa có (giữ nguyên nếu đã có)."""
    if "refresh_tokens" not in set(sa.inspect(op.get_bind()).get_table_names()):
        op.execute(sa.text(_DDL))


def downgrade() -> None:
    """Gỡ bảng refresh_tokens."""
    op.execute(sa.text("DROP TABLE IF EXISTS refresh_tokens"))
