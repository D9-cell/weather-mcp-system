"""MCP tool definitions for weather operations."""

import logging
from typing import Optional

from mcp.types import Tool, TextContent

from weather_mcp.services import WeatherService

logger = logging.getLogger(__name__)


def get_weather_tool() -> Tool:
    """Define the get_current_weather MCP tool.

    Returns:
        Tool: MCP tool definition with schema
    """
    logger.debug("Creating weather tool definition")
    return Tool(
        name="get_current_weather",
        description="Get the current weather for a specified city. Returns temperature, humidity, conditions, and more.",
        inputSchema={
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city name (e.g., 'London', 'San Francisco')",
                },
                "country": {
                    "type": "string",
                    "description": "Optional ISO 3166 country code (e.g., 'US', 'GB', 'FR')",
                },
            },
            "required": ["city"],
        },
    )


async def handle_get_current_weather(
    weather_service: WeatherService,
    city: str,
    country: Optional[str] = None,
) -> list[TextContent]:
    """Handle the get_current_weather tool invocation.

    Args:
        weather_service: Weather service instance
        city: City name
        country: Optional country code

    Returns:
        list[TextContent]: MCP response with weather data as JSON

    Raises:
        Exception: If weather data cannot be retrieved
    """
    logger.info(f"Handling get_current_weather request for {city}, {country or 'unknown'}")

    try:
        weather_data = await weather_service.get_current_weather(city, country)

        # Return structured JSON only
        logger.debug("Weather data retrieved successfully, returning JSON response")
        return [
            TextContent(
                type="text",
                text=weather_data.model_dump_json(indent=2),
            )
        ]
    except Exception as e:
        # Return error as structured response
        logger.error(f"Failed to get weather data for {city}: {e}", exc_info=True)
        error_response = {
            "error": str(e),
            "city": city,
            "country": country,
        }
        return [
            TextContent(
                type="text",
                text=str(error_response),
            )
        ]
