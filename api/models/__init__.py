"""SQLAlchemy models cho 9 bảng theo docs/erd.md.

Import toàn bộ model ở đây để Base.metadata nhận đủ bảng trước khi tạo schema
cho test hoặc khi service dùng relationship.
"""

from api.models.audit_log import AuditLog
from api.models.category import Category
from api.models.invoice import Invoice
from api.models.order import Order, OrderItem
from api.models.product import Product
from api.models.role import Role
from api.models.table import CafeTable
from api.models.user import User

__all__ = [
    "AuditLog",
    "CafeTable",
    "Category",
    "Invoice",
    "Order",
    "OrderItem",
    "Product",
    "Role",
    "User",
]
