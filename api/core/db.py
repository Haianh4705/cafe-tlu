"""Khởi tạo SQLAlchemy engine, sessionmaker và dependency get_db.

Tuân thủ:
- WORKFLOW.md mục 8 & 15: Connection pool, utf8mb4.
- Issue #20: Cung cấp get_db và hàm kiểm tra kết nối DB cho /health.
"""

import logging
from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from api.core.config import settings

logger = logging.getLogger(__name__)

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=(settings.APP_ENV == "dev" and settings.LOG_LEVEL.upper() == "DEBUG"),
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Lớp DeclarativeBase cho tất cả SQLAlchemy models."""

    pass


def get_db() -> Generator[Session, None, None]:
    """Dependency cung cấp Session cơ sở dữ liệu cho mỗi HTTP request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> bool:
    """Kiểm tra kết nối tới MySQL bằng lệnh SELECT 1."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.warning("Không thể kết nối cơ sở dữ liệu MySQL: %s", exc)
        return False
