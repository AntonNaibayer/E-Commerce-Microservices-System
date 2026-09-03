from fastapi import FastAPI
from shared.auth.handlers import register_auth_exception_handlers

from app.api.v1.router import router

app = FastAPI()

register_auth_exception_handlers(app)

app.include_router(router)

