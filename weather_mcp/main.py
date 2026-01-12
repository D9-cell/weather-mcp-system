"""Weather MCP Server - Main entry point."""

import asyncio
import logging

from weather_mcp.server import WeatherMCPServer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for the MCP server."""
    server = WeatherMCPServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
