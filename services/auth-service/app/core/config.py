from functools import cached_property
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DbSettings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class AuthJWT(BaseSettings):
    PRIVATE_KEY_PATH: Path
    PUBLIC_KEY_PATH: Path

    @cached_property
    def private_key_text(self) -> str:
        """Читает приватный ключ с диска один раз и кэширует в памяти."""
        return self.PRIVATE_KEY_PATH.read_text()

    @cached_property
    def public_key_text(self) -> str:
        """Читает публичный ключ с диска один раз и кэширует в памяти."""
        return self.PUBLIC_KEY_PATH.read_text()

    ALGORITHM: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int 
    REFRESH_TOKEN_EXPIRE_DAYS: int

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class Settings(BaseSettings):
    db: DbSettings = Field(default_factory=DbSettings) # type: ignore
    auth_jwt: AuthJWT = Field(default_factory=AuthJWT) # type: ignore

settings = Settings()