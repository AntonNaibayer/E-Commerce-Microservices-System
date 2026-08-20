from functools import cached_property

from pydantic_settings import BaseSettings, SettingsConfigDict


class DBSettings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.DB_USER}:{self.DB_PASS}@"
            f"{self.DB_HOST}:{self.DB_PORT}/"
            f"{self.DB_NAME}"
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class RedisSettings(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASS: str
    REDIS_NAME: str

    @property
    def redis_url(self) -> str:
        return (
            f"redis://:{self.REDIS_PASS}@"
            f"{self.REDIS_HOST}:{self.REDIS_PORT}/0"
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class Settings(BaseSettings):
    db: DBSettings = DBSettings()
    redis: RedisSettings = RedisSettings()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()