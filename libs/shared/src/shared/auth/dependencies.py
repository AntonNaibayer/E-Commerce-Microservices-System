from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from shared.auth.enums import UserRole

from .config import settings
from .exceptions import ForbiddenError, InvalidTokenError
from .jwt import decode_access_token
from .schemas import AccessTokenPayload

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

async def get_current_user_payload(
    access_token: Annotated[str | None, Depends(oauth2_scheme)],
) -> AccessTokenPayload:
    if access_token is None:
        raise InvalidTokenError()

    return decode_access_token(
        token=access_token,
        public_key=settings.public_key_text,
        algorithm=settings.ALGORITHM,
    )

CurrentUser = Annotated[AccessTokenPayload, Depends(get_current_user_payload)]

def require_role(*allowed_roles: UserRole):
    def dependency(current_user: CurrentUser) -> CurrentUser:
        if current_user.role not in allowed_roles:
            raise ForbiddenError()

        return current_user

    return dependency

AdminUser = Annotated[
    AccessTokenPayload,
    Depends(require_role(UserRole.ADMIN)),
]
