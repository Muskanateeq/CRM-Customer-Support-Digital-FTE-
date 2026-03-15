"""
Configuration Module

Loads environment variables and provides application settings.
Uses Pydantic Settings for type-safe configuration management.
"""

from typing import List, Union, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database Configuration
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/tasknest"

    # Authentication & Security
    BETTER_AUTH_SECRET: str
    BETTER_AUTH_URL: str = "http://localhost:3000"
    BETTER_AUTH_JWKS_URL: str = "http://localhost:3000/api/auth/jwks"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_DAYS: int = 7

    # CORS Configuration
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:3000", "http://localhost:3001"]

    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # LLM Provider Configuration (Phase 3)
    LLM_PROVIDER: str = "groq"  # Options: "groq", "gemini", or "openai"

    # Groq Configuration (FREE - 14,400 requests/day)
    GROQ_API_KEY: Optional[str] = None  # Required if using Groq
    GROQ_MODEL: str = "llama-3.3-70b-versatile"  # Groq model name

    # Gemini Configuration
    GOOGLE_API_KEY: Optional[str] = None  # Required if using Gemini
    GEMINI_MODEL: str = "gemini-2.5-flash"  # Options: gemini-2.5-flash or gemini-2.5-pro

    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = None  # Required if using OpenAI
    OPENAI_MODEL: str = "gpt-4o"  # OpenAI model name

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from comma-separated string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Global settings instance
settings = Settings()
