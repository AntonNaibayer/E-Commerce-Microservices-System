import uuid
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from app.core.config import settings
from app.core.exceptions import InvalidTokenTypeError
from app.db.models.user import User
from app.enums.auth import TokenType
from app.schemas.token import AccessTokenPayload, RefreshTokenPayload

TOKEN_TYPE_FIELD = "token_type"

def hash_password(
    password: str
) -> bytes:
    salt = bcrypt.gensalt(rounds=13)
    return bcrypt.hashpw(
        password=password.encode(),
        salt=salt
    )

def validate_password(
    password: str,
    hashed_password: bytes
) -> bool:
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password
    )

def encode_jwt(
    payload: dict,
    private_key: str = settings.auth_jwt.private_key_text,
    algorithm: str = settings.auth_jwt.ALGORITHM,
    expire_minutes: int = settings.auth_jwt.ACCESS_TOKEN_EXPIRE_MINUTES,
    expire_timedelta: timedelta | None = None
) -> str:
    
    to_encode = payload.copy()
    now = datetime.now(UTC)

    if expire_timedelta is not None:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)

    to_encode.update(
        exp = expire,
        iat = now
    )

    return jwt.encode(
        payload=to_encode,
        key=private_key,
        algorithm=algorithm
    )

def decode_jwt(
    token: str | bytes,
    public_key: str = settings.auth_jwt.public_key_text,
    algorithm: str = settings.auth_jwt.ALGORITHM
) -> dict:
    return jwt.decode(
        jwt=token,
        key=public_key,
        algorithms=[algorithm]
    )

def generate_jti() -> str:
    """Генерирует уникальный идентификатор для JWT (claim 'jti')."""
    return uuid.uuid4().hex

def validate_token_type(
    payload: dict,
    token_type: str
) -> bool:
    current_token_type = payload.get(TOKEN_TYPE_FIELD)
    if current_token_type == token_type:
        return True
    raise InvalidTokenTypeError(
        f"Expected token type {token_type!r}, got {current_token_type!r}"
    )

def create_jwt(
    token_type: TokenType,
    token_data: dict,
    expire_minutes: int = settings.auth_jwt.ACCESS_TOKEN_EXPIRE_MINUTES,
    expire_timedelta: timedelta | None = None
) -> str:
    jwt_payload = {
        TOKEN_TYPE_FIELD: token_type
    }
    jwt_payload.update(token_data)

    return encode_jwt(
        payload=jwt_payload,
        expire_minutes=expire_minutes,
        expire_timedelta=expire_timedelta
    )

def create_access_token(
    user: User
) -> str:
    jwt_payload = {
        "sub": str(user.id),
        "email": user.email
    }

    return create_jwt(
        token_type=TokenType.ACCESS,
        token_data=jwt_payload,
        expire_minutes=settings.auth_jwt.ACCESS_TOKEN_EXPIRE_MINUTES
    )

def create_refresh_token(
    user: User
) -> str:
    jwt_payload = {
        "sub": str(user.id),
        "jti": generate_jti()
    }
    return create_jwt(
        token_type=TokenType.REFRESH,
        token_data=jwt_payload,
        expire_timedelta=timedelta(days = settings.auth_jwt.REFRESH_TOKEN_EXPIRE_DAYS)
    )

def get_access_token_payload(
    token: str | bytes,
    public_key: str = settings.auth_jwt.public_key_text,
    algorithm: str = settings.auth_jwt.ALGORITHM,
) -> AccessTokenPayload:
    raw_payload = decode_jwt(
        token=token,
        public_key=public_key,
        algorithm=algorithm,
    )
    return AccessTokenPayload.model_validate(raw_payload)

def get_refresh_token_payload(
    token: str | bytes,
    public_key: str = settings.auth_jwt.public_key_text,
    algorithm: str = settings.auth_jwt.ALGORITHM,
) -> RefreshTokenPayload:
    raw_payload = decode_jwt(
        token=token,
        public_key=public_key,
        algorithm=algorithm,
    )
    return RefreshTokenPayload.model_validate(raw_payload)
