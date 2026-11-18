"""Nghiệp vụ public Kiosk: lấy thực đơn khả dụng và tạo đơn khách tự chọn món."""

import logging
from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from api.models.audit_log import AuditLog
from api.models.category import Category
from api.models.order import Order, OrderItem
from api.models.product import Product
from api.models.role import Role
from api.models.table import CafeTable
from api.models.user import User
from api.schemas.public import PublicOrderCreate
from shared.error_codes import ErrorCode
from shared.errors import AppError

logger = logging.getLogger(__name__)


def build_qr_payload(order_code: str, total_amount: int) -> str:
    """Sinh chuỗi nội dung mã QR thanh toán VietQR theo mã đơn và số tiền."""
    return f"CAFETLU|VIETQR|{order_code}|{total_amount}"


def get_public_menu(db: Session) -> tuple[list[Category], list[CafeTable], list[Product]]:
    """Lấy danh mục đang hoạt động, danh sách bàn và món chưa xoá cho Kiosk."""
    categories = list(
        db.scalars(select(Category).where(Category.is_active.is_(True)).order_by(Category.id)).all()
    )
    tables = list(
        db.scalars(
            select(CafeTable).where(CafeTable.is_active.is_(True)).order_by(CafeTable.id)
        ).all()
    )
    products = list(
        db.scalars(
            select(Product)
            .join(Category, Product.category_id == Category.id)
            .options(selectinload(Product.category))
            .where(Product.deleted_at.is_(None), Category.is_active.is_(True))
            .order_by(Product.category_id, Product.id)
        ).all()
    )
    return categories, tables, products


def _resolve_kiosk_creator_id(db: Session) -> int:
    """Tìm tài khoản staff đang hoạt động (dự phòng bất kỳ user hoạt động) để gắn đơn Kiosk."""
    staff_id = db.scalar(
        select(User.id)
        .join(Role, User.role_id == Role.id)
        .where(User.is_active.is_(True), Role.name == "staff")
        .order_by(User.id)
        .limit(1)
    )
    if staff_id is not None:
        return int(staff_id)

    fallback_id = db.scalar(
        select(User.id).where(User.is_active.is_(True)).order_by(User.id).limit(1)
    )
    if fallback_id is not None:
        return int(fallback_id)

    raise AppError(
        ErrorCode.CONFLICT,
        "Chưa có tài khoản nhân viên hoạt động để tiếp nhận đơn",
        409,
    )


def _generate_order_code(db: Session) -> str:
    """Sinh mã đơn duy nhất theo ngày dạng ORD-YYYYMMDD-XXX."""
    prefix = f"ORD-{datetime.now().strftime('%Y%m%d')}-"
    existing_codes = db.scalars(
        select(Order.order_code).where(Order.order_code.like(f"{prefix}%"))
    ).all()

    max_seq = 0
    for code in existing_codes:
        suffix = code.removeprefix(prefix)
        if suffix.isdigit():
            max_seq = max(max_seq, int(suffix))
    return f"{prefix}{max_seq + 1:03d}"


def create_public_order(
    db: Session,
    payload: PublicOrderCreate,
    ip_address: str | None = None,
) -> tuple[Order, CafeTable, list[tuple[OrderItem, Product]]]:
    """Tạo đơn trạng thái pending từ Kiosk, tính tiền tại server và chuyển bàn sang occupied."""
    table = db.scalar(
        select(CafeTable)
        .where(CafeTable.id == payload.table_id, CafeTable.is_active.is_(True))
        .with_for_update()
    )
    if table is None:
        raise AppError(
            ErrorCode.NOT_FOUND,
            "Không tìm thấy bàn phục vụ",
            404,
            {"field": "table_id", "value": payload.table_id},
        )

    existing_open = db.scalar(
        select(Order.id).where(
            Order.table_id == table.id,
            Order.status.in_(("pending", "serving")),
            Order.is_deleted.is_(False),
        )
    )
    if table.status != "available" or existing_open is not None:
        raise AppError(
            ErrorCode.CONFLICT,
            "Bàn đang có khách hoặc đã đặt trước, vui lòng chọn bàn trống khác",
            409,
            {"field": "table_id", "value": table.id},
        )

    product_ids = {item.product_id for item in payload.items}
    products = db.scalars(
        select(Product)
        .options(selectinload(Product.category))
        .where(Product.id.in_(product_ids), Product.deleted_at.is_(None))
    ).all()
    products_by_id = {prod.id: prod for prod in products}

    total_amount = Decimal(0)
    prepared_items: list[tuple[OrderItem, Product]] = []
    for item in payload.items:
        product = products_by_id.get(item.product_id)
        if product is None or not product.category.is_active:
            raise AppError(
                ErrorCode.NOT_FOUND,
                "Không tìm thấy món trong thực đơn",
                404,
                {"field": "product_id", "value": item.product_id},
            )
        if not product.is_available:
            raise AppError(
                ErrorCode.INSUFFICIENT_STOCK,
                f"Món '{product.name}' hiện đang tạm hết",
                409,
                {"field": "product_id", "value": item.product_id},
            )

        unit_price = Decimal(product.price)
        subtotal = unit_price * item.quantity
        total_amount += subtotal
        clean_notes = item.notes.strip() if item.notes else None
        order_item = OrderItem(
            product_id=product.id,
            quantity=item.quantity,
            unit_price=unit_price,
            subtotal=subtotal,
            status="pending",
            notes=clean_notes or None,
        )
        prepared_items.append((order_item, product))

    creator_id = _resolve_kiosk_creator_id(db)
    order_code = _generate_order_code(db)
    clean_order_note = payload.notes.strip() if payload.notes else ""
    order_notes = f"[Kiosk] {clean_order_note}" if clean_order_note else "[Kiosk khách tự gọi]"

    order = Order(
        order_code=order_code,
        table_id=table.id,
        created_by=creator_id,
        status="pending",
        total_amount=total_amount,
        notes=order_notes,
        is_deleted=False,
    )
    table.status = "occupied"
    db.add(order)
    db.flush()

    for order_item, _ in prepared_items:
        order_item.order_id = order.id
        db.add(order_item)
    db.flush()

    db.add(
        AuditLog(
            user_id=None,
            action="CREATE_PUBLIC_ORDER",
            entity_type="orders",
            entity_id=order.id,
            details={
                "order_code": order.order_code,
                "table_id": table.id,
                "total_amount": int(total_amount),
                "source": "kiosk",
            },
            ip_address=ip_address,
        )
    )

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        logger.warning("Xung đột khi tạo đơn Kiosk tại bàn %s: %s", table.id, exc)
        raise AppError(
            ErrorCode.CONFLICT,
            "Bàn đang có khách hoặc mã đơn bị trùng, vui lòng thử lại",
            409,
            {"field": "table_id", "value": table.id},
        ) from exc

    db.refresh(order)
    for order_item, _ in prepared_items:
        db.refresh(order_item)
    logger.info(
        "Tạo đơn Kiosk %s tại bàn %s (tổng %s đ)",
        order.order_code,
        table.table_number,
        int(total_amount),
    )
    return order, table, prepared_items
