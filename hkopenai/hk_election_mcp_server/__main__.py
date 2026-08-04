"""
Console-script entry point for hkopenai.hk_election_mcp_server.
"""

from hkopenai_common.cli_utils import cli_main
from .server import server


def main():
    """Console-script entry point for the hk election mcp server."""
    cli_main(server, "hk election mcp server")


if __name__ == "__main__":
    main()
