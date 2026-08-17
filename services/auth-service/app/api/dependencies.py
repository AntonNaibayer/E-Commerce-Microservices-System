from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.api.errors import invalid_token_error
from app.db.models.user import User
from app.db.session import SessionDep
from app.services import auth as auth_service
from app.services.auth_exceptions import (
    InvalidTokenError,
    TokenNotFoundError,
    UserNotFoundError,
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False
)

async def get_current_user(
    session: SessionDep,
    access_token: Annotated[str | None, Depends(oauth2_scheme)],
) -> User:
    if access_token is None:
        raise TokenNotFoundError
    try:
        user = await auth_service.get_current_user(session=session, access_token=access_token)
    except (InvalidTokenError, UserNotFoundError):
        raise invalid_token_error

    return user

CurrentUser = Annotated[User, Depends(get_current_user)]