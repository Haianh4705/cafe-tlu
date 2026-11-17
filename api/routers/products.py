"""Endpoint món ăn (docs/api-contract.md #8-#12)."""

from typing import Any

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from api.core.db import get_db
from api.core.security import require_role
from api.models.product import Product
from api.models.user import User
from api.schemas.common import Envelope
from api.schemas.product import ProductCreate, ProductOut, ProductUpdate
from api.services import products as product_service

router = APIRouter(prefix="/products", tags=["products"])
STAFF_ROLES = ("admin", "staff", "barista")


def _product_out(product: Product) -> ProductOut:
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


@router.get("", response_model=Envelope[list[ProductOut]])
def list_products(
    search: str | None = None,
    category_id: int | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _user: User = Depends(require_role(*STAFF_ROLES)),
) -> Envelope[list[ProductOut]]:
    products, total = product_service.list_products(db, search, category_id, page, page_size)
    meta: dict[str, Any] = {
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": (total + page_size - 1) // page_size,
    }
    return Envelope(data=[_product_out(product) for product in products], meta=meta)


@router.get("/{product_id}", response_model=Envelope[ProductOut])
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(require_role(*STAFF_ROLES)),
) -> Envelope[ProductOut]:
    return Envelope(data=_product_out(product_service.get_product(db, product_id)))


@router.post("", response_model=Envelope[ProductOut], status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    _user: User = Depends(require_role("admin")),
) -> Envelope[ProductOut]:
    product = product_service.create_product(db, payload)
    return Envelope(data=_product_out(product))


@router.patch("/{product_id}", response_model=Envelope[ProductOut])
def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    _user: User = Depends(require_role("admin")),
) -> Envelope[ProductOut]:
    product = product_service.update_product(db, product_id, payload)
    return Envelope(data=_product_out(product))


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(require_role("admin")),
) -> Response:
    product_service.soft_delete_product(db, product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
