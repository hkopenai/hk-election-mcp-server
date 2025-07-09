"""
Module for creating and running the HK OpenAI Election MCP Server.

This module provides functionality to set up a FastMCP server with tools related to
Hong Kong election data, specifically for retrieving registered electors in geographical
constituencies.
"""

import argparse
from fastmcp import FastMCP
from hkopenai.hk_election_mcp_server import tool_gc_registered_electors
from typing import Dict, List, Annotated, Optional
from pydantic import Field


def create_mcp_server():
    """
    Create and configure the MCP server.
    
    Returns:
        FastMCP: Configured MCP server instance with election data tools.
    """
    mcp = FastMCP(name="HK OpenAI election Server")

    @mcp.tool(
        description="Get the number of registered electors in Hong Kong's geographical constituencies by year range",
    )
    def get_gc_registered_electors(
        start_year: Annotated[int, Field(description="Start year for data range")],
        end_year: Annotated[int, Field(description="End year for data range")],
    ) -> Dict:
        return tool_gc_registered_electors.get_gc_registered_electors(
            start_year, end_year
        )

    return mcp


def main(args):
    """
    Main function to run the MCP Server.
    
    Args:
        args: Command line arguments passed to the function.
    """
    server = create_mcp_server()

    if args.sse:
        server.run(transport="streamable-http", host=args.host, port=args.port)
        print(f"MCP Server running in SSE mode on port {args.port}, bound to {args.host}")
    else:
        server.run()
        print("MCP Server running in stdio mode")


if __name__ == "__main__":
    main()
