# Incident Agent

A Python FastMCP (Model Context Protocol) server for incident management and analysis.

This project provides a complete MCP server implementation with tools for greeting, echo functionality, and server information retrieval. It demonstrates the FastMCP framework capabilities and serves as a foundation for building more complex incident management tools.

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager

## Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/JayLiuMLP/incident-agent.git
   cd incident-agent
   ```

2. **Install dependencies**

   ```bash
   uv sync
   ```

3. **Verify installation**

   ```bash
   uv run python -c "import fastmcp; print('FastMCP installed successfully!')"
   ```

## MCP Server Usage

### Available Tools

The server provides the following MCP tools:

- **hello** - Greet a person or the world
- **echo** - Echo back a message  
- **server_info** - Get server information and status

### Available Resources

- **config://server/info** - Server configuration information

### Starting the MCP Server

1. **Standard MCP Server (stdio transport)**

   ```bash
   uv run fastmcp run main.py
   ```

2. **HTTP Server** (for API access)

   ```bash
   uv run fastmcp run main.py --transport http --port 8000
   ```

3. **Inspect Server Configuration**

   ```bash
   uv run fastmcp inspect main.py
   ```

### Testing the MCP Server

#### Method 1: Python Client (Recommended)

Use the built-in Python client utilities for easy testing:

```bash
# Run complete test suite (recommended)
uv run python mcp_client_utils.py

# Run comprehensive HTTP client test
uv run python http_client_test.py
```

#### Method 2: Using in Your Python Code

```python
import asyncio
from mcp_client_utils import MCPClient, say_hello, echo_message

# Using utility functions
async def example():
    greeting = await say_hello("Developer")
    echo_result = await echo_message("Test message")
    print(f"Greeting: {greeting}")
    print(f"Echo: {echo_result}")

# Using client class
async def advanced_example():
    client = MCPClient("http://localhost:8000/mcp")
    tools = await client.list_tools()
    server_info = await client.get_server_info()
    print(f"Available tools: {tools}")
    print(f"Server version: {server_info['version']}")

# Run the examples
asyncio.run(example())
asyncio.run(advanced_example())
```

#### Method 3: Integration with MCP Clients

The server can be integrated with MCP-compatible clients like Claude Desktop by adding to your configuration:

```json
{
  "mcpServers": {
    "incident-agent": {
      "command": "uv",
      "args": ["run", "fastmcp", "run", "main.py"],
      "cwd": "/path/to/incident-agent"
    }
  }
}
```

#### Method 4: HTTP API (curl)

⚠️ **Note**: HTTP API requires proper session management and is more complex. Python client is recommended.

For advanced users, you can use curl with the HTTP server:

```bash
# Start HTTP server first
uv run fastmcp run main.py --transport http --port 8000

# Test with Python client (much easier)
uv run python mcp_client_utils.py
```

### Server Output Example

When running the test client, you should see:

```text
🚀 MCP 客户端工具演示
Hello: Hello, 开发者! 🌍 Welcome to the Incident Agent MCP Server!
Echo: Echo: 这是一条测试消息
服务器状态: running
服务器版本: 0.1.0
可用工具: ['hello', 'echo', 'server_info']
```

## Development

- **Run the application**

  ```bash
  uv run python main.py
  ```

- **Run tests**

  ```bash
  uv run pytest
  ```

- **Setup pre-commit hooks**

  ```bash
  uv run pre-commit install
  ```

- **Test MCP functionality**

  ```bash
  # Quick test
  uv run python mcp_client_utils.py
  ```

## Quick Start

Want to test the MCP server right away? Follow these steps:

1. **Install and setup** (if not done already)

   ```bash
   git clone https://github.com/JayLiuMLP/incident-agent.git
   cd incident-agent
   uv sync
   ```

2. **Start the HTTP server** (in one terminal)

   ```bash
   uv run fastmcp run main.py --transport http --port 8000
   ```

3. **Test with Python client** (in another terminal)

   ```bash
   uv run python mcp_client_utils.py
   ```

4. **Expected output**

   ```text
   🚀 MCP 客户端工具演示
   Hello: Hello, 开发者! 🌍 Welcome to the Incident Agent MCP Server!
   Echo: Echo: 这是一条测试消息
   服务器状态: running
   服务器版本: 0.1.0
   可用工具: ['hello', 'echo', 'server_info']
   ```

That's it! Your MCP server is working. 🎉

## Project Structure

```text
incident-agent/
├── main.py                     # Main MCP server entry point
├── run_server.py              # Server demo script
├── mcp_client_utils.py        # Primary Python client for testing (RECOMMENDED)
├── simple_client.py           # Simple Python client example
├── http_client_test.py        # Comprehensive HTTP client test
├── PYTHON_CLIENT_GUIDE.md     # Detailed Python client usage guide
├── HELLO_WORLD_MCP.md         # MCP server documentation
├── pyproject.toml             # Project configuration and dependencies
├── .cursorrules               # Development guidelines and best practices
└── src/incident_agent/        # Main application source
    ├── __init__.py           # Package initialization
    ├── server/               # MCP server implementation
    │   ├── __init__.py
    │   └── server.py         # FastMCP server definition
    └── tools/                # MCP tools implementation
        ├── __init__.py
        └── hello_tools.py    # Hello world tools
```

### Key Files

- **`main.py`** - MCP server entry point, use with `fastmcp run`
- **`mcp_client_utils.py`** - **RECOMMENDED** Python client with utility functions and classes for testing
- **`simple_client.py`** - Minimal client example for reference
- **`src/incident_agent/server/server.py`** - Core server implementation
- **`src/incident_agent/tools/hello_tools.py`** - Tool implementations

## Troubleshooting

### Common Issues

1. **"Failed to connect to localhost" error**
   - Make sure the server is running: `uv run fastmcp run main.py --transport http --port 8000`
   - Check if port 8000 is available: `lsof -i :8000`

2. **curl requests don't work**
   - Use Python client instead (recommended): `uv run python mcp_client_utils.py`
   - HTTP API with curl requires complex session management

3. **"No such file or directory" error**
   - Make sure you're in the project directory
   - Run `uv sync` to install dependencies

4. **Import errors**
   - Ensure virtual environment is activated by using `uv run` prefix
   - Check that FastMCP is installed: `uv run python -c "import fastmcp; print('OK')"`

### Getting Help

- Check `PYTHON_CLIENT_GUIDE.md` for detailed client usage
- Check `HELLO_WORLD_MCP.md` for server implementation details
- See `.cursorrules` for development guidelines

## Contributing

This project follows FastMCP development best practices. See `.cursorrules` for detailed development guidelines.
