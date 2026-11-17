"""Xác thực và phân quyền: bcrypt, JWT, dependency người dùng hiện tại.

Tuân thủ skill `security` mục 2-3 và docs/api-contract.md #2-#5.
"""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from api.core.config import settings
from api.core.db import get_db
from api.models.user import User
from shared.error_codes import ErrorCode
from shared.errors import AppError

UNAUTHENTICATED_MESSAGE = "Vui lòng đăng nhập lại"

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)
bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """Băm mật khẩu bằng bcrypt cost 12."""
    return password_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """So khớp mật khẩu với hash; hash hỏng coi như sai."""
    try:
        return password_context.verify(password, password_hash)
    except ValueError:
        return False


def create_access_token(user: User) -> str:
    """Tạo access token 30 phút, payload chứa `sub` (user id) và `role`."""
    issued_at = datetime.now(UTC)
    payload = {
        "sub": str(user.id),
        "role": user.role.name,
        "iat": issued_at,
        "exp": issued_at + timedelta(minutes=settings.JWT_EXPIRES_MINUTES),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """Giải mã access token; sai/hết hạn đều thành 401 UNAUTHENTICATED."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError as exc:
        raise AppError(ErrorCode.UNAUTHENTICATED, UNAUTHENTICATED_MESSAGE, 401) from exc

    if not payload.get("sub"):
        raise AppError(ErrorCode.UNAUTHENTICATED, UNAUTHENTICATED_MESSAGE, 401)
    return payload


def generate_refresh_token() -> tuple[str, str]:
    """Sinh refresh token thô và sha256 hex để lưu DB."""
    raw_token = secrets.token_urlsafe(48)
    return raw_token, hash_refresh_token(raw_token)


def hash_refresh_token(raw_token: str) -> str:
    """Băm refresh token bằng sha256 (không lưu token thô)."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Lấy người dùng từ Bearer token; thiếu/sai/khoá đều trả 401."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise AppError(ErrorCode.UNAUTHENTICATED, UNAUTHENTICATED_MESSAGE, 401)

    payload = decode_access_token(credentials.credentials)
    try:
        user_id = int(payload["sub"])
    except (TypeError, ValueError) as exc:
        raise AppError(ErrorCode.UNAUTHENTICATED, UNAUTHENTICATED_MESSAGE, 401) from exc

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise AppError(ErrorCode.UNAUTHENTICATED, UNAUTHENTICATED_MESSAGE, 401)
    return user


def require_role(*allowed_roles: str):
    """Dependency kiểm quyền ở server theo tên role."""

    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role.name not in allowed_roles:
            raise AppError(
                ErrorCode.FORBIDDEN,
                "Bạn không có quyền thực hiện thao tác này",
                403,
            )
        return user

    return dependency
