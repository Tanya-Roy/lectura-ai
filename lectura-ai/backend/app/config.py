from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # General Application Settings
    APP_NAME: str = "Lectura AI"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Database Settings
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://lectura:lectura_secret_123@localhost:5432/lectura_db",
        description="Async connection string for SQLAlchemy with asyncpg",
    )
    DATABASE_SYNC_URL: str = Field(
        default="postgresql://lectura:lectura_secret_123@localhost:5432/lectura_db",
        description="Synchronous connection string for Alembic migrations",
    )

    # Redis Settings
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security & Authentication Settings
    JWT_SECRET: str = "lectura_super_secret_jwt_key_2026_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # AI & External API Keys
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL_NAME: str = "gpt-4o"
    OPENAI_FAST_MODEL_NAME: str = "gpt-4o-mini"
    YOUTUBE_API_KEY: str = ""

    # CORS Settings
    CORS_ORIGINS: Union[str, List[str]] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    # Feature Flags
    ENABLE_VERIFICATION_AGENT: bool = True
    ENABLE_QUIZ_GENERATION: bool = True
    ENABLE_FLASHCARD_GENERATION: bool = True
    ENABLE_REDIS_CACHE: bool = True


settings = Settings()
