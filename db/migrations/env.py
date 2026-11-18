"""Cấu hình môi trường chạy Alembic cho MySQL CafeTLU."""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

import api.models  # noqa: F401  (nạp đủ model vào Base.metadata)
from api.core.config import settings
from api.core.db import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

target_metadata = Base.metadata


def _url() -> str:
    return (
        config.attributes.get("sqlalchemy_url")
        or config.get_main_option("sqlalchemy.url")
        or settings.database_url
    )


def _run_with(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    context.configure(
        url=_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()
elif (shared := config.attributes.get("connection")) is not None:
    _run_with(shared)
else:
    with create_engine(_url(), poolclass=pool.NullPool).connect() as conn:
        _run_with(conn)
