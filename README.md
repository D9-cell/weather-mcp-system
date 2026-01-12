# Weather MCP System

A production-grade MCP (Model Context Protocol) system that enables natural language weather queries through a local LLM, with structured tool calling and external API integration.

## Overview

The Weather MCP System provides a complete solution for natural language weather queries using modern AI architecture. It consists of two main components:

- **MCP Server**: A structured API server that exposes weather-related tools using the OpenWeatherMap API
- **MCP Client**: A CLI-based client that accepts natural language input, uses a local LLM (Ollama) to detect tool calls, and orchestrates the complete query workflow

This system demonstrates the power of MCP by enabling seamless integration between conversational AI and structured APIs, all running locally without cloud dependencies.

### Why MCP?

MCP (Model Context Protocol) provides a standardized way for AI models to interact with external tools and APIs. Unlike traditional chatbots that generate natural language responses, MCP enables:

- **Structured tool calling**: AI models can invoke specific functions with typed parameters
- **Deterministic results**: Tool responses are structured JSON, not conversational text
- **Composability**: Easy integration of multiple tools and services
- **Local execution**: No cloud APIs required for the core functionality

## Architecture Overview

### System Components

```Components
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MCP Client    │    │   MCP Server    │    │ OpenWeatherMap  │
│                 │    │                 │    │      API        │
│ • CLI Interface │◄──►│ •Weather Tools  │◄──►│                 │
│ • Ollama LLM    │    │ •JSON Responses │    │                 │
│ • Tool Detection│    │ •API Integration│    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

#### MCP Server (`weather_mcp/`)

- **Purpose**: Exposes structured weather tools via MCP protocol
- **Technology**: Python + MCP SDK + OpenWeatherMap API
- **Responsibilities**:
  - Tool discovery and registration
  - Weather data fetching and formatting
  - Error handling and validation
  - Structured JSON responses only

#### MCP Client (`client/`)

- **Purpose**: Natural language interface with tool calling orchestration
- **Technology**: Python + Ollama HTTP API + MCP client SDK
- **Responsibilities**:
  - CLI user interaction
  - LLM conversation management
  - Tool call detection and execution
  - Result formatting and display

#### Local LLM (Ollama)

- **Purpose**: Natural language understanding and tool call generation
- **Technology**: Local inference via HTTP API
- **Responsibilities**:
  - Understanding user intent
  - Generating appropriate tool calls
  - Processing tool results into natural language responses

## System Workflow

The system follows a clear, iterative workflow for processing weather queries:

### 1. User Input

User enters a natural language query via CLI:

```question
"What's the weather like in Tokyo?"
```

### 2. LLM Processing

The MCP Client sends the query to Ollama with available tool definitions. The LLM:

- Analyzes the query intent
- Identifies that weather information is needed
- Generates a structured tool call for `get_current_weather`

### 3. Tool Call Detection

The MCP Client detects the tool call in the LLM response and extracts:

- Tool name: `get_current_weather`
- Parameters: `{"city": "Tokyo"}`

### 4. MCP Server Invocation

The MCP Client calls the MCP Server with the structured parameters. The server:

- Validates the request
- Calls OpenWeatherMap API
- Formats the response as structured JSON
- Returns deterministic weather data

### 5. Result Processing

The MCP Client sends the tool result back to the LLM, which:

- Processes the structured weather data
- Generates a natural language response
- Incorporates the weather information into a conversational reply

### 6. Final Output

The system displays the complete response to the user:

```output
"The current weather in Tokyo is 15°C with clear skies and 67% humidity."
```

## Data Flow

### Request Flow

```flow
Natural Language → LLM → Tool Call JSON → MCP Server → External API → Structured JSON → LLM → Natural Language
```

### Data Types

#### Natural Language (User ↔ LLM)

- Conversational text input from users
- Natural language responses from the LLM
- Human-readable but unstructured

#### Structured JSON (LLM ↔ MCP Server)

- Tool call specifications with typed parameters
- Deterministic API responses with fixed schemas
- Machine-readable and validated

#### MCP Protocol Messages

- Tool discovery requests/responses
- Tool invocation requests/responses
- Initialization and session management

### Component Responsibilities

#### LLM (Ollama)

- **Input**: Natural language + tool schemas
- **Output**: Natural language responses + tool calls
- **Purpose**: Intent understanding and conversational responses

#### MCP Server

- **Input**: Structured tool calls with typed parameters
- **Output**: Structured JSON responses only
- **Purpose**: Deterministic API integration and data formatting

#### MCP Client

- **Input**: User CLI input + LLM responses + MCP responses
- **Output**: Formatted CLI output
- **Purpose**: Orchestration and user interface

## Project Structure

```structure
weather-mcp-system/
├── pyproject.toml              # Project configuration and dependencies
├── uv.lock                     # Locked dependency versions
├── .env.example                # Environment variables template
├── README.md                   # This documentation
├── weather_mcp/                # MCP Server package
│   ├── __init__.py             # Package initialization
│   ├── __main__.py             # Module entry point
│   ├── main.py                 # Server entry point
│   ├── server.py               # MCP server implementation
│   ├── config/                 # Configuration layer
│   │   ├── __init__.py
│   │   └── settings.py         # Environment settings
│   ├── services/               # Service layer
│   │   ├── __init__.py
│   │   └── openweather.py      # OpenWeatherMap client
│   └── tools/                  # Tool definitions
│       ├── __init__.py
│       └── weather.py          # MCP tool definitions
├── client/                     # MCP Client package
│   ├── __init__.py             # Package initialization
│   ├── __main__.py             # Module entry point
│   ├── main.py                 # CLI entry point
│   ├── orchestrator.py         # Control flow orchestration
│   ├── llm.py                  # Ollama adapter
│   └── mcp.py                  # MCP client wrapper
└── tests/                      # Test suite
    └── __init__.py
