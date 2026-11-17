"""Schema request/response cho /products."""

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    category_id: int = Field(gt=0)
    price: int = Field(ge=0)
    unit: str = Field(default="ly", min_length=1, max_length=20)
    image_url: str | None = Field(default=None, max_length=255)
    is_available: bool = True


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    category_id: int | None = Field(default=None, gt=0)
    price: int | None = Field(default=None, ge=0)
    unit: str | None = Field(default=None, min_length=1, max_length=20)
    image_url: str | None = Field(default=None, max_length=255)
    is_available: bool | None = None


class ProductOut(BaseModel):
    id: int
    name: str
    category_id: int
    category: str
    price: int
    unit: str
    image_url: str | None
    is_available: bool
