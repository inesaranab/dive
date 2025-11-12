"""Configuration management using Pydantic settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # OpenAI Configuration
    openai_api_key: str

    # Database Configuration
    database_url: str = "postgresql://classifier_user:classifier_pass@localhost:5432/news_classifier"

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Classification categories
    categories: dict[int, str] = {
        0: "Politics",
        1: "Sport",
        2: "Technology",
        3: "Entertainment",
        4: "Business",
    }

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# Global settings instance
settings = Settings()

