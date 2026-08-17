import uuid

from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    decode_jwt,
    get_access_token_payload,
    get_refresh_token_payload,
    hash_password,
    validate_password,
)
from app.db.crud.revoked_token import get_revoked_token_by_jti
from app.db.crud.user import get_user_by_email, get_user_by_id
from app.db.models.revoked_token import RevokedToken
from app.db.models.user import User
from app.enums.auth import TokenType
from app.schemas.token import (
    AccessTokenPayload,
    BaseTokenPayload,
    RefreshTokenPayload,
    TokenPair,
)
from app.services.auth_exceptions import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    InvalidTokenError,
    TokenRevokedError,
    UserInactiveError,
    UserNotFoundError,
)
from app.utils.auth import issue_tokens


def _get_token_payload[T: BaseTokenPayload](
    token: str,
    token_type: TokenType,
    payload_model: type[T]
) -> T:
    try:
        payload = decode_jwt(token=token)

        if payload.get("token_type") != token_type:
            raise InvalidTokenError()
        
        return payload_model.model_validate(payload)

    except (InvalidTokenError, ValidationError) as e:
        raise InvalidTokenError() from e

def get_payload_access_token(access_token: str) -> AccessTokenPayload:
    return _get_token_payload(access_token, TokenType.ACCESS, AccessTokenPayload)

def get_payload_refresh_token(refresh_token: str) -> RefreshTokenPayload:
    return _get_token_payload(refresh_token, TokenType.REFRESH, RefreshTokenPayload)

async def get_user_or_raise(
    session: AsyncSession,
    email: str
) -> User:
    user = await get_user_by_email(session=session, email=email)
    
    if user is None:
        raise InvalidCredentialsError()
    return user

async def get_current_user(
    session: AsyncSession,
    access_token: str,
) -> User:
    payload = get_access_token_payload(token=access_token)

    user = await get_user_by_id(
        session=session,
        user_id=uuid.UUID(payload.sub)
    )

    if user is None:
        raise UserNotFoundError()

    return user

async def register_user(
    session: AsyncSession,
    email: str,
    password: str,
) -> User:

    if await get_user_by_email(session=session, email=email) is not None:
        raise EmailAlreadyRegisteredError()

    hashed_password = hash_password(password=password)

    user = User(email=email, hashed_password=hashed_password)
    
    session.add(user)
    try:
        await session.commit()
        await session.refresh(user)
        return user
    except IntegrityError as e:
        await session.rollback()
        raise EmailAlreadyRegisteredError() from e

async def authenticate_user(
    session: AsyncSession,
    email: str,
    password: str,
) -> TokenPair:
    user = await get_user_or_raise(
        session=session,
        email=email
    )

    if not validate_password(
        password=password,
        hashed_password=user.hashed_password
    ):
        raise InvalidCredentialsError()

    if not user.is_active:
        raise UserInactiveError()

    access_token, refresh_token = issue_tokens(user=user)

    return TokenPair(access_token=access_token, refresh_token=refresh_token)

async def refresh_tokens(
    session: AsyncSession,
    refresh_token: str | None,
) -> TokenPair:

    if refresh_token is None:
        raise InvalidTokenError()

    payload = get_refresh_token_payload(
        token=refresh_token
    )

    revoked_token = await get_revoked_token_by_jti(
        session=session, 
        jti=payload.jti
    )

    if revoked_token is not None:
        raise InvalidTokenError()

    
    user_id = uuid.UUID(payload.sub)

    user = await get_user_by_id(
        session=session, 
        user_id=user_id
    )
    if user is None:
        raise InvalidTokenError()

    access_token, refresh_token = issue_tokens(user)


    new_revoked_token = RevokedToken(
        jti=payload.jti,
        expires_at=payload.exp
    )

    session.add(new_revoked_token)

    try:
        await session.commit()

    except IntegrityError as e:
        await session.rollback()
        raise InvalidTokenError() from e

    return TokenPair(access_token=access_token, refresh_token=refresh_token)

async def logout_user(
    session: AsyncSession,
    refresh_token: str | None,
) -> None:
    if refresh_token is None:
        raise InvalidTokenError()

    payload = get_payload_refresh_token(refresh_token)

    revoked_token = RevokedToken(
        jti=payload.jti,
        expires_at=payload.exp
    )

    session.add(revoked_token)
    try:
        await session.commit()      

            
    except IntegrityError as e:
        await session.rollback()
        raise TokenRevokedError() from e
    
    

