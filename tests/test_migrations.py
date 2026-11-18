"""Kiểm thử nâng cấp schema bằng Alembic cho volume MySQL cũ trước #69 (#78)."""

from pathlib import Path

import pymysql
import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

from api.core.config import settings
from api.core.db import get_db
from api.core.security import hash_password
from api.main import app
from tests.conftest import skip_or_fail_db

UPGRADE_DB = "cafe_tlu_upgrade_test"
SCHEMA_SQL = Path(__file__).resolve().parent.parent / "db" / "schema.sql"
LOGIN = {"username": "thungan01", "password": "123456"}


def _db_url(db_name: str) -> str:
    return (
        f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}/{db_name}?charset=utf8mb4"
    )


def _exec(conn, sql: str) -> None:
    with conn.cursor() as cur:
        cur.execute(sql)
        while cur.nextset():
            pass


def _alembic_cfg() -> Config:
    cfg = Config("alembic.ini")
    cfg.attributes["sqlalchemy_url"] = _db_url(UPGRADE_DB)
    return cfg


@pytest.fixture
def upgrade_db():
    if not settings.DB_NAME.endswith("_test"):
        skip_or_fail_db("DB_NAME phải kết thúc bằng _test để chạy test nâng cấp DB")
    try:
        conn = pymysql.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            charset="utf8mb4",
            autocommit=True,
            client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS,
        )
    except Exception:
        skip_or_fail_db("MySQL không khả dụng — chạy `make up` để bật")
    try:
        _exec(
            conn,
            f"DROP DATABASE IF EXISTS `{UPGRADE_DB}`; "
            f"CREATE DATABASE `{UPGRADE_DB}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
        )
        yield conn
    finally:
        _exec(conn, f"DROP DATABASE IF EXISTS `{UPGRADE_DB}`")
        conn.close()


def test_upgrade_pre_69_volume_preserves_data_and_fixes_login(upgrade_db, monkeypatch) -> None:
    cfg = _alembic_cfg()
    command.upgrade(cfg, "0001")
    _exec(
        upgrade_db,
        f"USE `{UPGRADE_DB}`; DROP TABLE alembic_version; "
        "INSERT INTO roles (id, name) VALUES (2, 'staff'); "
        "INSERT INTO categories (id, name) VALUES (1, 'Cà phê'); "
        "INSERT INTO products (id, name, category_id, price) VALUES (1, 'Bạc xỉu', 1, 29000);",
    )

    eng = create_engine(_db_url(UPGRADE_DB), pool_pre_ping=True)
    factory = sessionmaker(autocommit=False, autoflush=False, bind=eng)

    def _override_db():
        with factory() as db:
            yield db

    try:
        with eng.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO users (id, username, password_hash, full_name, role_id) "
                    "VALUES (2, 'thungan01', :pw, 'Thu Ngân Cũ', 2)"
                ),
                {"pw": hash_password("123456")},
            )

        app.dependency_overrides[get_db] = _override_db
        monkeypatch.setattr("api.core.db.engine", eng)
        with TestClient(app, raise_server_exceptions=False) as client:

            def auth(path: str, **kw):
                return client.post(f"/api/v1/auth/{path}", **kw)

            assert client.get("/health").status_code == 200
            assert auth("login", json=LOGIN).status_code == 500

            command.upgrade(cfg, "head")
            assert "refresh_tokens" in set(inspect(eng).get_table_names())
            with eng.connect() as conn:
                ver = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
                price = conn.execute(text("SELECT price FROM products WHERE id = 1")).scalar()
                assert (ver, price) == ("0002", 29000)

            login_res = auth("login", json=LOGIN)
            assert login_res.status_code == 200
            tok = login_res.json()["data"]["refresh_token"]
            rot = auth("refresh", json={"refresh_token": tok})
            assert rot.status_code == 200
            new_tok = rot.json()["data"]
            hdr = {"Authorization": f"Bearer {new_tok['access_token']}"}
            assert (
                auth(
                    "logout", json={"refresh_token": new_tok["refresh_token"]}, headers=hdr
                ).status_code
                == 200
            )
            assert (
                auth("refresh", json={"refresh_token": new_tok["refresh_token"]}).status_code == 401
            )
    finally:
        app.dependency_overrides.clear()
        eng.dispose()


def test_upgrade_on_fresh_post_69_schema_is_idempotent(upgrade_db) -> None:
    _exec(upgrade_db, f"USE `{UPGRADE_DB}`; " + SCHEMA_SQL.read_text(encoding="utf-8"))
    cfg = _alembic_cfg()
    command.upgrade(cfg, "head")
    command.upgrade(cfg, "head")

    eng = create_engine(_db_url(UPGRADE_DB), pool_pre_ping=True)
    try:
        assert "refresh_tokens" in set(inspect(eng).get_table_names())
        with eng.connect() as conn:
            assert conn.execute(text("SELECT version_num FROM alembic_version")).scalar() == "0002"
    finally:
        eng.dispose()
