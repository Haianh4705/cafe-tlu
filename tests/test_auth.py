"""Test xác thực: bcrypt/JWT/require_role (không cần DB) và endpoint (cần MySQL)."""

import hashlib
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest
from fastapi import Depends
from jose import jwt
from sqlalchemy import select

from api.core.config import settings
from api.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    require_role,
    verify_password,
)
from api.main import app
from api.models.audit_log import AuditLog
from api.models.refresh_token import RefreshToken
from api.models.user import User
from shared.error_codes import ErrorCode
from shared.errors import AppError

LOGIN_URL = "/api/v1/auth/login"
REFRESH_URL = "/api/v1/auth/refresh"
LOGOUT_URL = "/api/v1/auth/logout"
ME_URL = "/api/v1/auth/me"


@app.get("/test/admin-only")
def _admin_only(user: User = Depends(require_role("admin"))) -> dict[str, bool]:
    return {"ok": True}


def _login(client, username: str = "thungan01", password: str = "123456"):
    return client.post(LOGIN_URL, json={"username": username, "password": password})


def _auth_header(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


# ── Không cần DB ────────────────────────────────────────────────────────────


def test_hash_password_uses_bcrypt_cost_12() -> None:
    password_hash = hash_password("123456")
    assert password_hash.startswith("$2b$12$")
    assert password_hash != "123456"
    assert verify_password("123456", password_hash)
    assert not verify_password("sai-mat-khau", password_hash)


def test_verify_password_rejects_broken_hash() -> None:
    assert not verify_password("123456", "khong-phai-bcrypt-hash")


def test_access_token_contains_subject_and_role() -> None:
    fake_user = SimpleNamespace(id=7, role=SimpleNamespace(name="staff"))
    token = create_access_token(fake_user)
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    assert payload["sub"] == "7"
    assert payload["role"] == "staff"
    assert "exp" in payload


def test_expired_access_token_is_rejected() -> None:
    expired_token = jwt.encode(
        {
            "sub": "1",
            "role": "staff",
            "exp": datetime.now(UTC) - timedelta(minutes=1),
        },
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    with pytest.raises(AppError) as exc_info:
        decode_access_token(expired_token)
    assert exc_info.value.status_code == 401
    assert exc_info.value.code == ErrorCode.UNAUTHENTICATED


def test_require_role_allows_admin_and_denies_staff() -> None:
    admin = SimpleNamespace(role=SimpleNamespace(name="admin"))
    staff = SimpleNamespace(role=SimpleNamespace(name="staff"))
    dependency = require_role("admin")

    assert dependency(user=admin) is admin

    with pytest.raises(AppError) as exc_info:
        dependency(user=staff)
    assert exc_info.value.status_code == 403
    assert exc_info.value.code == ErrorCode.FORBIDDEN


# ── Cần MySQL (CI chạy; máy local skip nếu chưa bật Docker) ─────────────────


def test_login_returns_tokens_and_stores_only_hash(client, staff_user, db_session) -> None:
    response = _login(client)
    assert response.status_code == 200

    data = response.json()["data"]
    assert data["token_type"] == "bearer"
    assert data["user"] == {
        "id": staff_user.id,
        "username": "thungan01",
        "full_name": "Trần Thị B",
        "role": "staff",
    }

    stored = db_session.scalar(select(RefreshToken))
    assert stored is not None
    assert stored.token_hash == _sha256(data["refresh_token"])
    assert stored.token_hash != data["refresh_token"]


def test_login_failure_is_identical_for_wrong_password_and_unknown_user(
    client, staff_user, db_session
) -> None:
    wrong_password = _login(client, password="sai-mat-khau")
    unknown_user = _login(client, username="khong-ton-tai")

    assert wrong_password.status_code == 401
    assert unknown_user.status_code == 401
    assert wrong_password.json()["error"] == unknown_user.json()["error"]
    assert wrong_password.json()["error"]["code"] == ErrorCode.UNAUTHENTICATED

    failures = db_session.scalars(select(AuditLog).where(AuditLog.action == "LOGIN_FAILED")).all()
    assert len(failures) == 2


def test_login_rejects_inactive_user(client, staff_user, db_session) -> None:
    staff_user.is_active = False
    db_session.flush()

    response = _login(client)
    assert response.status_code == 401
    assert response.json()["error"]["code"] == ErrorCode.UNAUTHENTICATED


def test_me_returns_current_user(client, staff_user) -> None:
    access_token = _login(client).json()["data"]["access_token"]

    response = client.get(ME_URL, headers=_auth_header(access_token))
    assert response.status_code == 200
    assert response.json()["data"]["username"] == "thungan01"


def test_me_without_token_returns_401(client) -> None:
    response = client.get(ME_URL)
    assert response.status_code == 401
    assert response.json()["error"]["code"] == ErrorCode.UNAUTHENTICATED


def test_refresh_rotates_tokens_and_revokes_old(client, staff_user, db_session) -> None:
    old_refresh_token = _login(client).json()["data"]["refresh_token"]

    rotated = client.post(REFRESH_URL, json={"refresh_token": old_refresh_token})
    assert rotated.status_code == 200
    new_refresh_token = rotated.json()["data"]["refresh_token"]
    assert new_refresh_token != old_refresh_token

    reused = client.post(REFRESH_URL, json={"refresh_token": old_refresh_token})
    assert reused.status_code == 401
    assert reused.json()["error"]["code"] == ErrorCode.UNAUTHENTICATED

    old_row = db_session.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == _sha256(old_refresh_token))
    )
    assert old_row.revoked_at is not None
    assert old_row.replaced_by_id is not None


def test_logout_revokes_refresh_token(client, staff_user) -> None:
    tokens = _login(client).json()["data"]

    response = client.post(
        LOGOUT_URL,
        json={"refresh_token": tokens["refresh_token"]},
        headers=_auth_header(tokens["access_token"]),
    )
    assert response.status_code == 200

    reused = client.post(REFRESH_URL, json={"refresh_token": tokens["refresh_token"]})
    assert reused.status_code == 401


def test_logout_requires_access_token(client, staff_user) -> None:
    tokens = _login(client).json()["data"]

    response = client.post(LOGOUT_URL, json={"refresh_token": tokens["refresh_token"]})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == ErrorCode.UNAUTHENTICATED


def test_staff_forbidden_on_admin_route(client, staff_user) -> None:
    access_token = _login(client).json()["data"]["access_token"]

    response = client.get("/test/admin-only", headers=_auth_header(access_token))
    assert response.status_code == 403
    assert response.json()["error"]["code"] == ErrorCode.FORBIDDEN
