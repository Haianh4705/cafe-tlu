"""Smoke test DDL + seed + verify_seed.sql và chốt chặn MySQL trên CI (#85)."""

from pathlib import Path

import pymysql
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.core.config import settings
from api.core.db import get_db
from api.main import app
from tests.conftest import skip_or_fail_db

DB_DIR = Path(__file__).resolve().parent.parent / "db"
SEED_DB = "cafe_tlu_seed_test"


def _exec_fetch_last(conn, sql: str) -> list[tuple]:
    rows: list[tuple] = []
    with conn.cursor() as cur:
        cur.execute(sql)
        while True:
            if cur.description is not None:
                rows = list(cur.fetchall())
            if not cur.nextset():
                break
    return rows


def test_skip_or_fail_db_fails_on_ci_and_skips_locally(monkeypatch) -> None:
    monkeypatch.setenv("CI", "true")
    with pytest.raises(pytest.fail.Exception):
        skip_or_fail_db("mất kết nối DB")

    monkeypatch.delenv("CI", raising=False)
    with pytest.raises(pytest.skip.Exception):
        skip_or_fail_db("mất kết nối DB")


def test_schema_and_seed_sql_invariants_and_auth_smoke() -> None:
    if not settings.DB_NAME.endswith("_test"):
        skip_or_fail_db("DB_NAME phải kết thúc bằng _test để chạy smoke seed")

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
    except Exception as exc:
        skip_or_fail_db(f"MySQL không khả dụng cho smoke seed ({exc})")

    schema_sql = (DB_DIR / "schema.sql").read_text(encoding="utf-8")
    seed_sql = (DB_DIR / "seed.sql").read_text(encoding="utf-8")
    verify_sql = (DB_DIR / "verify_seed.sql").read_text(encoding="utf-8")
    seed_url = (
        f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}/{SEED_DB}?charset=utf8mb4"
    )

    eng = None
    try:
        _exec_fetch_last(
            conn,
            f"DROP DATABASE IF EXISTS `{SEED_DB}`; "
            f"CREATE DATABASE `{SEED_DB}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; "
            f"USE `{SEED_DB}`;",
        )
        _exec_fetch_last(conn, schema_sql)
        _exec_fetch_last(conn, seed_sql)
        _exec_fetch_last(conn, seed_sql)  # nạp lại lần 2 để khẳng định idempotent

        rows = _exec_fetch_last(conn, verify_sql)
        assert len(rows) == 23
        assert [r for r in rows if r[3] != "PASS"] == []
        assert any(r[0] == "bảng refresh_tokens tồn tại = 1" and r[3] == "PASS" for r in rows)

        eng = create_engine(seed_url, pool_pre_ping=True)
        factory = sessionmaker(autocommit=False, autoflush=False, bind=eng)

        def _override_db():
            with factory() as db:
                yield db

        app.dependency_overrides[get_db] = _override_db
        with TestClient(app) as client:
            res = client.post(
                "/api/v1/auth/login",
                json={"username": "thungan01", "password": "123456"},
            )
            assert res.status_code == 200

        # Kiểm tra đảo chiều: sửa lệch tổng tiền và xoá bảng phiên phải bị phát hiện ngay.
        _exec_fetch_last(conn, "UPDATE orders SET total_amount = total_amount + 1 WHERE id = 1")
        bad_rows = _exec_fetch_last(conn, verify_sql)
        assert any(r[0] == "đơn lệch tổng tiền = 0" and r[3] == "FAIL" for r in bad_rows)

        _exec_fetch_last(conn, "DROP TABLE refresh_tokens")
        with pytest.raises(pymysql.err.ProgrammingError):
            _exec_fetch_last(conn, verify_sql)
    finally:
        app.dependency_overrides.clear()
        if eng is not None:
            eng.dispose()
        _exec_fetch_last(conn, f"DROP DATABASE IF EXISTS `{SEED_DB}`")
        conn.close()
