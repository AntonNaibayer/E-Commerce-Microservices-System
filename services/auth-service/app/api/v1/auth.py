import uuid
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import InvalidTokenError
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_jwt,
    hash_password,
    validate_password,
)
from app.db.crud.revoked_token import get_revoked_token_by_jti
from app.db.crud.user import get_user_by_email, get_user_by_id
from app.db.models.revoked_token import RevokedToken
from app.db.models.user import User
from app.db.session import SessionDep
from app.enums.auth import TokenType
from app.schemas.token import (
    AccessToken,
    AccessTokenPayload,
    BaseTokenPayload,
    RefreshTokenPayload,
)
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(
    prefix="/auth",
    tags=["AUTH"]
)


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False
)


def get_token_payload[T: BaseTokenPayload](
    token: str,
    token_type: TokenType,
    payload_model: type[T]
) -> T:
    try:
        payload = decode_jwt(token=token)

        if payload.get("token_type") != token_type:
            raise invalid_token_error
        
        return payload_model.model_validate(payload)

    except (InvalidTokenError, ValidationError) as e:
        raise invalid_token_error



    

def get_payload_access_token(access_token: str) -> AccessTokenPayload:
    return get_token_payload(access_token, TokenType.ACCESS, AccessTokenPayload)


def get_payload_refresh_token(refresh_token: str) -> RefreshTokenPayload:
    return get_token_payload(refresh_token, TokenType.REFRESH, RefreshTokenPayload)



@router.post(
    "/register",
    response_model=UserResponse
)
async def register_user(
    session: SessionDep,
    user_data: UserCreate,
) -> UserResponse:

    if await get_user_by_email(session=session, email=user_data.email) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)

    hashed_password = hash_password(password=user_data.password)

    user = User(email=user_data.email, hashed_password=hashed_password)

    session.add(user)
    try:
        await session.commit()
        await session.refresh(user)
        return UserResponse.model_validate(user)
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user data"
        )


def _set_cookie_refresh(
    response: Response,
    refresh_token: str
) -> None:
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax"
    )


async def get_user_or_raise(
    session: AsyncSession,
    email: str
) -> User:
    user = await get_user_by_email(session=session, email=email)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )
    return user

@router.post(
    "/login",
    response_model=AccessToken
)
async def login_user(
    session: SessionDep, 
    response: Response,
    user_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> AccessToken:

    user = await get_user_or_raise(
        session=session,
        email=user_data.username
    )

    if not validate_password(
        password=user_data.password, hashed_password=user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User is inactive"
        )

    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)

    _set_cookie_refresh(response=response, refresh_token=refresh_token)

    return AccessToken(access_token=access_token)


@router.post(
    "/refresh",
    response_model=AccessToken,
)
async def refresh_access_token(
    session: SessionDep,
    response: Response,
    refresh_token: Annotated[str | None, Cookie()] = None
) -> AccessToken:


    
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token"
        )


    payload = get_payload_refresh_token(refresh_token=refresh_token)
    
    

    revoked_token = await get_revoked_token_by_jti(
        session=session, 
        jti=payload.jti
    )

    if revoked_token is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token"
        )

    
    user_id = uuid.UUID(payload.sub)

    user = await get_user_by_id(
        session=session, 
        user_id=user_id
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="invalid token"
        )


    access_token = create_access_token(user=user)
    refresh_token = create_refresh_token(user=user)


    new_revoked_token = RevokedToken(
        jti=payload.jti,
        expires_at=payload.exp
    )

    session.add(new_revoked_token)

    try:
       await session.commit()

    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
        )


    _set_cookie_refresh(response=response, refresh_token=refresh_token)

    return AccessToken(access_token=access_token)

@router.post(
    "/logout",
    status_code=status.HTTP_200_OK
)
async def loguot_user(
    session: SessionDep,
    response: Response,
    refresh_token: Annotated[str | None, Cookie()] = None
):
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token"
        )

    payload = get_payload_refresh_token(refresh_token=refresh_token)

    revoked_token = RevokedToken(
        jti=payload.jti,
        expires_at=payload.exp
    )

    session.add(revoked_token)
    try:
        await session.commit()      

          
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bad request"
        )
    
    response.delete_cookie(
        key="refresh_token",
    )


invalid_token_error = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="invalid token"
)
    

async def get_current_user(
    session: SessionDep,
    access_token: Annotated[str | None, Depends(oauth2_scheme)],
) -> User:
    if access_token is None:
        raise invalid_token_error

    token = get_payload_access_token(access_token=access_token)
    user = await get_user_by_id(session=session, user_id=uuid.UUID(token.sub))

    if user is None:
        raise invalid_token_error

    return user
    

@router.get(
    "/me",
    response_model=UserResponse
)
async def get_self_info(
    current_user: Annotated[User, Depends(get_current_user)]
) -> UserResponse: 

    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User blocked"
        )

    return UserResponse.model_validate(current_user)

