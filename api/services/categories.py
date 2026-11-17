"""Nghiệp vụ danh mục món."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from api.models.category import Category
from api.schemas.category import CategoryCreate
from shared.error_codes import ErrorCode
from shared.errors import AppError


def list_categories(db: Session) -> list[Category]:
    return list(db.scalars(select(Category).order_by(Category.name)).all())


def create_category(db: Session, payload: CategoryCreate) -> Category:
    if db.scalar(select(Category.id).where(Category.name == payload.name)) is not None:
        raise AppError(
            ErrorCode.CONFLICT,
            "Tên danh mục đã tồn tại",
            409,
            {"field": "name", "value": payload.name},
        )

    category = Category(
        name=payload.name,
        description=payload.description,
        is_active=payload.is_active,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category
