"""Test xác thực: bcrypt/JWT/require_role (không cần DB) và endpoint (cần MySQL)."""

import hashlib
import threading
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest
from fastapi import Depends
from jose import jwt
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from api.core.config import settings
from api.core.security import (
    create_access_token,
    decode_access_token,
    generate_refresh_token,
    hash_password,
    require_role,
    verify_password,
)
from api.main import app
from api.models.audit_log import AuditLog
from api.models.refresh_token import RefreshToken
from api.models.role import Role
from api.models.user import User
from api.services import auth as auth_service
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


def test_refresh_concurrent_only_one_succeeds(engine) -> None:
    """Hai request refresh đồng thời chỉ một thành công; row được khoá khi rotate (#86)."""
    testing_session = sessionmaker(bind=engine, expire_on_commit=False)
    setup = testing_session()
    role = Role(name="staff_concurrent")
    setup.add(role)
    setup.flush()
    user = User(
        username="refresh_concurrent",
        password_hash=hash_password("123456"),
        full_name="Refresh Concurrent",
        role_id=role.id,
    )
    setup.add(user)
    setup.flush()
    raw_token, token_hash = generate_refresh_token()
    issued_at = datetime.now(UTC).replace(tzinfo=None)
    token = RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        created_at=issued_at,
        expires_at=issued_at + timedelta(days=1),
        user_agent="pytest",
    )
    setup.add(token)
    setup.commit()
    user_id, role_id = user.id, role.id
    setup.close()

    barrier = threading.Barrier(2)
    results: list[tuple[str, object]] = []
    lock = threading.Lock()

    def worker() -> None:
        session = testing_session()
        try:
            barrier.wait(timeout=5)
            _, _, new_raw = auth_service.refresh(session, raw_token, "pytest")
            with lock:
                results.append(("ok", new_raw))
        except AppError as exc:
            with lock:
                results.append(("err", exc.status_code))
        except Exception as exc:  # pragma: no cover - lỗi hạ tầng bất ngờ
            with lock:
                results.append(("crash", repr(exc)))
        finally:
            session.close()

    threads = [threading.Thread(target=worker) for _ in range(2)]
    try:
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=15)

        assert [kind for kind, _ in results].count("ok") == 1, results
        assert ("err", 401) in results
        assert all(kind != "crash" for kind, _ in results)
        assert all(not thread.is_alive() for thread in threads)

        check = testing_session()
        rows = check.scalars(
            select(RefreshToken).where(RefreshToken.user_id == user_id).order_by(RefreshToken.id)
        ).all()
        assert len(rows) == 2
        assert sum(1 for row in rows if row.revoked_at is None) == 1
        assert sum(1 for row in rows if row.revoked_at is not None) == 1
        check.close()
    finally:
        cleanup = testing_session()
        for row in cleanup.scalars(
            select(RefreshToken).where(RefreshToken.user_id == user_id)
        ).all():
            cleanup.delete(row)
        cleanup.flush()
        user_row = cleanup.get(User, user_id)
        if user_row is not None:
            cleanup.delete(user_row)
        cleanup.flush()
        role_row = cleanup.get(Role, role_id)
        if role_row is not None:
            cleanup.delete(role_row)
        cleanup.commit()
        cleanup.close()


def test_validation_error_does_not_echo_sensitive_input(client) -> None:
    """422 chỉ trả loc/msg/type, không echo mật khẩu người dùng gửi lên (#86)."""
    secret = "987654321"
    response = client.post(
        LOGIN_URL,
        json={"username": "thungan01", "password": int(secret)},
    )

    assert response.status_code == 422
    assert secret not in response.text
    errors = response.json()["error"]["details"]["errors"]
    assert errors
    assert errors[0]["loc"] == ["body", "password"]
    assert all("input" not in error for error in errors)


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


def test_logout_without_body_revokes_all_sessions(client, staff_user) -> None:
    first = _login(client).json()["data"]
    second = _login(client).json()["data"]

    response = client.post(LOGOUT_URL, headers=_auth_header(first["access_token"]))
    assert response.status_code == 200

    for tokens in (first, second):
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


def test_login_and_refresh_truncate_long_user_agent_to_255(client, staff_user, db_session) -> None:
    headers = {"User-Agent": "A" * 300}

    login_response = client.post(
        LOGIN_URL,
        json={"username": "thungan01", "password": "123456"},
        headers=headers,
    )
    assert login_response.status_code == 200

    tokens = db_session.scalars(select(RefreshToken).order_by(RefreshToken.id)).all()
    assert len(tokens) == 1
    assert tokens[0].user_agent is not None
    assert len(tokens[0].user_agent) == 255

    refresh_response = client.post(
        REFRESH_URL,
        json={"refresh_token": login_response.json()["data"]["refresh_token"]},
        headers=headers,
    )
    assert refresh_response.status_code == 200

    rotated = db_session.scalars(select(RefreshToken).order_by(RefreshToken.id)).all()
    assert len(rotated) == 2
    assert all(token.user_agent is not None and len(token.user_agent) == 255 for token in rotated)
