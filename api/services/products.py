"""Nghiệp vụ món ăn: danh sách, chi tiết, tạo/sửa, xoá mềm."""

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from api.models.category import Category
from api.models.product import Product
from api.schemas.product import ProductCreate, ProductUpdate
from shared.error_codes import ErrorCode
from shared.errors import AppError


def list_products(
    db: Session,
    search: str | None,
    category_id: int | None,
    page: int,
    page_size: int,
) -> tuple[list[Product], int]:
    conditions = [Product.deleted_at.is_(None)]
    if search:
        conditions.append(Product.name.contains(search, autoescape=True))
    if category_id is not None:
        conditions.append(Product.category_id == category_id)

    total = db.scalar(select(func.count()).select_from(Product).where(*conditions)) or 0
    products = db.scalars(
        select(Product)
        .options(selectinload(Product.category))
        .where(*conditions)
        .order_by(Product.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return list(products), total


def get_product(db: Session, product_id: int) -> Product:
    product = db.scalar(
        select(Product)
        .options(selectinload(Product.category))
        .where(Product.id == product_id, Product.deleted_at.is_(None))
    )
    if product is None:
        raise AppError(
            ErrorCode.NOT_FOUND,
            "Không tìm thấy món",
            404,
            {"field": "id", "value": product_id},
        )
    return product


def create_product(db: Session, payload: ProductCreate) -> Product:
    _ensure_category_exists(db, payload.category_id)
    _ensure_unique_name(db, payload.name)

    product = Product(**payload.model_dump())
    db.add(product)
    _commit_or_duplicate(db, payload.name)
    db.refresh(product)
    return product


def update_product(db: Session, product_id: int, payload: ProductUpdate) -> Product:
    product = get_product(db, product_id)
    changes = payload.model_dump(exclude_unset=True)

    if "category_id" in changes:
        _ensure_category_exists(db, changes["category_id"])
    if "name" in changes:
        _ensure_unique_name(db, changes["name"], exclude_id=product.id)

    for field, value in changes.items():
        setattr(product, field, value)

    _commit_or_duplicate(db, product.name)
    db.refresh(product)
    return product


def soft_delete_product(db: Session, product_id: int) -> None:
    product = get_product(db, product_id)
    product.deleted_at = datetime.now(UTC).replace(tzinfo=None)
    db.commit()


def _ensure_category_exists(db: Session, category_id: int) -> None:
    if db.get(Category, category_id) is None:
        raise AppError(
            ErrorCode.NOT_FOUND,
            "Không tìm thấy danh mục",
            404,
            {"field": "category_id", "value": category_id},
        )


def _ensure_unique_name(db: Session, name: str, exclude_id: int | None = None) -> None:
    query = select(Product.id).where(Product.name == name, Product.deleted_at.is_(None))
    if exclude_id is not None:
        query = query.where(Product.id != exclude_id)
    if db.scalar(query) is not None:
        raise AppError(
            ErrorCode.PRODUCT_NAME_DUPLICATED,
            "Tên món đã tồn tại",
            409,
            {"field": "name", "value": name},
        )


def _commit_or_duplicate(db: Session, name: str) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise AppError(
            ErrorCode.PRODUCT_NAME_DUPLICATED,
            "Tên món đã tồn tại",
            409,
            {"field": "name", "value": name},
        ) from exc
