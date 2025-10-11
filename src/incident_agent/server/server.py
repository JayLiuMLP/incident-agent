"""
Main FastMCP server for the Incident Agent.

This module creates a simple hello world MCP server with basic tools.
"""

from fastmcp import FastMCP
from ..tools.hello_tools import hello_world, echo_message, get_server_info


def create_server() -> FastMCP:
    """
    Create and configure the Incident Agent MCP server.
    
    Returns:
        Configured FastMCP server instance.
    """
    # Create FastMCP server instance
    mcp = FastMCP("incident-agent")
    
    # Register tools using decorators
    @mcp.tool
    async def hello(name: str = "World") -> str:
        """Say hello to someone or the world."""
        return await hello_world(name)
    
    @mcp.tool
    async def echo(message: str) -> str:
        """Echo back the provided message."""
        return await echo_message(message)
    
    @mcp.tool
    async def server_info() -> dict:
        """Get information about this MCP server."""
        return await get_server_info()
    
    # Register a simple resource
    @mcp.resource("config://server/info")
    async def server_config() -> dict:
        """Provide server configuration information."""
        return {
            "server_name": "incident-agent",
            "version": "0.1.0",
            "description": "Hello World MCP Server",
            "tools_available": ["hello", "echo", "server_info"],
            "resources_available": ["config://server/info"]
        }
    
    return mcp


# Create the server instance for direct usage
server = create_server()

if __name__ == "__main__":
    # Run the server directly
    import asyncio
    from fastmcp.utilities.testing import test_server
    
    async def main():
        """Test the server locally."""
        print("🚀 Starting Incident Agent MCP Server...")
        print("Available tools: hello, echo, server_info")
        print("Available resources: config://server/info")
        
        # Simple test of our server
        await test_server(server)
    
    asyncio.run(main())
