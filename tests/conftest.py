"""Fixture DB cho test backend.

Chỉ chạy trên database có tên kết thúc bằng `_test` để tránh xoá nhầm DB dev.
MySQL không khả dụng (máy chưa bật Docker) thì test cần DB tự skip; CI luôn có MySQL.
"""

import os
from typing import NoReturn

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

import api.models  # noqa: F401  (đăng ký toàn bộ model vào Base.metadata)
from api.core.config import settings
from api.core.db import Base, get_db
from api.core.security import hash_password
from api.main import app
from api.models.role import Role
from api.models.user import User


def is_ci_env() -> bool:
    """Trả về True khi đang chạy trong môi trường CI."""
    return os.getenv("CI", "").strip().lower() in {"1", "true", "yes"}


def skip_or_fail_db(reason: str) -> NoReturn:
    """Fail ngay trên CI nếu thiếu DB test; máy local giữ skip để dev không cần Docker."""
    if is_ci_env():
        pytest.fail(reason)
    pytest.skip(reason)


@pytest.fixture(scope="session")
def engine():
    if not settings.DB_NAME.endswith("_test"):
        skip_or_fail_db("DB_NAME phải kết thúc bằng _test để chạy test DB")

    test_engine = create_engine(settings.database_url, pool_pre_ping=True)
    try:
        with test_engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as exc:
        skip_or_fail_db(f"MySQL không khả dụng — chạy `make up` để bật ({exc})")

    Base.metadata.drop_all(test_engine)
    Base.metadata.create_all(test_engine)
    yield test_engine
    Base.metadata.drop_all(test_engine)
    test_engine.dispose()


@pytest.fixture
def db_session(engine) -> Session:
    """Mỗi test trong một transaction lớn, rollback khi kết thúc."""
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection, join_transaction_mode="create_savepoint")()
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db_session: Session):
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db_session: Session) -> User:
    role = Role(name="admin")
    db_session.add(role)
    db_session.flush()

    user = User(
        username="admin",
        password_hash=hash_password("123456"),
        full_name="Quản trị viên",
        role_id=role.id,
    )
    db_session.add(user)
    db_session.flush()
    return user


@pytest.fixture
def staff_user(db_session: Session) -> User:
    role = Role(name="staff")
    db_session.add(role)
    db_session.flush()

    user = User(
        username="thungan01",
        password_hash=hash_password("123456"),
        full_name="Trần Thị B",
        role_id=role.id,
    )
    db_session.add(user)
    db_session.flush()
    return user
