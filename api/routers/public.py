"""Endpoint công khai cho Kiosk khách hàng tự gọi món (docs/api-contract.md #24-#25)."""

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from api.core.db import get_db
from api.models.product import Product
from api.schemas.category import CategoryOut
from api.schemas.common import Envelope
from api.schemas.product import ProductOut
from api.schemas.public import (
    PublicMenuOut,
    PublicOrderCreate,
    PublicOrderItemOut,
    PublicOrderOut,
    PublicTableOut,
)
from api.services import public_kiosk as kiosk_service

router = APIRouter(prefix="/public", tags=["public-kiosk"])


def _to_product_out(product: Product) -> ProductOut:
    return ProductOut(
        id=product.id,
        name=product.name,
        category_id=product.category_id,
        category=product.category.name,
        price=int(product.price),
        unit=product.unit,
        image_url=product.image_url,
        is_available=bool(product.is_available),
    )


@router.get("/menu", response_model=Envelope[PublicMenuOut])
def get_public_menu(db: Session = Depends(get_db)) -> Envelope[PublicMenuOut]:
    """Trả danh mục, danh sách bàn và thực đơn khả dụng cho Kiosk."""
    categories, tables, products = kiosk_service.get_public_menu(db)
    data = PublicMenuOut(
        categories=[CategoryOut.model_validate(cat) for cat in categories],
        tables=[PublicTableOut.model_validate(tbl) for tbl in tables],
        products=[_to_product_out(prod) for prod in products],
    )
    return Envelope(data=data)


@router.post(
    "/orders",
    response_model=Envelope[PublicOrderOut],
    status_code=status.HTTP_201_CREATED,
)
def create_public_order(
    payload: PublicOrderCreate,
    request: Request,
    db: Session = Depends(get_db),
) -> Envelope[PublicOrderOut]:
    """Tiếp nhận đơn tự gọi món từ Kiosk khách hàng và trả về kèm payload QR."""
    ip_address = request.client.host if request.client else None
    order, table, items = kiosk_service.create_public_order(db, payload, ip_address=ip_address)
    total_amount = int(order.total_amount)
    data = PublicOrderOut(
        id=order.id,
        order_code=order.order_code,
        table_id=table.id,
        table_number=table.table_number,
        status=order.status,
        total_amount=total_amount,
        notes=order.notes,
        qr_payload=kiosk_service.build_qr_payload(order.order_code, total_amount),
        created_at=order.created_at,
        items=[
            PublicOrderItemOut(
                id=order_item.id,
                product_id=product.id,
                product_name=product.name,
                unit=product.unit,
                quantity=order_item.quantity,
                unit_price=int(order_item.unit_price),
                subtotal=int(order_item.subtotal),
                notes=order_item.notes,
            )
            for order_item, product in items
        ],
    )
    return Envelope(data=data)
