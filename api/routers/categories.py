"""Endpoint danh mục món (docs/api-contract.md #6-#7)."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from api.core.db import get_db
from api.core.security import require_role
from api.models.user import User
from api.schemas.category import CategoryCreate, CategoryOut
from api.schemas.common import Envelope
from api.services import categories as category_service

router = APIRouter(prefix="/categories", tags=["categories"])
STAFF_ROLES = ("admin", "staff", "barista")


@router.get("", response_model=Envelope[list[CategoryOut]])
def list_categories(
    db: Session = Depends(get_db),
    _user: User = Depends(require_role(*STAFF_ROLES)),
) -> Envelope[list[CategoryOut]]:
    categories = category_service.list_categories(db)
    return Envelope(data=[CategoryOut.model_validate(category) for category in categories])


@router.post(
    "",
    response_model=Envelope[CategoryOut],
    status_code=status.HTTP_201_CREATED,
)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    _user: User = Depends(require_role("admin")),
) -> Envelope[CategoryOut]:
    category = category_service.create_category(db, payload)
    return Envelope(data=CategoryOut.model_validate(category))
