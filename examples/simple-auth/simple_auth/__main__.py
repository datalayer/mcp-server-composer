"""
MCP Server and Client with GitHub OAuth2 Authentication

Run the server with:
    python -m simple_auth server

Run the client with:
    python -m simple_auth client

Run the pydantic-ai agent with:
    python -m simple_auth agent

Or run directly:
    python -m simple_auth.server
    python -m simple_auth.client
    python -m simple_auth.agent
"""

import sys


def main():
    """Main entry point for the package"""
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nUsage:")
        print("  python -m simple_auth server    # Run the MCP server")
        print("  python -m simple_auth client    # Run the MCP client demo")
        print("  python -m simple_auth agent     # Run the pydantic-ai agent CLI")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "server":
        from simple_auth.server import main as server_main
        server_main()
    elif command == "client":
        from simple_auth.client import main as client_main
        client_main()
    elif command == "agent":
        from simple_auth.agent import main as agent_main
        agent_main()
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
