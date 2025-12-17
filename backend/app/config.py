from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Core
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    SECRET_KEY: str = Field(..., env="SECRET_KEY")

    # AI Keys
    GEMINI_API_KEY: str | None = Field(default=None, env="GEMINI_API_KEY")
    XAI_API_KEY: str | None = Field(default=None, env="XAI_API_KEY")

    # ✅ FIX: Explicitly define XAI_MODEL
    XAI_MODEL: str | None = Field(default="grok-beta", env="XAI_MODEL")

    # Auth
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
