"""
MCP Server and Client with GitHub OAuth2 Authentication

Run the server with:
    python -m simple_auth server

Run the client with:
    python -m simple_auth client

Or run directly:
    python -m simple_auth.server
    python -m simple_auth.client
"""

import sys


def main():
    """Main entry point for the package"""
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nUsage:")
        print("  python -m simple_auth server    # Run the MCP server")
        print("  python -m simple_auth client    # Run the MCP client")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "server":
        from simple_auth.server import main as server_main
        server_main()
    elif command == "client":
        from simple_auth.client import main as client_main
        client_main()
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
