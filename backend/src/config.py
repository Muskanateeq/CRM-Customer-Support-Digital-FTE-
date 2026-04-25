"""
Custora Customer Success FTE - Configuration Management
Centralized configuration using Pydantic Settings with validation
"""

from pydantic import Field, validator
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables with validation."""

    # ============================================
    # Application Settings
    # ============================================
    ENVIRONMENT: str = Field(default="development", description="Environment: development, staging, production")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    # ============================================
    # API Configuration
    # ============================================
    API_HOST: str = Field(default="0.0.0.0", description="API host")
    API_PORT: int = Field(default=8000, description="API port")
    API_CORS_ORIGINS: str = Field(default="http://localhost:3000", description="CORS allowed origins (comma-separated)")
    FRONTEND_URL: str = Field(default="http://localhost:3000", description="Frontend URL for ticket links")

    # ============================================
    # Neon PostgreSQL Settings
    # ============================================
    DATABASE_URL: str = Field(..., description="Full PostgreSQL connection string")
    POSTGRES_HOST: str = Field(..., description="PostgreSQL host")
    POSTGRES_PORT: int = Field(default=5432, description="PostgreSQL port")
    POSTGRES_DB: str = Field(..., description="Database name")
    POSTGRES_USER: str = Field(..., description="Database user")
    POSTGRES_PASSWORD: str = Field(..., description="Database password")
    PROJECT_ID: str = Field(..., description="Neon project ID")
    NEON_API_KEY: Optional[str] = Field(default=None, description="Neon API key for management operations")

    # Database pool settings
    DB_POOL_MIN_SIZE: int = Field(default=2, description="Minimum pool size")
    DB_POOL_MAX_SIZE: int = Field(default=10, description="Maximum pool size")

    # ============================================
    # OpenAI Settings
    # ============================================
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API key")
    AGENT_MODEL: str = Field(default="gpt-4o", description="OpenAI model")
    AGENT_TEMPERATURE: float = Field(default=0.7, ge=0.0, le=2.0, description="Agent temperature")
    AGENT_MAX_TOKENS: int = Field(default=1000, ge=1, le=4096, description="Max tokens")
    AGENT_TIMEOUT_SECONDS: int = Field(default=30, ge=1, le=120, description="Agent timeout")

    # ============================================
    # Groq Settings (Alternative to OpenAI)
    # ============================================
    USE_GROQ: bool = Field(default=False, description="Use Groq instead of OpenAI")
    GROQ_API_KEY: Optional[str] = Field(default=None, description="Groq API key")
    # Groq models: llama-3.3-70b-versatile, llama-3.1-70b-versatile, mixtral-8x7b-32768

    # ============================================
    # Kafka Settings
    # ============================================
    KAFKA_ENABLED: bool = Field(default=False, description="Enable Kafka event streaming")
    KAFKA_BOOTSTRAP_SERVERS: str = Field(default="localhost:9092", description="Kafka bootstrap servers")
    KAFKA_SASL_USERNAME: Optional[str] = Field(default=None, description="Kafka SASL username")
    KAFKA_SASL_PASSWORD: Optional[str] = Field(default=None, description="Kafka SASL password")

    # ============================================
    # Gmail API Settings
    # ============================================
    GMAIL_ENABLED: bool = Field(default=False, description="Enable Gmail channel")
    GMAIL_ADDRESS: Optional[str] = Field(default=None, description="Gmail support email address")
    ADMIN_EMAIL: Optional[str] = Field(default="custora.admin.support@gmail.com", description="Admin email for escalation notifications")
    GMAIL_CREDENTIALS_JSON: Optional[str] = Field(default=None, description="Gmail OAuth credentials")
    GMAIL_TOKEN_JSON: Optional[str] = Field(default=None, description="Gmail OAuth token")
    GOOGLE_PUBSUB_TOPIC: Optional[str] = Field(default=None, description="Google Pub/Sub topic")
    GOOGLE_PUBSUB_SUBSCRIPTION: Optional[str] = Field(default=None, description="Pub/Sub subscription")

    # ============================================
    # Twilio WhatsApp Settings
    # ============================================
    TWILIO_ACCOUNT_SID: Optional[str] = Field(default=None, description="Twilio account SID")
    TWILIO_AUTH_TOKEN: Optional[str] = Field(default=None, description="Twilio auth token")
    TWILIO_WHATSAPP_NUMBER: Optional[str] = Field(default=None, description="Twilio WhatsApp number")
    WHATSAPP_ENABLED: bool = Field(default=True, description="Enable WhatsApp channel")

    # ============================================
    # Channel Configuration
    # ============================================
    WEBFORM_ENABLED: bool = Field(default=True, description="Enable web form channel")
    MAX_EMAIL_LENGTH: int = Field(default=2000, ge=100, le=10000, description="Max email response length")
    MAX_WHATSAPP_LENGTH: int = Field(default=1600, ge=100, le=1600, description="Max WhatsApp length")
    MAX_WEBFORM_LENGTH: int = Field(default=1000, ge=100, le=5000, description="Max web form length")

    # ============================================
    # Monitoring Settings
    # ============================================
    ENABLE_METRICS: bool = Field(default=True, description="Enable Prometheus metrics")
    METRICS_PORT: int = Field(default=9090, description="Metrics port")

    # ============================================
    # Kubernetes Settings
    # ============================================
    K8S_NAMESPACE: str = Field(default="customer-success-fte", description="Kubernetes namespace")
    K8S_REPLICAS_API: int = Field(default=3, ge=1, le=50, description="API replicas")
    K8S_REPLICAS_WORKER: int = Field(default=3, ge=1, le=50, description="Worker replicas")

    # ============================================
    # Worker Configuration
    # ============================================
    WORKER_POOL_SIZE: int = Field(default=4, ge=1, le=20, description="Worker pool size")

    # ============================================
    # Better Auth Configuration
    # ============================================
    BETTER_AUTH_SECRET: Optional[str] = Field(default=None, description="Better Auth secret for JWT signing")
    BETTER_AUTH_URL: Optional[str] = Field(default="http://localhost:3000", description="Better Auth base URL")

    # OAuth Providers
    GOOGLE_CLIENT_ID: Optional[str] = Field(default=None, description="Google OAuth client ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = Field(default=None, description="Google OAuth client secret")
    GITHUB_CLIENT_ID: Optional[str] = Field(default=None, description="GitHub OAuth client ID")
    GITHUB_CLIENT_SECRET: Optional[str] = Field(default=None, description="GitHub OAuth client secret")

    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        """Validate environment value."""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of {allowed}")
        return v

    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        """Validate log level."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of {allowed}")
        return v.upper()

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.ENVIRONMENT == "development"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
