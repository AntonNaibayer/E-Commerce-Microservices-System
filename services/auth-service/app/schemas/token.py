import uuid

from enums.auth import AuthScheme, TokenType
from pydantic import BaseModel, EmailStr


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: AuthScheme = AuthScheme.BEARER

class TokenPayload(BaseModel):
    sub: uuid.UUID | None = None
    email: EmailStr | None = None 
    exp: int  # время истечения токена
    token_type: TokenType
    iat: int | None = None
    jti: str | None = None