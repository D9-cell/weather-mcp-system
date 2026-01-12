"""MCP client wrapper for tool discovery and invocation."""

import json
import logging
from typing import Any, Dict, List, Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client # type: ignore

logger = logging.getLogger(__name__)


class MCPClient:
    """Wrapper for MCP client operations."""

    def __init__(self, server_command: str, server_args: List[str], cwd: str):
        """Initialize MCP client.

        Args:
            server_command: Command to start MCP server (e.g., 'uv')
            server_args: Arguments for server command
            cwd: Working directory for server
        """
        logger.info(f"Initializing MCP client with command: {server_command} {' '.join(server_args)}")
        self.server_command = server_command
        self.server_args = server_args
        self.cwd = cwd
        self.session: Optional[ClientSession] = None # type: ignore
        self._read = None
        self._write = None
        self._context_manager = None

    async def connect(self):
        """Connect to MCP server."""
        logger.info("Connecting to MCP server")
        try:
            server_params = StdioServerParameters(
                command=self.server_command,
                args=self.server_args,
                cwd=self.cwd,
            )

            # Create stdio connection
            logger.debug("Creating stdio connection")
            self._context_manager = stdio_client(server_params)
            self._read, self._write = await self._context_manager.__aenter__()

            # Initialize session
            logger.debug("Initializing MCP session")
            self.session = ClientSession(self._read, self._write)
            await self.session.__aenter__()

            # Initialize the connection
            logger.debug("Initializing MCP connection")
            await self.session.initialize()
            logger.info("MCP client connected successfully")

        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}", exc_info=True)
            raise RuntimeError(
                f"Cannot connect to MCP server.\n"
                f"Command: {self.server_command} {' '.join(self.server_args)}\n"
                f"Working directory: {self.cwd}\n"
                f"Error: {e}"
            ) from e

    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools from MCP server.

        Returns:
            List of tool definitions
        """
        if not self.session:
            raise RuntimeError("MCP client not connected")

        logger.debug("Listing tools from MCP server")
        try:
            result = await self.session.list_tools()

            # Convert MCP tool objects to dicts
            tools = []
            for tool in result.tools:
                tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema,
                })

            logger.info(f"Retrieved {len(tools)} tools from MCP server")
            return tools

        except Exception as e:
            logger.error(f"Failed to list tools: {e}", exc_info=True)
            raise RuntimeError(f"Cannot list tools from MCP server: {e}") from e

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool on the MCP server.

        Args:
            tool_name: Name of the tool to call
            arguments: Arguments for the tool

        Returns:
            Tool result
        """
        if not self.session:
            raise RuntimeError("MCP client not connected")

        logger.info(f"Calling MCP tool: {tool_name}")
        logger.debug(f"Tool arguments: {arguments}")

        try:
            result = await self.session.call_tool(tool_name, arguments)

            # Extract content from result
            if result.content:
                # MCP returns a list of content items
                content_item = result.content[0]
                if hasattr(content_item, "text"):
                    # Try to parse as JSON first
                    try:
                        parsed_result = json.loads(content_item.text)
                        logger.debug(f"Tool result parsed as JSON: {type(parsed_result)}")
                        return parsed_result
                    except json.JSONDecodeError:
                        logger.debug("Tool result is plain text")
                        return content_item.text
                logger.debug("Tool result converted to string")
                return str(content_item)

            logger.warning(f"Tool {tool_name} returned no content")
            return None

        except Exception as e:
            logger.error(f"Tool call failed for {tool_name}: {e}", exc_info=True)
            raise RuntimeError(f"Tool '{tool_name}' execution failed: {e}") from e

    async def close(self):
        """Close MCP connection."""
        logger.debug("Closing MCP client connection")
        if self.session:
            try:
                await self.session.__aexit__(None, None, None)
                logger.debug("MCP session closed")
            except Exception as e:
                logger.warning(f"Error closing MCP session: {e}")

        if self._context_manager:
            try:
                await self._context_manager.__aexit__(None, None, None)
                logger.debug("MCP context manager closed")
            except Exception as e:
                logger.warning(f"Error closing MCP context manager: {e}")

        logger.info("MCP client closed")
