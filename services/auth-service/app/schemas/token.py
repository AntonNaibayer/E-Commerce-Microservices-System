from enums.auth import AuthScheme, TokenType
from pydantic import BaseModel, EmailStr


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: AuthScheme = AuthScheme.BEARER

class BaseTokenPayload(BaseModel):
    sub: str
    exp: int
    iat: int
    token_type: TokenType

class AccessTokenPayload(BaseTokenPayload):
    token_type: TokenType = TokenType.ACCESS
    email: EmailStr 

class RefreshTokenPayload(BaseTokenPayload):
    token_type: TokenType = TokenType.REFRESH
    jti: str