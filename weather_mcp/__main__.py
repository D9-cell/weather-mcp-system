"""Main entry point for Weather MCP Server."""

import asyncio
import sys

from weather_mcp.server import WeatherMCPServer


def main():
    """Main entry point for the Weather MCP Server."""
    server = WeatherMCPServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
