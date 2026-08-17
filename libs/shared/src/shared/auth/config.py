from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class JWTSettings(BaseSettings):
    PUBLIC_KEY_PATH: Path
    ALGORITHM: str

    public_key_text: str

    def model_post_init(self, __context) -> None:  # noqa: PYI063
        self.public_key_text = self.PUBLIC_KEY_PATH.read_text()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = JWTSettings()