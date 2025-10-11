# Python Client Connection Guide

## Overview

This guide demonstrates how to use Python clients to connect to an MCP server running on localhost.

## Prerequisites

Ensure the MCP server is running:

```bash
uv run fastmcp run main.py --transport http --port 8000
```

## Method 1: Simple Client (`simple_client.py`)

The simplest connection method, suitable for quick testing:

```python
import asyncio
from fastmcp.client import Client
from fastmcp.client.transports import StreamableHttpTransport

async def call_mcp_tools():
    server_url = "http://localhost:8000/mcp"
    transport = StreamableHttpTransport(server_url)
    
    async with Client(transport=transport) as client:
        # Call tools
        result = await client.call_tool("hello", {"name": "user"})
        print(result.content[0].text)

asyncio.run(call_mcp_tools())
```

**Run:**

```bash
uv run python simple_client.py
```

## Method 2: Utility Class Wrapper (`mcp_client_utils.py`)

More convenient wrapper that can be reused in other projects:

```python
from mcp_client_utils import MCPClient, say_hello, echo_message

# Approach A: Using convenience functions
async def example1():
    result = await say_hello("John")
    echo = await echo_message("test message")
    
# Approach B: Using client class
async def example2():
    client = MCPClient()
    tools = await client.list_tools()
    result = await client.call_tool("hello", {"name": "Jane"})
```

**Run:**

```bash
uv run python mcp_client_utils.py
```

## Using in Your Own Code

### Import and Use Utility Classes

```python
import asyncio
from mcp_client_utils import MCPClient

async def my_app():
    client = MCPClient("http://localhost:8000/mcp")
    
    # Get available tools
    tools = await client.list_tools()
    print(f"Available tools: {tools}")
    
    # Call tools
    greeting = await client.call_tool("hello", {"name": "my application"})
    echo_result = await client.call_tool("echo", {"message": "Hello MCP!"})
    
    # Get server information
    server_info = await client.get_server_info()
    print(f"Server version: {server_info['version']}")

# Run your application
asyncio.run(my_app())
```

### Using in Jupyter Notebook

```python
# In Jupyter cells
import asyncio
from mcp_client_utils import say_hello, echo_message

# Direct async function calls
result = await say_hello("Jupyter user")
print(result)

# Or in synchronous environment
result = asyncio.run(say_hello("sync user"))
print(result)
```

## Available Tools

Based on your MCP server, the following tools are available:

1. **hello** - Greeting tool

   ```python
   result = await client.call_tool("hello", {"name": "username"})
   ```

2. **echo** - Echo tool

   ```python
   result = await client.call_tool("echo", {"message": "message to echo"})
   ```

3. **server_info** - Server information

   ```python
   result = await client.call_tool("server_info", {})
   ```

## Troubleshooting

### Connection Failures

- Ensure server is running: `ps aux | grep fastmcp`
- Check port: `lsof -i :8000`
- Restart server: `uv run fastmcp run main.py --transport http --port 8000`

### Endpoint Issues

The client automatically tests the following endpoints:

- `http://localhost:8000/mcp`
- `http://localhost:8000/mcp/`
- `http://localhost:8000`

### Common Errors

1. **Connection refused**: Server not started
2. **404 error**: Incorrect endpoint path
3. **Timeout**: Server responding slowly, increase timeout

## Integrate Into Your Project

Copy `mcp_client_utils.py` to your project, then:

```python
from mcp_client_utils import MCPClient

# In your application initialization
mcp_client = MCPClient()

# Call where needed
async def some_function():
    result = await mcp_client.call_tool("hello", {"name": "user"})
    return result
```

Now you can easily connect and use your MCP server in any Python application! 🚀
