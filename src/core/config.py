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
    API_V1_STR: str = "/api/v1"

    # Database Settings
    DB_HOST: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    
    # Security Settings
    SECRET_KEY: str = "your-secret-key-replace-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


config = Config()
