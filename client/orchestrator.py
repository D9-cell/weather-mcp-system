"""Orchestrator for LLM ↔ MCP control flow."""

import json
import logging
import os
from typing import Any, Dict, List

from client.llm import OllamaClient, convert_mcp_tools_to_ollama_format
from client.mcp import MCPClient

logger = logging.getLogger(__name__)


class WeatherOrchestrator:
    """Orchestrates interaction between Ollama LLM and MCP Server."""

    def __init__(self):
        """Initialize orchestrator."""
        logger.debug("Initializing WeatherOrchestrator")

        # Validate required environment variables
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

        logger.info(f"Using Ollama at {ollama_url} with model {ollama_model}")

        self.llm = OllamaClient(
            base_url=ollama_url,
            model=ollama_model,
        )

        # MCP Server configuration
        server_path = os.getenv(
            "MCP_SERVER_PATH",
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        )
        logger.info(f"MCP server path: {server_path}")

        self.mcp = MCPClient(
            server_command="uv",
            server_args=["run", "python", "-m", "weather_mcp.main"],
            cwd=server_path,
        )

        self.tools = []
        self.conversation_history: List[Dict[str, str]] = []

    async def initialize(self):
        """Initialize connections and discover tools."""
        logger.info("Connecting to MCP Server...")
        try:
            await self.mcp.connect()
            logger.info("MCP Server connection established")
        except Exception as e:
            logger.error(f"Failed to connect to MCP Server: {e}", exc_info=True)
            raise RuntimeError(
                "Could not connect to MCP Server. Please ensure the server is running:\n"
                "  uv run python -m weather_mcp.main"
            ) from e

        logger.info("Discovering available tools...")
        try:
            self.tools = await self.mcp.list_tools()
            logger.info(f"Discovered {len(self.tools)} tools")
        except Exception as e:
            logger.error(f"Failed to discover tools: {e}", exc_info=True)
            raise RuntimeError("Could not discover tools from MCP Server") from e

        if self.tools:
            print(f"✓ Found {len(self.tools)} tool(s):")
            for tool in self.tools:
                print(f"  - {tool['name']}: {tool['description']}")
                logger.debug(f"Tool discovered: {tool['name']}")
        else:
            logger.warning("No tools discovered from MCP server")
            print("⚠ No tools discovered from MCP server")

        print("✓ Ready!\n")

    async def process_query(self, user_input: str) -> str:
        """Process user query through LLM with tool calling.

        Args:
            user_input: User's question

        Returns:
            Final response text
        """
        logger.info(f"Processing query: {user_input[:100]}...")

        # Add user message to conversation
        self.conversation_history.append({
            "role": "user",
            "content": user_input,
        })

        # Convert MCP tools to Ollama format
        ollama_tools = convert_mcp_tools_to_ollama_format(self.tools) if self.tools else None
        logger.debug(f"Prepared {len(ollama_tools) if ollama_tools else 0} tools for LLM")

        # Main loop: handle tool calls iteratively
        max_iterations = 5
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            logger.debug(f"Starting iteration {iteration}/{max_iterations}")

            try:
                # Call LLM with conversation history and tools
                logger.debug("Calling Ollama LLM")
                response = await self.llm.chat(
                    messages=self.conversation_history,
                    tools=ollama_tools,
                )
                logger.debug("LLM response received")

            except Exception as e:
                logger.error(f"LLM call failed: {e}", exc_info=True)
                raise RuntimeError(
                    "Could not connect to Ollama. Please ensure it's running:\n"
                    "  ollama serve"
                ) from e

            message = response.get("message", {})
            content = message.get("content", "")
            tool_calls = message.get("tool_calls", [])

            # If no tool calls, we have the final answer
            if not tool_calls:
                logger.info("No tool calls detected, returning final response")
                # Add assistant response to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": content,
                })
                return content

            # Handle tool calls
            logger.info(f"Tool calls detected: {len(tool_calls)}")
            print(f"[Tool calls detected: {len(tool_calls)}]")

            # Add assistant message with tool calls to history
            self.conversation_history.append({
                "role": "assistant",
                "content": content,
                "tool_calls": tool_calls,
            })

            # Execute each tool call
            for tool_call in tool_calls:
                function = tool_call.get("function", {})
                tool_name = function.get("name")
                arguments = function.get("arguments", {})

                logger.info(f"Executing tool: {tool_name} with args: {arguments}")
                print(f"  → Calling {tool_name} with {arguments}")

                try:
                    # Call MCP server
                    logger.debug(f"Calling MCP tool: {tool_name}")
                    tool_result = await self.mcp.call_tool(tool_name, arguments)
                    logger.debug(f"MCP tool result: {tool_result}")

                    # Convert result to JSON string if it's a dict
                    if isinstance(tool_result, dict):
                        result_content = json.dumps(tool_result)
                    else:
                        result_content = str(tool_result)

                    print(f"  ✓ Result received")
                    logger.info(f"Tool {tool_name} executed successfully")

                    # Add tool result to conversation
                    self.conversation_history.append({
                        "role": "tool",
                        "content": result_content,
                    })

                except Exception as e:
                    error_msg = f"Tool execution failed: {e}"
                    logger.error(error_msg, exc_info=True)
                    print(f"  ✗ {str(e)}")

                    # Add error as tool result
                    self.conversation_history.append({
                        "role": "tool",
                        "content": json.dumps({"error": str(e)}),
                    })

        # Max iterations reached
        logger.warning(f"Max iterations ({max_iterations}) reached for query")
        return "I apologize, but I couldn't complete your request after multiple attempts."

    async def cleanup(self):
        """Cleanup resources."""
        logger.info("Starting cleanup")
        try:
            await self.llm.close()
            logger.debug("LLM client closed")
        except Exception as e:
            logger.warning(f"Error closing LLM client: {e}")

        try:
            await self.mcp.close()
            logger.debug("MCP client closed")
        except Exception as e:
            logger.warning(f"Error closing MCP client: {e}")

        logger.info("Cleanup complete")
