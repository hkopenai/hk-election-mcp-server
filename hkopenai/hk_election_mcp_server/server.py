"""
Module for creating and running the HK OpenAI Election MCP Server.

This module provides functionality to set up a FastMCP server with tools related to
Hong Kong election data, specifically for retrieving registered electors in geographical
constituencies.
"""

from fastmcp import FastMCP
from hkopenai.hk_election_mcp_server import tool_gc_registered_electors


def create_mcp_server():
    """
    Create and configure the MCP server.
    
    Returns:
        FastMCP: Configured MCP server instance with election data tools.
    """
    mcp = FastMCP(name="HK OpenAI election Server")

    tool_gc_registered_electors.register(mcp)

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
