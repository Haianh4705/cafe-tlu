"""Nghiệp vụ bàn và đơn gọi món tại bàn (docs/api-contract.md #13-#18)."""

import logging
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from api.models.order import Order, OrderItem
from api.models.product import Product
from api.models.table import CafeTable
from api.models.user import User
from api.schemas.order import OrderItemCreate, OrderItemUpdate
from api.services.public_kiosk import generate_order_code
from shared.error_codes import ErrorCode
from shared.errors import AppError

logger = logging.getLogger(__name__)

OPEN_STATUSES = ("pending", "serving")


def list_tables(db: Session) -> list[tuple[CafeTable, int | None]]:
    """Trả bàn đang hoạt động kèm id đơn mở để GUI khôi phục giỏ hàng."""
    tables = list(
        db.scalars(
            select(CafeTable).where(CafeTable.is_active.is_(True)).order_by(CafeTable.id)
        ).all()
    )
    open_orders = dict(
        db.execute(
            select(Order.table_id, Order.id).where(
                Order.status.in_(OPEN_STATUSES),
                Order.is_deleted.is_(False),
            )
        ).all()
    )
    return [(table, open_orders.get(table.id)) for table in tables]


def create_order(db: Session, table_id: int, user: User) -> Order:
    """Mở đơn mới cho bàn trống; DB chỉ cho mỗi bàn một đơn đang mở."""
    table = db.scalar(
        select(CafeTable)
        .where(CafeTable.id == table_id, CafeTable.is_active.is_(True))
        .with_for_update()
    )
    if table is None:
        raise AppError(
            ErrorCode.NOT_FOUND,
            "Không tìm thấy bàn phục vụ",
            404,
            {"field": "table_id", "value": table_id},
        )

    existing_open = db.scalar(
        select(Order.id).where(
            Order.table_id == table.id,
            Order.status.in_(OPEN_STATUSES),
            Order.is_deleted.is_(False),
        )
    )
    if table.status != "available" or existing_open is not None:
        raise AppError(
            ErrorCode.CONFLICT,
            "Bàn đang có khách hoặc đã đặt trước",
            409,
            {"field": "table_id", "value": table.id},
        )

    order = Order(
        order_code=generate_order_code(db),
        table_id=table.id,
        created_by=user.id,
        status="pending",
        total_amount=Decimal(0),
        is_deleted=False,
    )
    table.status = "occupied"
    db.add(order)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        logger.warning("Xung đột mở đơn tại bàn %s: %s", table.id, exc)
        raise AppError(
            ErrorCode.CONFLICT,
            "Bàn vừa được mở đơn bởi người khác",
            409,
            {"field": "table_id", "value": table.id},
        ) from exc

    db.refresh(order)
    return get_order(db, order.id)


def get_order(db: Session, order_id: int) -> Order:
    """Lấy đơn kèm dòng món và sản phẩm; đơn đã xoá mềm coi như không tồn tại."""
    order = db.scalar(_order_query().where(Order.id == order_id, Order.is_deleted.is_(False)))
    if order is None:
        raise AppError(
            ErrorCode.NOT_FOUND,
            "Không tìm thấy đơn hàng",
            404,
            {"field": "id", "value": order_id},
        )
    return order


def add_item(db: Session, order_id: int, payload: OrderItemCreate) -> Order:
    """Thêm món, gộp số lượng nếu món đã có và tính lại tổng tiền trong cùng transaction."""
    order = _get_open_order_for_update(db, order_id)
    product = db.scalar(
        select(Product)
        .options(selectinload(Product.category))
        .where(Product.id == payload.product_id, Product.deleted_at.is_(None))
    )
    _validate_product(product, payload.product_id)

    item = db.scalar(
        select(OrderItem)
        .where(
            OrderItem.order_id == order.id,
            OrderItem.product_id == product.id,
            OrderItem.status != "cancelled",
        )
        .with_for_update()
    )
    quantity = payload.quantity
    if item is None:
        unit_price = Decimal(product.price)
        item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=quantity,
            unit_price=unit_price,
            subtotal=unit_price * quantity,
            status="pending",
            notes=payload.notes.strip() if payload.notes else None,
        )
        db.add(item)
    else:
        item.quantity += quantity
        item.subtotal = item.unit_price * item.quantity
        if payload.notes is not None:
            item.notes = payload.notes.strip() or None

    _recalculate_total(db, order)
    db.commit()
    return get_order(db, order.id)


