from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import CurrentUser
from app.api.errors import invalid_credentials_error, invalid_token_error
from app.db.session import SessionDep
from app.enums.auth import TokenType
from app.schemas.token import AccessToken
from app.schemas.user import UserCreate, UserResponse
from app.services import auth as auth_services
from app.services.auth_exceptions import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    InvalidTokenError,
    TokenNotFoundError,
    TokenRevokedError,
    UserInactiveError,
)
from app.utils.auth import _set_cookie_token

router = APIRouter(prefix="/auth", tags=["AUTH"])


@router.post("/register", response_model=UserResponse)
async def register_user(
    session: SessionDep,
    user_data: UserCreate,
) -> UserResponse:

    try:
        user = await auth_services.register_user(
            session=session, email=user_data.email, password=user_data.password
        )
    except EmailAlreadyRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Incorrect email or password"
        )

    return UserResponse.model_validate(user)


@router.post("/login", response_model=AccessToken)
async def login_user(
    session: SessionDep,
    response: Response,
    user_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> AccessToken:

    try:
        tokens = await auth_services.authenticate_user(
            session=session,
            email=user_data.username,
            password=user_data.password,
        )
    except (InvalidCredentialsError, UserInactiveError, TokenNotFoundError):
        raise invalid_credentials_error

    _set_cookie_token(
        response=response, token_type=TokenType.REFRESH, token=tokens.refresh_token
    )

    return AccessToken(access_token=tokens.access_token)


@router.post("/refresh", response_model=AccessToken)
async def refresh_access_token(
    session: SessionDep,
    response: Response,
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> AccessToken:
    try:
        tokens = await auth_services.refresh_tokens(
            session=session, refresh_token=refresh_token
        )
    except InvalidTokenError:
        raise invalid_token_error

    _set_cookie_token(
        response=response, token_type=TokenType.REFRESH, token=tokens.refresh_token
    )

    return AccessToken(access_token=tokens.access_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_user(
    session: SessionDep,
    response: Response,
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> None:
    try:
        await auth_services.logout_user(session=session, refresh_token=refresh_token)
    except (InvalidTokenError, TokenRevokedError):
        raise invalid_token_error

    response.delete_cookie(
        key="refresh_token",
    )


@router.get("/me", response_model=UserResponse)
async def get_self_info(
    current_user: CurrentUser,
) -> UserResponse:

    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User blocked"
        )

    return UserResponse.model_validate(current_user)
