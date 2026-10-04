from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str
    SECRET_KEY: str = Field(min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_TIME: int = 30
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    LOG_TO_FILE: bool = True
    REDIS_URL: str | None = None

settings = Settings()