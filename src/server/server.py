"""
Main FastMCP server for the Incident Agent.

This module creates a simple hello world MCP server with basic tools.
"""

from fastmcp import FastMCP
from ..tools.hello_tools import hello_world, echo_message, get_server_info
from ..tools.pagerduty_tools import get_latest_incidents, get_incident_summary, search_incidents


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
    
    # PagerDuty incident management tools
    @mcp.tool
    async def get_current_incidents(limit: int = 5, status: str = "all") -> dict:
        """
        Get current PagerDuty incidents.
        
        Args:
            limit: Maximum number of incidents to return (default: 5)
            status: Filter by status - 'open', 'resolved', or 'all' (default: 'all')
        """
        status_filter = None if status == "all" else status
        return await get_latest_incidents(limit=limit, status_filter=status_filter)
    
    @mcp.tool
    async def get_incident_stats(days: int = 7) -> dict:
        """
        Get PagerDuty incident statistics and summary.
        
        Args:
            days: Number of days to look back (default: 7)
        """
        return await get_incident_summary(days=days)
    
    @mcp.tool 
    async def find_incidents(query: str, limit: int = 10, days: int = 30) -> dict:
        """
        Search for PagerDuty incidents by title/description.
        
        Args:
            query: Search term to look for in incident titles
            limit: Maximum number of results (default: 10)
            days: Number of days to search back (default: 30)
        """
        return await search_incidents(query=query, limit=limit, days=days)
    
    # Register resources
    @mcp.resource("config://server/info")
    async def server_config() -> dict:
        """Provide server configuration information."""
        return {
            "server_name": "incident-agent",
            "version": "0.1.0",
            "description": "Incident Agent MCP Server with PagerDuty Integration",
            "tools_available": [
                "hello", "echo", "server_info",
                "get_current_incidents", "get_incident_stats", "find_incidents"
            ],
            "resources_available": ["config://server/info", "pagerduty://incidents/latest"]
        }
    
    @mcp.resource("pagerduty://incidents/latest") 
    async def latest_incidents_resource() -> dict:
        """Resource providing latest PagerDuty incidents."""
        result = await get_latest_incidents(limit=10, status_filter="open")
        return {
            "resource_type": "pagerduty_incidents",
            "data": result,
            "last_updated": result.get("query_time", "unknown")
        }
    
    return mcp


# Create the server instance for direct usage
server = create_server()

if __name__ == "__main__":
    # Run the server directly
    import asyncio
    
    async def main():
        """Test the server locally."""
        print("🚀 Starting Incident Agent MCP Server...")
        print("📋 Available tools:")
        print("   • hello - Say hello")
        print("   • echo - Echo messages")  
        print("   • server_info - Get server information")
        print("   🎫 PagerDuty Tools:")
        print("   • get_current_incidents - Get latest incidents")
        print("   • get_incident_stats - Get incident statistics")
        print("   • find_incidents - Search incidents")
        print("📦 Available resources:")
        print("   • config://server/info - Server configuration")
        print("   • pagerduty://incidents/latest - Latest incidents")
        
        print("\n✅ Server configured successfully!")
        print("🔗 To connect with a client, use the server instance.")
        print("📚 Example usage:")
        print("   result = await server.call_tool('get_current_incidents', {'limit': 3})")
    
    asyncio.run(main())
