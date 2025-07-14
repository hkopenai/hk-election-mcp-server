"""
Main entry point for the HK OpenAI Election MCP Server.

This module serves as the entry point to run the MCP server application.
"""



from hkopenai_common.cli_utils import cli_main
from .server import create_mcp_server

if __name__ == "__main__":
    cli_main(create_mcp_server, "HK Election MCP Server")
