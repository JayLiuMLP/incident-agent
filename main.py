"""
Main entry point for the Incident Agent MCP Server.
"""

from src.server.server import create_server

# Create the server instance for FastMCP CLI
mcp = create_server()


def main():
    """Create and return the MCP server for external usage."""
    print("Creating Incident Agent MCP Server...")
    print(f"✅ Server '{mcp.name}' created successfully!")
    return mcp


if __name__ == "__main__":
    # When run directly, just create the server
    server = main()
    print("💡 To run the server, use: uv run fastmcp run main.py")
    print("💡 Or use: python run_server.py for a demo")
