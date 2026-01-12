"""Ollama LLM adapter with tool calling support."""

import json
import logging
from typing import Any, Dict, List, Optional

import httpx # type: ignore

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for Ollama HTTP API with tool calling support."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "qwen2.5:7b"):
        """Initialize Ollama client.

        Args:
            base_url: Ollama API base URL
            model: Model name to use
        """
        logger.info(f"Initializing Ollama client with model: {model} at {base_url}")
        self.base_url = base_url
        self.model = model
        self.client = httpx.AsyncClient(timeout=120.0)

    async def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Send chat request to Ollama with optional tool definitions.

        Args:
            messages: List of message dicts with 'role' and 'content'
            tools: Optional list of tool definitions

        Returns:
            Response dict with 'message' containing 'content' and optional 'tool_calls'
        """
        logger.debug(f"Sending chat request with {len(messages)} messages and {len(tools) if tools else 0} tools")

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }

        if tools:
            payload["tools"] = tools

        try:
            logger.debug(f"POST to {self.base_url}/api/chat")
            response = await self.client.post(
                f"{self.base_url}/api/chat",
                json=payload,
            )
            response.raise_for_status()
            result = response.json()
            logger.debug("LLM response received successfully")
            return result

        except httpx.ConnectError as e:
            logger.error(f"Cannot connect to Ollama at {self.base_url}: {e}")
            raise RuntimeError(
                f"Cannot connect to Ollama at {self.base_url}.\n"
                "Please ensure Ollama is running:\n"
                "  ollama serve"
            ) from e
        except httpx.TimeoutException as e:
            logger.error(f"Ollama request timed out: {e}")
            raise RuntimeError(
                "Ollama request timed out. The model might be too large or the system is busy."
            ) from e
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama HTTP error {e.response.status_code}: {e.response.text}")
            if e.response.status_code == 404:
                raise RuntimeError(
                    f"Model '{self.model}' not found in Ollama.\n"
                    f"Please pull the model first:\n"
                    f"  ollama pull {self.model}"
                ) from e
            else:
                raise RuntimeError(f"Ollama API error: {e.response.text}") from e
        except Exception as e:
            logger.error(f"Unexpected error calling Ollama: {e}", exc_info=True)
            raise RuntimeError(f"Unexpected error communicating with Ollama: {e}") from e

    async def close(self):
        """Close HTTP client."""
        logger.debug("Closing Ollama HTTP client")
        try:
            await self.client.aclose()
            logger.debug("Ollama client closed successfully")
        except Exception as e:
            logger.warning(f"Error closing Ollama client: {e}")


def convert_mcp_tools_to_ollama_format(mcp_tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert MCP tool schema to Ollama function calling format.

    Args:
        mcp_tools: List of MCP tool definitions

    Returns:
        List of tools in Ollama format
    """
    logger.debug(f"Converting {len(mcp_tools)} MCP tools to Ollama format")
    ollama_tools = []

    for tool in mcp_tools:
        ollama_tool = {
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["inputSchema"],
            },
        }
        ollama_tools.append(ollama_tool)

    logger.debug(f"Converted {len(ollama_tools)} tools successfully")
    return ollama_tools