```

## Prerequisites

### System Requirements

- **Operating System**: Linux, macOS, or Windows with WSL
- **Python**: Version 3.10 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended for LLM inference)
- **Network**: Internet connection for OpenWeatherMap API

### Required Software

- **uv**: Modern Python package manager (<https://github.com/astral-sh/uv>)
- **Ollama**: Local LLM runtime (<https://ollama.com/>)
- **OpenWeatherMap API Key**: Free API key from OpenWeatherMap

### LLM Model

- **Recommended**: `qwen2.5:7b` (good tool calling support, reasonable resource usage)
- **Alternative**: `llama3.1:8b` (excellent reasoning, higher resource requirements)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd weather-mcp-system
```

### 2. Install Dependencies

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv sync
```

### 3. Set Up Ollama

```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.com/install.sh | sh

# Pull the recommended model
ollama pull qwen2.5:7b

# Verify installation
ollama list
```

### 4. Configure Environment Variables

```bash
# Copy the environment template
cp .env.example .env

# Edit .env and add your OpenWeatherMap API key
# Get your free API key from: https://openweathermap.org/api
nano .env
```

**Required `.env` content:**

```env
OPENWEATHERMAP_API_KEY=your_actual_api_key_here
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
```

### 5. Verify Setup

```bash
# Test MCP Server
uv run python -m weather_mcp.main

# In another terminal, test MCP Client
uv run python -m client.main
```

## Running the Project

### Starting the MCP Server

The MCP Server runs as a background service that the MCP Client connects to:

```bash
# Terminal 1: Start MCP Server
uv run python -m weather_mcp.main
```

The server will start and wait for MCP client connections via stdio.

### Starting the MCP Client

The MCP Client provides the interactive CLI interface:

```bash
# Terminal 2: Start MCP Client
uv run python -m client.main
```

### Example CLI Session

```example
$ uv run python -m client.main

=== Weather MCP Client ===
Powered by Ollama + MCP Server
Type your weather question (or 'exit' to quit)

Connecting to MCP Server...
Discovering available tools...
✓ Found 1 tool(s):
  - get_current_weather: Get the current weather for a specified city. Returns temperature, humidity, conditions, and more.
✓ Ready!

You: What's the weather like in Tokyo?
[Tool calls detected: 1]
  → Calling get_current_weather with {'city': 'Tokyo'}
  ✓ Result received

Assistant: The current weather in Tokyo is 15°C with clear skies. The temperature feels like 14°C, humidity is at 67%, and there's a gentle wind speed of 3.2 m/s.

You: How about the weather in London?
[Tool calls detected: 1]
  → Calling get_current_weather with {'city': 'London'}
  ✓ Result received

Assistant: In London, it's currently 8°C with light rain. The feels-like temperature is 6°C, humidity is 87%, and wind speed is 4.1 m/s.

You: exit
Goodbye!
```

## Configuration

### Environment Variables

| Variable                 | Required | Default | Description |
|--------------------------|----------|---------|-------------|
| `OPENWEATHERMAP_API_KEY` | Yes      | -       |Your OpenWeatherMap API key |
| `OLLAMA_BASE_URL`        | No       |`http://localhost:11434` | Ollama HTTP API endpoint |
| `OLLAMA_MODEL`           | No       | `qwen2.5:7b` | LLM model to use |
| `MCP_SERVER_PATH`        | No       | Auto-detected | Path to MCP server directory |

### API Key Management

1. **Sign up** at <https://openweathermap.org/>
2. **Navigate** to the API Keys section
3. **Copy** your default API key
4. **Paste** it into your `.env` file

The free tier provides:

- 1,000 API calls per day
- Current weather data
- 5-day weather forecasts

### Model Selection

Different Ollama models have varying tool calling capabilities:

- **qwen2.5:7b**: Excellent tool calling, good reasoning, moderate resource usage
- **llama3.1:8b**: Strong reasoning, good tool calling, higher resource requirements
- **codellama:7b**: Good for technical tasks, moderate tool calling support

## Error Handling & Logging

### Error Types Handled

#### Network Errors

