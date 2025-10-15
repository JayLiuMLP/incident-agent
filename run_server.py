#!/usr/bin/env python3
"""
Entry point script to run the Incident Agent MCP Server.
"""

import asyncio
import sys
from src.server import server


async def main():
    """
    Run the Incident Agent MCP server.
    """
    print("🚀 Starting Incident Agent MCP Server...")
    print("Server Name: incident-agent")
    print("Description: A simple hello world MCP server for incident management")
    print("\nAvailable Tools:")
    print("  - hello: Say hello to someone or the world")
    print("  - echo: Echo back the provided message") 
    print("  - server_info: Get information about this MCP server")
    print("\nAvailable Resources:")
    print("  - config://server/info: Server configuration information")
    print("\n" + "="*50)
    
    try:
        # For now, just show that the server can be created
        print(f"✅ Server created successfully: {server.name}")
        print("🎉 Hello World MCP Server is ready!")
        print("\nTo use this server with an MCP client:")
        print("  - Use FastMCP CLI: uv run fastmcp run run_server.py")
        print("  - Or integrate with Claude Desktop or other MCP clients")
        
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
