from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from .exceptions import ForbiddenError, InvalidTokenError


async def invalid_token_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Invalid token"},
        headers={"WWW-Authenticate": "Bearer"}
    )


async def forbidden_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": "Insufficient permissions"},
    )


def register_auth_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        InvalidTokenError,
        invalid_token_exception_handler,
    )

    app.add_exception_handler(
        ForbiddenError,
        forbidden_exception_handler,
    )