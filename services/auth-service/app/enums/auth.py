from enum import StrEnum


class AuthScheme(StrEnum):
    BEARER = "Bearer"


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"