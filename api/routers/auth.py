"""Endpoint xác thực: login, refresh, logout, me (docs/api-contract.md #2-#5)."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from api.core.db import get_db
from api.core.security import get_current_user
from api.models.user import User
from api.schemas.auth import LoginRequest, LogoutRequest, RefreshRequest, TokenResponse, UserOut
from api.schemas.common import Envelope, MessageData
from api.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


def _client_info(request: Request) -> tuple[str | None, str | None]:
    ip_address = request.client.host if request.client else None
    return ip_address, request.headers.get("user-agent")


def _user_out(user: User) -> UserOut:
    return UserOut(
        id=user.id,
        username=user.username,
        full_name=user.full_name,
        role=user.role.name,
    )


def _token_response(user: User, access_token: str, refresh_token: str) -> TokenResponse:
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=_user_out(user),
    )


@router.post("/login", response_model=Envelope[TokenResponse])
def login(
    payload: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> Envelope[TokenResponse]:
    ip_address, user_agent = _client_info(request)
    user, access_token, refresh_token = auth_service.authenticate(
        db, payload.username, payload.password, ip_address, user_agent
    )
    return Envelope(data=_token_response(user, access_token, refresh_token))


@router.post("/refresh", response_model=Envelope[TokenResponse])
def refresh(
    payload: RefreshRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> Envelope[TokenResponse]:
    _, user_agent = _client_info(request)
    user, access_token, refresh_token = auth_service.refresh(db, payload.refresh_token, user_agent)
    return Envelope(data=_token_response(user, access_token, refresh_token))


@router.post("/logout", response_model=Envelope[MessageData])
def logout(
    payload: LogoutRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Envelope[MessageData]:
    auth_service.logout(db, user, payload.refresh_token)
    return Envelope(data=MessageData(message="Đã đăng xuất"))


@router.get("/me", response_model=Envelope[UserOut])
def me(user: User = Depends(get_current_user)) -> Envelope[UserOut]:
    return Envelope(data=_user_out(user))