- **Ollama connection failures**: Clear messages when LLM is unreachable
- **MCP Server connection issues**: Automatic retry with informative errors
- **OpenWeatherMap API failures**: HTTP status code handling with user-friendly messages

#### Data Validation Errors

- **Invalid city names**: API-level validation with helpful error messages
- **Missing API keys**: Startup validation prevents runtime failures
- **Malformed tool calls**: Graceful degradation with error reporting

#### LLM Processing Errors

- **Tool call parsing failures**: Fallback to text-only responses
- **Model response timeouts**: Configurable timeouts with user notification
- **Iteration limits**: Prevents infinite loops with maximum retry limits

### Logging Levels

- **INFO**: Normal operation, connection status, tool discovery
- **WARNING**: Non-critical issues, retry attempts
- **ERROR**: Failures that prevent operation, with full stack traces
- **DEBUG**: Detailed internal state (available with `--debug` flag)

### User-Facing Error Messages

All errors are presented to users in a clear, actionable format:

```
Error: Could not connect to Ollama. Please ensure it's running:
  ollama serve

Error: OpenWeatherMap API key not found. Please set OPENWEATHERMAP_API_KEY in .env

Error: City 'InvalidCity123' not found. Please check the spelling.
```

## Extensibility

### Adding New MCP Tools

1. **Define the tool** in `weather_mcp/tools/`:

```python
def get_weather_forecast_tool() -> Tool:
    return Tool(
        name="get_weather_forecast",
        description="Get 5-day weather forecast for a city",
        inputSchema={
            "type": "object",
            "properties": {
                "city": {"type": "string"},
                "country": {"type": "string"}
            },
            "required": ["city"]
        }
    )
```

1. **Implement the handler**:

```python
async def handle_get_weather_forecast(weather_service, city, country=None):
    # Implementation here
    pass
```

1. **Register in the server**:

```python
@self.server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "get_weather_forecast":
        # Handle forecast tool
    elif name == "get_current_weather":
        # Handle current weather tool
```

### Swapping the LLM

1. **Install a new model**:

```bash
ollama pull llama3.1:8b
```

1. **Update environment**:

```env
OLLAMA_MODEL=llama3.1:8b
```

1. **Test compatibility**: Different models may have varying tool calling capabilities

### Extending the Client

#### Adding New Commands

Modify `client/main.py` to add CLI commands beyond weather queries.

#### Custom Output Formatting

Extend `client/orchestrator.py` to support different output formats (JSON, table, etc.).

#### Multi-turn Conversations

Enhance conversation history management for more complex interactions.

## Troubleshooting

### Common Issues

#### "Could not connect to Ollama"

**Symptoms**: Client fails to start with connection error
**Cause**: Ollama service not running
**Fix**:

```bash
# Start Ollama service
ollama serve

# In another terminal, verify it's running
curl http://localhost:11434/api/tags
```

#### "OpenWeatherMap API key not found"

**Symptoms**: Server fails to start or returns auth errors
**Cause**: Missing or invalid API key in `.env`
**Fix**:

```bash
# Check .env file exists and contains the key
cat .env

# Get a new API key from https://openweathermap.org/api
# Update .env and restart
```

#### "No tools discovered from MCP server"

**Symptoms**: Client starts but reports no tools available
**Cause**: MCP Server not running or connection failed
**Fix**:

```bash
# Ensure MCP Server is running in another terminal
uv run python -m weather_mcp.main

# Check for connection errors in server logs
```

#### "Tool call failed" or "City not found"

**Symptoms**: Tool execution returns error
**Cause**: Invalid city name or API limits exceeded
**Fix**:

- Verify city name spelling
- Check API key validity and usage limits
- Try with a different city (e.g., "London" instead of "london")

#### "Module import errors"

**Symptoms**: `uv run python -m ...` fails with import errors
**Cause**: Dependencies not installed or Python path issues
**Fix**:

```bash
# Reinstall dependencies
uv sync

# Check Python version compatibility
python --version  # Should be 3.10+
```

### Performance Issues

#### Slow LLM Responses

- **Cause**: Large model or insufficient hardware
- **Fix**: Try smaller model (`qwen2.5:3b`) or upgrade hardware

#### High Memory Usage

- **Cause**: Large models loaded in memory
- **Fix**: Use smaller models or add more RAM

### Debug Mode

Enable detailed logging for troubleshooting:

```bash
# Set environment variable
export PYTHONPATH=/path/to/weather-mcp-system
export LOG_LEVEL=DEBUG

# Run with debug output
uv run python -c "import logging; logging.basicConfig(level=logging.DEBUG)" -m client.main
```

## License

This project is provided as-is for educational and demonstration purposes. The code demonstrates modern MCP architecture patterns and local LLM integration techniques.

---

**Built with**: Python, MCP SDK, Ollama, OpenWeatherMap API  
**Architecture**: Clean separation between conversational AI and structured APIs  
**Philosophy**: Local-first, privacy-preserving, extensible by design
