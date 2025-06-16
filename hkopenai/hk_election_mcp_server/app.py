import argparse
from fastmcp import FastMCP
from hkopenai.hk_election_mcp_server import tool_gc_registered_electors
from typing import Dict, List, Annotated, Optional
from pydantic import Field


def create_mcp_server():
    """Create and configure the MCP server"""
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


def main():
    parser = argparse.ArgumentParser(description="HKO MCP Server")
    parser.add_argument(
        "-s", "--sse", action="store_true", help="Run in SSE mode instead of stdio"
    )
    args = parser.parse_args()

    server = create_mcp_server()

    if args.sse:
        server.run(transport="streamable-http")
        print("HKO MCP Server running in SSE mode on port 8000")
    else:
        server.run()
        print("HKO MCP Server running in stdio mode")


if __name__ == "__main__":
    main()
