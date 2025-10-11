#!/usr/bin/env python3
"""
MCP Client Utility Functions - Can be imported and used in other scripts
"""

import asyncio
import json
from typing import Dict, Any, Optional, List
from fastmcp.client import Client
from fastmcp.client.transports import StreamableHttpTransport


class MCPClient:
    """Simple MCP client wrapper class"""
    
    def __init__(self, server_url: str = "http://localhost:8000/mcp"):
        self.server_url = server_url
        self.transport = StreamableHttpTransport(server_url)
    
    async def call_tool(self, tool_name: str, arguments: Optional[Dict[str, Any]] = None) -> str:
        """Call the specified tool"""
        if arguments is None:
            arguments = {}
        
        async with Client(transport=self.transport) as client:
            result = await client.call_tool(tool_name, arguments)
            return result.content[0].text
    
    async def list_tools(self) -> List[str]:
        """Get a list of all available tools"""
        async with Client(transport=self.transport) as client:
            tools = await client.list_tools()
            return [tool.name for tool in tools]
    
    async def get_server_info(self) -> Dict[str, Any]:
        """Get server information"""
        result = await self.call_tool("server_info")
        return json.loads(result)


# Convenience functions
async def say_hello(name: str = "World") -> str:
    """Say hello to the specified person"""
    client = MCPClient()
    return await client.call_tool("hello", {"name": name})


async def echo_message(message: str) -> str:
    """Echo back a message"""
    client = MCPClient()
    return await client.call_tool("echo", {"message": message})


async def get_server_status() -> Dict[str, Any]:
    """Get server status information"""
    client = MCPClient()
    return await client.get_server_info()


# Demo usage
async def demo():
    """Demonstrate how to use these functions"""
    print("🚀 MCP Client Tools Demo")
    
    # Using convenience functions
    hello_result = await say_hello("Developer")
    print(f"Hello: {hello_result}")
    
    echo_result = await echo_message("This is a test message")
    print(f"Echo: {echo_result}")
    
    server_info = await get_server_status()
    print(f"Server status: {server_info['status']}")
    print(f"Server version: {server_info['version']}")
    
    # Using client class
    client = MCPClient()
    
    tools = await client.list_tools()
    print(f"Available tools: {tools}")


if __name__ == "__main__":
    # Run demo
    asyncio.run(demo())
