"""
Incident Agent - A FastMCP-based server for handling incident management tasks.
"""

__version__ = "0.1.0"
__author__ = "Incident Agent Team"

from .server.server import create_server

__all__ = ["create_server"]
