from fastapi import Response

from app.core.security import create_access_token, create_refresh_token
from app.db.models.user import User
from app.enums.auth import TokenType


def issue_tokens(user: User) -> tuple[str, str]:
    return create_access_token(user), create_refresh_token(user)

def _set_cookie_token(
    response: Response,
    token_type: TokenType,
    token: str
) -> None:
    response.set_cookie(
        key=token_type+"_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="lax"
    )