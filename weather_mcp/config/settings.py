"""Application settings and configuration."""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # OpenWeatherMap API Configuration
    openweathermap_api_key: str = Field(
        ...,
        description="OpenWeatherMap API key",
        validation_alias="OPENWEATHERMAP_API_KEY",
    )

    openweathermap_base_url: str = Field(
        default="https://api.openweathermap.org/data/2.5",
        description="OpenWeatherMap API base URL",
        validation_alias="OPENWEATHERMAP_BASE_URL",
    )

    request_timeout: int = Field(
        default=10,
        description="HTTP request timeout in seconds",
        validation_alias="REQUEST_TIMEOUT",
    )

    @property
    def weather_api_url(self) -> str:
        """Construct the weather API endpoint URL."""
        return f"{self.openweathermap_base_url}/weather"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
