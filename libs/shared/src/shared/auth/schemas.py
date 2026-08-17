from datetime import UTC, datetime

from pydantic import BaseModel, EmailStr, field_validator

from shared.auth.enums import TokenType, UserRole


class AccessTokenPayload(BaseModel):
    sub: str
    email: EmailStr
    role: UserRole
    exp: datetime
    iat: int
    token_type: TokenType = TokenType.ACCESS

    @field_validator("exp", mode="before")
    @classmethod
    def _parse_exp(cls, value: int | datetime) -> datetime:
        if isinstance(value, int):
            return datetime.fromtimestamp(value, tz=UTC)
        return value