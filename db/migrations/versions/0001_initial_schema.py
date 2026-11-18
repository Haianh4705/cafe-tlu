"""Khởi tạo 9 bảng nền tảng theo db/schema.sql (#55)."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_ENG = "ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
_TS = "created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"

_TABLES: tuple[tuple[str, str], ...] = (
    ("roles", f"CREATE TABLE roles (id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT, name VARCHAR(50) NOT NULL, description VARCHAR(255) NULL, {_TS}, PRIMARY KEY (id), UNIQUE KEY uq_roles_name (name)) {_ENG}"),
    ("users", f"CREATE TABLE users (id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT, username VARCHAR(50) NOT NULL, password_hash VARCHAR(255) NOT NULL, full_name VARCHAR(100) NOT NULL, role_id BIGINT UNSIGNED NOT NULL, is_active TINYINT(1) NOT NULL DEFAULT 1, {_TS}, PRIMARY KEY (id), UNIQUE KEY uq_users_username (username), KEY idx_users_role_id (role_id), CONSTRAINT fk_users_roles FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE RESTRICT) {_ENG}"),
    ("categories", f"CREATE TABLE categories (id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT, name VARCHAR(100) NOT NULL, description VARCHAR(255) NULL, is_active TINYINT(1) NOT NULL DEFAULT 1, {_TS}, PRIMARY KEY (id), UNIQUE KEY uq_categories_name (name)) {_ENG}"),
    ("products", f"CREATE TABLE products (id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT, name VARCHAR(150) NOT NULL, category_id BIGINT UNSIGNED NOT NULL, price DECIMAL(12,0) NOT NULL, unit VARCHAR(20) NOT NULL DEFAULT 'ly', image_url VARCHAR(255) NULL, is_available TINYINT(1) NOT NULL DEFAULT 1, deleted_at DATETIME NULL DEFAULT NULL, active_name VARCHAR(150) GENERATED ALWAYS AS (IF(deleted_at IS NULL, name, NULL)) STORED, {_TS}, PRIMARY KEY (id), UNIQUE KEY uq_products_active_name (active_name), KEY idx_products_category_id (category_id), KEY idx_products_is_available (is_available), KEY idx_products_deleted_at (deleted_at), CONSTRAINT fk_products_categories FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE RESTRICT, CONSTRAINT chk_products_price CHECK (price >= 0)) {_ENG}"),
    ("tables", f"CREATE TABLE `tables` (id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT, table_number VARCHAR(50) NOT NULL, area VARCHAR(50) NOT NULL DEFAULT 'Tầng 1', seating_capacity INT NOT NULL DEFAULT 4, status VARCHAR(20) NOT NULL DEFAULT 'available', is_active TINYINT(1) NOT NULL DEFAULT 1, {_TS}, PRIMARY KEY (id), UNIQUE KEY uq_tables_table_number (table_number), KEY idx_tables_status (status), CONSTRAINT chk_tables_status CHECK (status IN ('available','occupied','reserved')), CONSTRAINT chk_tables_capacity CHECK (seating_capacity > 0)) {_ENG}"),
    ("orders", f"CREATE TABLE orders (id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT, order_code VARCHAR(50) NOT NULL, table_id BIGINT UNSIGNED NOT NULL, created_by BIGINT UNSIGNED NOT NULL, status VARCHAR(20) NOT NULL DEFAULT 'pending', total_amount DECIMAL(12,0) NOT NULL DEFAULT 0, notes TEXT NULL, is_deleted TINYINT(1) NOT NULL DEFAULT 0, open_table_id BIGINT UNSIGNED GENERATED ALWAYS AS (IF(status IN ('pending','serving'), table_id, NULL)) STORED, {_TS}, PRIMARY KEY (id), UNIQUE KEY uq_orders_order_code (order_code), UNIQUE KEY uq_orders_open_table (open_table_id), KEY idx_orders_table_id (table_id), KEY idx_orders_created_by (created_by), KEY idx_orders_status (status), KEY idx_orders_created_at (created_at), KEY idx_orders_status_created_at (status, created_at), CONSTRAINT fk_orders_tables FOREIGN KEY (table_id) REFERENCES `tables` (id) ON DELETE RESTRICT, CONSTRAINT fk_orders_users FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE RESTRICT, CONSTRAINT chk_orders_status CHECK (status IN ('pending','serving','completed','cancelled')), CONSTRAINT chk_orders_total CHECK (total_amount >= 0)) {_ENG}"),
    ("order_items", f"CREATE TABLE order_items (id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT, order_id BIGINT UNSIGNED NOT NULL, product_id BIGINT UNSIGNED NOT NULL, quantity INT NOT NULL DEFAULT 1, unit_price DECIMAL(12,0) NOT NULL, subtotal DECIMAL(12,0) NOT NULL, status VARCHAR(20) NOT NULL DEFAULT 'pending', notes VARCHAR(255) NULL, {_TS}, PRIMARY KEY (id), KEY idx_order_items_order_id (order_id), KEY idx_order_items_product_id (product_id), KEY idx_order_items_order_status (order_id, status), CONSTRAINT fk_order_items_orders FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE, CONSTRAINT fk_order_items_products FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE RESTRICT, CONSTRAINT chk_order_items_quantity CHECK (quantity > 0), CONSTRAINT chk_order_items_price CHECK (unit_price >= 0), CONSTRAINT chk_order_items_subtotal CHECK (subtotal = quantity * unit_price), CONSTRAINT chk_order_items_status CHECK (status IN ('pending','preparing','served','cancelled'))) {_ENG}"),
    ("invoices", f"CREATE TABLE invoices (id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT, invoice_code VARCHAR(50) NOT NULL, order_id BIGINT UNSIGNED NOT NULL, cashier_id BIGINT UNSIGNED NOT NULL, subtotal_amount DECIMAL(12,0) NOT NULL, discount_amount DECIMAL(12,0) NOT NULL DEFAULT 0, final_amount DECIMAL(12,0) NOT NULL, paid_amount DECIMAL(12,0) NOT NULL, change_amount DECIMAL(12,0) NOT NULL DEFAULT 0, payment_method VARCHAR(20) NOT NULL DEFAULT 'cash', paid_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, notes TEXT NULL, {_TS}, PRIMARY KEY (id), UNIQUE KEY uq_invoices_invoice_code (invoice_code), UNIQUE KEY uq_invoices_order_id (order_id), KEY idx_invoices_cashier_id (cashier_id), KEY idx_invoices_paid_at (paid_at), KEY idx_invoices_paid_at_order (paid_at, order_id), CONSTRAINT fk_invoices_orders FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE RESTRICT, CONSTRAINT fk_invoices_users FOREIGN KEY (cashier_id) REFERENCES users (id) ON DELETE RESTRICT, CONSTRAINT chk_invoices_discount CHECK (discount_amount >= 0), CONSTRAINT chk_invoices_final CHECK (final_amount = subtotal_amount - discount_amount), CONSTRAINT chk_invoices_paid CHECK (paid_amount >= final_amount), CONSTRAINT chk_invoices_change CHECK (change_amount = paid_amount - final_amount), CONSTRAINT chk_invoices_payment CHECK (payment_method IN ('cash','transfer','card'))) {_ENG}"),
    ("audit_logs", f"CREATE TABLE audit_logs (id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT, user_id BIGINT UNSIGNED NULL, action VARCHAR(50) NOT NULL, entity_type VARCHAR(50) NOT NULL, entity_id BIGINT UNSIGNED NULL, details JSON NULL, ip_address VARCHAR(45) NULL, created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (id), KEY idx_audit_logs_user_id (user_id), KEY idx_audit_logs_action (action), KEY idx_audit_logs_created_at (created_at), KEY idx_audit_logs_entity (entity_type, entity_id), CONSTRAINT fk_audit_logs_users FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL) {_ENG}"),
)


def upgrade() -> None:
    """Tạo các bảng nền tảng còn thiếu mà không đụng bảng đang có dữ liệu."""
    existing = set(sa.inspect(op.get_bind()).get_table_names())
    for table_name, ddl in _TABLES:
        if table_name not in existing:
            op.execute(sa.text(ddl))


def downgrade() -> None:
    """Gỡ 9 bảng nền tảng theo thứ tự ngược khoá ngoại."""
    for table_name, _ in reversed(_TABLES):
        op.execute(sa.text(f"DROP TABLE IF EXISTS `{table_name}`"))
