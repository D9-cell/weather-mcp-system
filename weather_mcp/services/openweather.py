"""OpenWeatherMap API service."""

import logging
from typing import Optional

import httpx
from pydantic import BaseModel, Field

from weather_mcp.config import Settings

logger = logging.getLogger(__name__)


class WeatherData(BaseModel):
    """Structured weather data response."""

    city: str = Field(..., description="City name")
    country: str = Field(..., description="Country code")
    temperature: float = Field(..., description="Temperature in Celsius")
    feels_like: float = Field(..., description="Feels like temperature in Celsius")
    humidity: int = Field(..., description="Humidity percentage")
    pressure: int = Field(..., description="Atmospheric pressure in hPa")
    description: str = Field(..., description="Weather description")
    wind_speed: float = Field(..., description="Wind speed in m/s")
    clouds: int = Field(..., description="Cloudiness percentage")


class WeatherService:
    """Service for interacting with OpenWeatherMap API."""

    def __init__(self, settings: Settings):
        """Initialize weather service with settings.

        Args:
            settings: Application settings containing API key and URLs
        """
        logger.info("Initializing WeatherService")
        self.settings = settings
        self.client = httpx.AsyncClient(timeout=settings.request_timeout)

    async def get_current_weather(
        self, city: str, country: Optional[str] = None
    ) -> WeatherData:
        """Fetch current weather data for a city.

        Args:
            city: City name
            country: Optional ISO 3166 country code (e.g., 'US', 'GB')

        Returns:
            WeatherData: Structured weather information

        Raises:
            httpx.HTTPStatusError: If API request fails
            ValueError: If response data is invalid
        """
        # Construct location query
        location = f"{city},{country}" if country else city
        logger.info(f"Fetching weather data for: {location}")

        # Build request parameters
        params = {
            "q": location,
            "appid": self.settings.openweathermap_api_key,
            "units": "metric",  # Use Celsius
        }

        try:
            # Make API request
            logger.debug(f"Making API request to {self.settings.weather_api_url}")
            response = await self.client.get(self.settings.weather_api_url, params=params)
            response.raise_for_status()

            data = response.json()
            logger.debug("Weather API response received successfully")

            # Parse and structure the response
            weather_data = WeatherData(
                city=data["name"],
                country=data["sys"]["country"],
                temperature=data["main"]["temp"],
                feels_like=data["main"]["feels_like"],
                humidity=data["main"]["humidity"],
                pressure=data["main"]["pressure"],
                description=data["weather"][0]["description"],
                wind_speed=data["wind"]["speed"],
                clouds=data["clouds"]["all"],
            )

            logger.info(f"Weather data parsed successfully for {weather_data.city}, {weather_data.country}")
            return weather_data

        except httpx.ConnectError as e:
            logger.error(f"Cannot connect to OpenWeatherMap API: {e}")
            raise RuntimeError("Cannot connect to weather service. Please check your internet connection.") from e
        except httpx.TimeoutException as e:
            logger.error(f"OpenWeatherMap API request timed out: {e}")
            raise RuntimeError("Weather service request timed out. Please try again.") from e
        except httpx.HTTPStatusError as e:
            logger.error(f"OpenWeatherMap API error {e.response.status_code}: {e.response.text}")
            if e.response.status_code == 401:
                raise RuntimeError("Invalid API key. Please check your OPENWEATHERMAP_API_KEY.") from e
            elif e.response.status_code == 404:
                raise RuntimeError(f"City '{location}' not found. Please check the city name and country code.") from e
            else:
                raise RuntimeError(f"Weather service error: {e.response.text}") from e
        except (KeyError, ValueError) as e:
            logger.error(f"Invalid response data from weather API: {e}")
            raise RuntimeError("Invalid response from weather service. Please try again.") from e
        except Exception as e:
            logger.error(f"Unexpected error in weather service: {e}", exc_info=True)
            raise RuntimeError(f"Unexpected error fetching weather data: {e}") from e

    async def close(self):
        """Close the HTTP client."""
        logger.debug("Closing WeatherService HTTP client")
        try:
            await self.client.aclose()
            logger.debug("WeatherService client closed successfully")
        except Exception as e:
            logger.warning(f"Error closing WeatherService client: {e}")
