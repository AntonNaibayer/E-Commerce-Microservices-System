from datetime import UTC, datetime

from pydantic import BaseModel, EmailStr, field_validator

from app.enums.auth import AuthScheme, TokenType


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: AuthScheme = AuthScheme.BEARER

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str

class AccessToken(BaseModel):
    access_token: str
    token_type: AuthScheme = AuthScheme.BEARER

class BaseTokenPayload(BaseModel):
    sub: str
    exp: datetime
    iat: int
    token_type: TokenType

    @field_validator("exp", mode="before")
    @classmethod
    def _parse_exp(cls, value: int | datetime) -> datetime:
        if isinstance(value, int):
            return datetime.fromtimestamp(value, tz=UTC)
        return value

class AccessTokenPayload(BaseTokenPayload):
    token_type: TokenType = TokenType.ACCESS
    email: EmailStr 

class RefreshTokenPayload(BaseTokenPayload):
    token_type: TokenType = TokenType.REFRESH
    jti: str