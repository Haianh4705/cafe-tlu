"""Kiểm tra ORM khớp với docs/erd.md và db/schema.sql.

Các test này không cần MySQL: chỉ đọc metadata và compile DDL theo dialect MySQL.
"""

from sqlalchemy.dialects import mysql
from sqlalchemy.schema import CreateTable

import api.models  # noqa: F401  (đăng ký toàn bộ model vào Base.metadata)
from api.core.db import Base

EXPECTED_TABLES = {
    "roles",
    "users",
    "categories",
    "products",
    "tables",
    "orders",
    "order_items",
    "invoices",
    "audit_logs",
}

MONEY_COLUMNS = {
    "products": ("price",),
    "orders": ("total_amount",),
    "order_items": ("unit_price", "subtotal"),
    "invoices": (
        "subtotal_amount",
        "discount_amount",
        "final_amount",
        "paid_amount",
        "change_amount",
    ),
}

FOREIGN_KEYS = {
    ("users", "role_id"): ("roles", "RESTRICT"),
    ("products", "category_id"): ("categories", "RESTRICT"),
    ("orders", "table_id"): ("tables", "RESTRICT"),
    ("orders", "created_by"): ("users", "RESTRICT"),
    ("order_items", "order_id"): ("orders", "CASCADE"),
    ("order_items", "product_id"): ("products", "RESTRICT"),
    ("invoices", "order_id"): ("orders", "RESTRICT"),
    ("invoices", "cashier_id"): ("users", "RESTRICT"),
    ("audit_logs", "user_id"): ("users", "SET NULL"),
}


def test_models_define_all_nine_tables() -> None:
    assert set(Base.metadata.tables) == EXPECTED_TABLES


def test_money_columns_are_decimal_12_0() -> None:
    for table_name, columns in MONEY_COLUMNS.items():
        table = Base.metadata.tables[table_name]
        for column_name in columns:
            column_type = table.c[column_name].type
            assert column_type.precision == 12, f"{table_name}.{column_name}"
            assert column_type.scale == 0, f"{table_name}.{column_name}"


def test_foreign_key_delete_rules_match_schema() -> None:
    for (table_name, column_name), (target, ondelete) in FOREIGN_KEYS.items():
        foreign_key = next(iter(Base.metadata.tables[table_name].c[column_name].foreign_keys))
        assert foreign_key.column.table.name == target
        assert foreign_key.ondelete == ondelete


def test_generated_columns_are_computed() -> None:
    products = Base.metadata.tables["products"]
    assert products.c["active_name"].computed is not None
    assert "deleted_at IS NULL" in str(products.c["active_name"].computed.sqltext)

    orders = Base.metadata.tables["orders"]
    assert orders.c["open_table_id"].computed is not None
    assert "pending" in str(orders.c["open_table_id"].computed.sqltext)
    assert "serving" in str(orders.c["open_table_id"].computed.sqltext)


def test_unique_constraints_and_indexes_match_schema() -> None:
    expected_unique = {
        "roles": "uq_roles_name",
        "users": "uq_users_username",
        "categories": "uq_categories_name",
        "products": "uq_products_active_name",
        "tables": "uq_tables_table_number",
        "orders": "uq_orders_order_code",
        "invoices": "uq_invoices_order_id",
    }
    for table_name, constraint_name in expected_unique.items():
        names = {c.name for c in Base.metadata.tables[table_name].constraints}
        assert constraint_name in names

    orders = Base.metadata.tables["orders"]
    assert "uq_orders_open_table" in {c.name for c in orders.constraints}
    assert {"idx_orders_status_created_at", "idx_orders_created_at"} <= {
        i.name for i in orders.indexes
    }

    audit_logs = Base.metadata.tables["audit_logs"]
    assert "idx_audit_logs_entity" in {i.name for i in audit_logs.indexes}


def test_models_compile_to_mysql_ddl() -> None:
    dialect = mysql.dialect()
    for table in Base.metadata.sorted_tables:
        ddl = str(CreateTable(table).compile(dialect=dialect))
        assert f"CREATE TABLE {table.name}" in ddl
