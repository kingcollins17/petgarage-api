from pydantic_settings import (  # ty:ignore[unresolved-import]
    BaseSettings,
    SettingsConfigDict,
)
from pathlib import Path
from typing import Optional


class Config(BaseSettings):
    # App Settings
    APP_NAME: str = "PetGarage API"
    APP_DEBUG: bool = False

    # Database Settings
    DB_HOST: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


config = Config()
