"""
Module for creating and running the HK OpenAI Election MCP Server.

This module provides functionality to set up a FastMCP server with tools related to
Hong Kong election data, specifically for retrieving registered electors in geographical
constituencies.
"""

from fastmcp import FastMCP
from .tools import gc_registered_electors


def server():
    """
    Create and configure the MCP server.

    Returns:
        FastMCP: Configured MCP server instance with election data tools.
    """
    mcp = FastMCP(name="HK OpenAI election Server")

    gc_registered_electors.register(mcp)

    return mcp
