"""Nghiệp vụ xác thực: đăng nhập, refresh (rotation) và logout."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from api.core.config import settings
from api.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_refresh_token,
    verify_password,
)
from api.models.audit_log import AuditLog
from api.models.refresh_token import RefreshToken
from api.models.user import User
from shared.error_codes import ErrorCode
from shared.errors import AppError

INVALID_CREDENTIALS_MESSAGE = "Tên đăng nhập hoặc mật khẩu không đúng"
SESSION_EXPIRED_MESSAGE = "Phiên đăng nhập đã hết hạn, vui lòng đăng nhập lại"


def _utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def authenticate(
    db: Session,
    username: str,
    password: str,
    ip_address: str | None,
    user_agent: str | None,
) -> tuple[User, str, str]:
    """Kiểm mật khẩu, phát cặp token; mọi thất bại trả cùng một thông điệp 401."""
    user = db.scalar(select(User).where(User.username == username))
    if user is None or not user.is_active or not verify_password(password, user.password_hash):
        db.add(
            AuditLog(
                user_id=user.id if user else None,
                action="LOGIN_FAILED",
                entity_type="users",
                entity_id=user.id if user else None,
                details={"username": username},
                ip_address=ip_address,
            )
        )
        db.commit()
        raise AppError(ErrorCode.UNAUTHENTICATED, INVALID_CREDENTIALS_MESSAGE, 401)

    access_token = create_access_token(user)
    refresh_token, _ = _issue_refresh_token(db, user.id, user_agent)
    db.commit()
    return user, access_token, refresh_token


def refresh(db: Session, raw_token: str, user_agent: str | None) -> tuple[User, str, str]:
    """Đổi refresh token cũ lấy cặp mới; token cũ bị thu hồi (rotation)."""
    now = _utcnow()
    token = db.scalar(
        select(RefreshToken)
        .where(RefreshToken.token_hash == hash_refresh_token(raw_token))
        .with_for_update()
    )
    if token is None or token.revoked_at is not None or token.expires_at <= now:
        raise AppError(ErrorCode.UNAUTHENTICATED, SESSION_EXPIRED_MESSAGE, 401)

    user = db.get(User, token.user_id)
    if user is None or not user.is_active:
        raise AppError(ErrorCode.UNAUTHENTICATED, SESSION_EXPIRED_MESSAGE, 401)

    access_token = create_access_token(user)
    new_raw_token, new_token = _issue_refresh_token(db, user.id, user_agent, now)
    token.revoked_at = now
    token.replaced_by_id = new_token.id
    db.commit()
    return user, access_token, new_raw_token


def logout(db: Session, user: User, raw_token: str | None) -> None:
    """Thu hồi refresh token hiện tại; không gửi token thì thu hồi mọi phiên của user."""
    now = _utcnow()

    if raw_token is None:
        active_tokens = db.scalars(
            select(RefreshToken)
            .where(
                RefreshToken.user_id == user.id,
                RefreshToken.revoked_at.is_(None),
            )
            .order_by(RefreshToken.id)
            .with_for_update()
        ).all()
        if active_tokens:
            for token in active_tokens:
                token.revoked_at = now
            db.commit()
        return

    token = db.scalar(
        select(RefreshToken)
        .where(
            RefreshToken.token_hash == hash_refresh_token(raw_token),
            RefreshToken.user_id == user.id,
        )
        .with_for_update()
    )
    if token is not None and token.revoked_at is None:
        token.revoked_at = now
        db.commit()


def _issue_refresh_token(
    db: Session,
    user_id: int,
    user_agent: str | None,
    now: datetime | None = None,
) -> tuple[str, RefreshToken]:
    issued_at = now or _utcnow()
    raw_token, token_hash = generate_refresh_token()
    token = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=issued_at + timedelta(days=settings.JWT_REFRESH_DAYS),
        created_at=issued_at,
        user_agent=user_agent,
    )
    db.add(token)
    db.flush()
    return raw_token, token
