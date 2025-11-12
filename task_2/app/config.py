"""Configuration management using Pydantic settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    openai_temperature: float = 0.7

    # Database Configuration
    database_url: str = "postgresql://chatbot_user:chatbot_pass@localhost:5432/chatbot_db"

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# Global settings instance
settings = Settings()

