"""
Hello World tools for the Incident Agent MCP server.
"""

from typing import Optional
from fastmcp import Context


async def hello_world(name: Optional[str] = None, ctx: Context = None) -> str:
    """
    Return a hello world greeting.
    
    Args:
        name: Optional name to greet. Defaults to "World".
        ctx: FastMCP context for logging.
        
    Returns:
        A greeting message.
    """
    if ctx:
        await ctx.info(f"Generating hello greeting for: {name or 'World'}")
    
    greeting_name = name or "World"
    return f"Hello, {greeting_name}! 🌍 Welcome to the Incident Agent MCP Server!"


async def echo_message(message: str, ctx: Context = None) -> str:
    """
    Echo back the provided message.
    
    Args:
        message: The message to echo back.
        ctx: FastMCP context for logging.
        
    Returns:
        The same message with a prefix.
    """
    if ctx:
        await ctx.info(f"Echoing message: {message}")
    
    return f"Echo: {message}"


async def get_server_info(ctx: Context = None) -> dict:
    """
    Get basic information about the server.
    
    Args:
        ctx: FastMCP context for logging.
        
    Returns:
        Server information dictionary.
    """
    if ctx:
        await ctx.info("Providing server information")
    
    return {
        "name": "Incident Agent MCP Server",
        "version": "0.1.0",
        "description": "A simple hello world MCP server for incident management",
        "capabilities": ["greeting", "echo", "server_info"],
        "status": "running"
    }