def update_item(db: Session, order_id: int, item_id: int, payload: OrderItemUpdate) -> Order:
    """Sửa số lượng/ghi chú của dòng món và tính lại tổng tiền."""
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise AppError(
            ErrorCode.VALIDATION_ERROR,
            "Cần cung cấp quantity hoặc notes",
            400,
            {"field": "quantity"},
        )

    order = _get_open_order_for_update(db, order_id)
    item = _get_item_or_404(db, order.id, item_id, for_update=True)
    if "quantity" in changes:
        if changes["quantity"] is None:
            raise AppError(
                ErrorCode.VALIDATION_ERROR,
                "quantity không được để trống",
                400,
                {"field": "quantity"},
            )
        item.quantity = int(changes["quantity"])
        item.subtotal = item.unit_price * item.quantity
    if "notes" in changes:
        notes = changes["notes"]
        item.notes = notes.strip() if notes else None

    _recalculate_total(db, order)
    db.commit()
    return get_order(db, order.id)


def remove_item(db: Session, order_id: int, item_id: int) -> None:
    """Bỏ món khỏi đơn đang mở và tính lại tổng tiền."""
    order = _get_open_order_for_update(db, order_id)
    item = _get_item_or_404(db, order.id, item_id, for_update=True)
    db.delete(item)
    _recalculate_total(db, order)
    db.commit()


def _order_query():
    return select(Order).options(
        selectinload(Order.table),
        selectinload(Order.items).selectinload(OrderItem.product),
    )


def _get_open_order_for_update(db: Session, order_id: int) -> Order:
    order = db.scalar(
        select(Order).where(Order.id == order_id, Order.is_deleted.is_(False)).with_for_update()
    )
    if order is None:
        raise AppError(
            ErrorCode.NOT_FOUND,
            "Không tìm thấy đơn hàng",
            404,
            {"field": "id", "value": order_id},
        )
    if order.status not in OPEN_STATUSES:
        raise AppError(
            ErrorCode.ORDER_ALREADY_PAID,
            "Đơn đã thanh toán hoặc đã đóng, không thể sửa",
            409,
            {"field": "status", "value": order.status},
        )
    return order


def _get_item_or_404(
    db: Session, order_id: int, item_id: int, *, for_update: bool = False
) -> OrderItem:
    query = select(OrderItem).where(
        OrderItem.id == item_id,
        OrderItem.order_id == order_id,
    )
    if for_update:
        query = query.with_for_update()
    item = db.scalar(query)
    if item is None:
        raise AppError(
            ErrorCode.NOT_FOUND,
            "Không tìm thấy món trong đơn",
            404,
            {"field": "item_id", "value": item_id},
        )
    return item


def _validate_product(product: Product | None, product_id: int) -> None:
    if product is None or product.deleted_at is not None:
        raise AppError(
            ErrorCode.NOT_FOUND,
            "Không tìm thấy món trong thực đơn",
            404,
            {"field": "product_id", "value": product_id},
        )
    if not product.category.is_active:
        raise AppError(
            ErrorCode.NOT_FOUND,
            "Món thuộc danh mục đã ngừng bán",
            404,
            {"field": "product_id", "value": product_id},
        )
    if not product.is_available:
        raise AppError(
            ErrorCode.INSUFFICIENT_STOCK,
            f"Món '{product.name}' hiện đang tạm hết",
            409,
            {"field": "product_id", "value": product_id},
        )


def _recalculate_total(db: Session, order: Order) -> None:
    db.flush()
    total = db.scalar(
        select(func.coalesce(func.sum(OrderItem.subtotal), 0)).where(
            OrderItem.order_id == order.id,
            OrderItem.status != "cancelled",
        )
    )
    order.total_amount = Decimal(total or 0)
