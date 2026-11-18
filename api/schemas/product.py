"""Schema request/response cho /products."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

MAX_PRODUCT_PRICE = 999_999_999_999


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    category_id: int = Field(gt=0)
    price: int = Field(ge=0, le=MAX_PRODUCT_PRICE)
    unit: str = Field(default="ly", min_length=1, max_length=20)
    image_url: str | None = Field(default=None, max_length=255)
    is_available: bool = True


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    category_id: int | None = Field(default=None, gt=0)
    price: int | None = Field(default=None, ge=0, le=MAX_PRODUCT_PRICE)
    unit: str | None = Field(default=None, min_length=1, max_length=20)
    image_url: str | None = Field(default=None, max_length=255)
    is_available: bool | None = None

    @model_validator(mode="before")
    @classmethod
    def reject_null_required_fields(cls, values: Any) -> Any:
        """PATCH allows omission but rejects null for non-nullable product columns."""
        if isinstance(values, dict):
            non_nullable_fields = {"name", "category_id", "price", "unit", "is_available"}
            invalid_fields = [
                name
                for name, value in values.items()
                if name in non_nullable_fields and value is None
            ]
            if invalid_fields:
                raise ValueError(f"Trường không được null: {', '.join(invalid_fields)}")
        return values


class ProductOut(BaseModel):
    id: int
    name: str
    category_id: int
    category: str
    price: int
    unit: str
    image_url: str | None
    is_available: bool
