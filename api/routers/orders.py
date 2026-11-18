"""Endpoint bàn và đơn gọi món tại bàn (docs/api-contract.md #13-#18)."""

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from api.core.db import get_db
from api.core.security import require_role
from api.models.order import Order
from api.models.user import User
from api.schemas.common import Envelope
from api.schemas.order import (
    OrderCreate,
    OrderItemCreate,
    OrderItemOut,
    OrderItemUpdate,
    OrderOut,
    TableOut,
)
from api.services import orders as order_service

router = APIRouter(tags=["tables-orders"])
STAFF_ROLES = ("admin", "staff", "barista")


def _to_order_out(order: Order) -> OrderOut:
    return OrderOut(
        id=order.id,
        order_code=order.order_code,
        table_id=order.table_id,
        table_number=order.table.table_number,
        status=order.status,
        total_amount=int(order.total_amount),
        notes=order.notes,
        created_at=order.created_at,
        items=[
            OrderItemOut(
                id=item.id,
                product_id=item.product_id,
                product_name=item.product.name,
                unit=item.product.unit,
                quantity=item.quantity,
                unit_price=int(item.unit_price),
                subtotal=int(item.subtotal),
                status=item.status,
                notes=item.notes,
            )
            for item in order.items
        ],
    )


@router.get("/tables", response_model=Envelope[list[TableOut]])
def list_tables(
    db: Session = Depends(get_db),
    _user: User = Depends(require_role(*STAFF_ROLES)),
) -> Envelope[list[TableOut]]:
    """Danh sách bàn đang hoạt động kèm id đơn đang mở (nếu có)."""
    data = [
        TableOut(
            id=table.id,
            table_number=table.table_number,
            area=table.area,
            seating_capacity=table.seating_capacity,
            status=table.status,
            open_order_id=open_order_id,
        )
        for table, open_order_id in order_service.list_tables(db)
    ]
    return Envelope(data=data)


@router.post("/orders", response_model=Envelope[OrderOut], status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role(*STAFF_ROLES)),
) -> Envelope[OrderOut]:
    """Mở đơn mới cho bàn đang trống."""
    return Envelope(data=_to_order_out(order_service.create_order(db, payload.table_id, user)))


@router.get("/orders/{order_id}", response_model=Envelope[OrderOut])
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(require_role(*STAFF_ROLES)),
) -> Envelope[OrderOut]:
    """Chi tiết đơn kèm các dòng món."""
    return Envelope(data=_to_order_out(order_service.get_order(db, order_id)))


@router.post(
    "/orders/{order_id}/items",
    response_model=Envelope[OrderOut],
    status_code=status.HTTP_201_CREATED,
)
def add_order_item(
    order_id: int,
    payload: OrderItemCreate,
    db: Session = Depends(get_db),
    _user: User = Depends(require_role(*STAFF_ROLES)),
) -> Envelope[OrderOut]:
    """Thêm món vào đơn; gộp số lượng nếu món đã có."""
    return Envelope(data=_to_order_out(order_service.add_item(db, order_id, payload)))


@router.patch("/orders/{order_id}/items/{item_id}", response_model=Envelope[OrderOut])
def update_order_item(
    order_id: int,
    item_id: int,
    payload: OrderItemUpdate,
    db: Session = Depends(get_db),
    _user: User = Depends(require_role(*STAFF_ROLES)),
) -> Envelope[OrderOut]:
    """Sửa số lượng hoặc ghi chú của một dòng món."""
    return Envelope(data=_to_order_out(order_service.update_item(db, order_id, item_id, payload)))


@router.delete(
    "/orders/{order_id}/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_order_item(
    order_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(require_role(*STAFF_ROLES)),
) -> Response:
    """Bỏ món khỏi đơn đang mở."""
    order_service.remove_item(db, order_id, item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
