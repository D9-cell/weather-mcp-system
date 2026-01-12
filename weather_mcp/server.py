"""MCP Server implementation for weather tools."""

import asyncio
import logging
from typing import Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent

from weather_mcp.config.settings import get_settings
from weather_mcp.services.openweather import WeatherService
from weather_mcp.tools.weather import get_weather_tool, handle_get_current_weather

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WeatherMCPServer:
    """Weather MCP Server implementation."""

    def __init__(self):
        """Initialize the MCP server."""
        self.server = Server("weather-mcp-server")
        self.settings = get_settings()
        self.weather_service: Optional[WeatherService] = None

        # Register handlers
        self._register_handlers()

    def _register_handlers(self):
        """Register MCP protocol handlers."""

        @self.server.list_tools()
        async def list_tools():
            """List available tools."""
            logger.debug("Listing available tools")
            tools = [get_weather_tool()]
            logger.info(f"Returning {len(tools)} tools")
            return tools

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Handle tool invocation."""
            logger.info(f"Tool call received: {name}")
            logger.debug(f"Tool arguments: {arguments}")

            if name == "get_current_weather":
                city = arguments.get("city")
                country = arguments.get("country")

                if not city:
                    logger.warning("Missing required parameter: city")
                    return [
                        TextContent(
                            type="text",
                            text='{"error": "Missing required parameter: city"}',
                        )
                    ]

                logger.info(f"Fetching weather for {city}, {country or 'unknown country'}")
                try:
                    result = await handle_get_current_weather(
                        self.weather_service, city, country
                    )
                    logger.info(f"Weather data retrieved successfully for {city}")
                    return result
                except Exception as e:
                    logger.error(f"Error fetching weather for {city}: {e}", exc_info=True)
                    return [
                        TextContent(
                            type="text",
                            text=f'{{"error": "Failed to fetch weather data: {str(e)}"}}',
                        )
                    ]
            else:
                logger.warning(f"Unknown tool requested: {name}")
                return [
                    TextContent(
                        type="text",
                        text=f'{{"error": "Unknown tool: {name}"}}',
                    )
                ]

    async def run(self):
        """Run the MCP server."""
        # Initialize services
        self.weather_service = WeatherService(self.settings)

        try:
            logger.info("Starting Weather MCP Server...")
            logger.info(f"API Base URL: {self.settings.openweathermap_base_url}")

            # Run the server with stdio transport
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options(),
                )
        finally:
            # Cleanup
            if self.weather_service:
                await self.weather_service.close()
                logger.info("Weather service closed")
