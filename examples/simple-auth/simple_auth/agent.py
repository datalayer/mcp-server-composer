#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pydantic AI Agent with MCP Server Tools

This agent demonstrates how to use pydantic-ai with an authenticated MCP server.

Features:
- OAuth2 authentication with GitHub (via shared oauth_client)
- Connection to MCP server with Bearer token authentication
- Interactive CLI interface powered by pydantic-ai
- Access to all MCP server tools (calculator, greeter, server_info)
- Uses Anthropic Claude Sonnet 4.5 model

Usage:
    python agent.py
    
    # Or via the Makefile:
    make agent

Learning Objectives:
1. Integrate pydantic-ai Agent with MCP servers
2. Handle OAuth2 authentication for AI agents
3. Use MCPServerSSE with authentication headers
4. Build interactive CLI agents with pydantic-ai
"""

import sys
import io
import asyncio
import httpx

# Import shared OAuth client
from .oauth_client import OAuthClient

# Pydantic AI imports
try:
    from pydantic_ai import Agent
    from pydantic_ai.mcp import MCPServerSSE
    HAS_PYDANTIC_AI = True
except ImportError:
    HAS_PYDANTIC_AI = False
    print("❌ Error: pydantic-ai not installed")
    print("   Install with: pip install 'pydantic-ai[mcp]'")
    sys.exit(1)


def authenticate() -> tuple[str, str]:
    """
    Perform OAuth2 authentication and return token and server URL
    
    Returns:
        Tuple of (access_token, server_url)
    
    Raises:
        SystemExit: If authentication fails
    """
    print("\n" + "=" * 70)
    print("🤖 Pydantic AI Agent with Authenticated MCP Server")
    print("=" * 70)
    print("\nBefore we start, we need to authenticate with the MCP server.")
    print("This will open a browser for GitHub OAuth authentication.\n")
    
    # Create OAuth client (verbose mode for user feedback)
    oauth = OAuthClient("config.json", verbose=True)
    
    # Perform authentication (includes metadata discovery)
    if not oauth.authenticate():
        print("\n❌ Authentication failed!")
        print("   Make sure the MCP server is running on port 8080")
        print("   (Run: make server)")
        sys.exit(1)
    
    # Get the token and server URL
    token = oauth.get_token()
    server_url = oauth.get_server_url()
    
    if not token:
        print("\n❌ Failed to obtain access token")
        sys.exit(1)
    
    print("\n✅ Authentication successful!")
    return token, server_url


def create_agent(access_token: str, server_url: str) -> tuple[Agent, httpx.AsyncClient]:
    """
    Create a pydantic-ai Agent connected to the authenticated MCP server
    
    Args:
        access_token: OAuth2 access token for authentication
        server_url: MCP server base URL
    
    Returns:
        Configured pydantic-ai Agent
        
    Note:
        The httpx client will be managed by pydantic-ai's internal lifecycle.
        Do NOT close it manually as it will be reused across multiple agent runs.
    """
    print("\n" + "=" * 70)
    print("🏗️  Creating AI Agent with MCP Tools")
    print("=" * 70)
    
    # Create HTTP client with authentication
    # IMPORTANT: Don't close this client - pydantic-ai manages it
    # Use default httpx client settings which work well with long-lived connections
    http_client = httpx.AsyncClient(
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=httpx.Timeout(connect=10.0, read=300.0, write=10.0, pool=5.0),
        # These settings are crucial for keeping connections alive
        http2=False,  # Disable HTTP/2 for better SSE compatibility
        follow_redirects=True,
        limits=httpx.Limits(
            max_keepalive_connections=10,
            max_connections=20,
            keepalive_expiry=30.0
        )
    )
    
    print(f"\n📡 Connecting to MCP server: {server_url}/sse")
    print("   Using Bearer token authentication")
    
    # Create MCP server connection with SSE transport
    # The pydantic-ai Agent will handle the lifecycle via __aenter__/__aexit__
    mcp_server = MCPServerSSE(
        url=f"{server_url}/sse",
        http_client=http_client,
        # Increase read timeout for long-running tool calls
        read_timeout=300.0,  # 5 minutes
        # Allow retries for transient failures
        max_retries=2
    )
    
    print("\n🤖 Initializing Agent with Anthropic Claude Sonnet 4.5")
    
    # Create Agent with Anthropic Claude Sonnet 4.5
    # The agent will have access to all tools from the MCP server
    agent = Agent(
        model='anthropic:claude-sonnet-4-0',
        toolsets=[mcp_server],
        system_prompt="""You are a helpful AI assistant with access to MCP server tools.

Available tools:
- calculator_add: Add two numbers
- calculator_multiply: Multiply two numbers
- greeter_hello: Greet someone
- greeter_goodbye: Say goodbye to someone
- get_server_info: Get information about the MCP server

When users ask you to perform calculations or greetings, use the appropriate tools.
Be friendly and explain what you're doing."""
    )
    
    print("✅ Agent created successfully!")
    print("\n📦 The agent has access to the following MCP server tools:")
    print("   • calculator_add - Add two numbers")
    print("   • calculator_multiply - Multiply two numbers")
    print("   • greeter_hello - Greet someone")
    print("   • greeter_goodbye - Say goodbye to someone")
    print("   • get_server_info - Get server information")
    
    return agent, http_client


def main():
    """Main entry point for the AI agent"""
    # Ensure UTF-8 encoding for emoji support
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    agent = None
    http_client = None
    try:
        # Step 1: Authenticate with OAuth2
        access_token, server_url = authenticate()
        
        # Step 2: Create agent with MCP server connection
        agent, http_client = create_agent(access_token, server_url)
        
        # Step 3: Launch interactive CLI
        print("\n" + "=" * 70)
        print("🚀 Launching Interactive CLI")
        print("=" * 70)
        print("\nYou can now chat with the AI agent!")
        print("The agent has access to the MCP server tools.")
        print("\nCommands:")
        print("  /exit     - Exit the CLI")
        print("  /markdown - Toggle markdown rendering")
        print("  /multiline - Enter multiline mode")
        print("  /cp       - Copy last response to clipboard")
        print("\nExamples:")
        print("  'What is 15 + 27?'")
        print("  'Multiply 8 by 9'")
        print("  'Say hello to Alice'")
        print("  'What can you tell me about the server?'")
        print("\n" + "=" * 70 + "\n")
        
        # Launch the CLI interface
        # The agent manages the MCP server lifecycle internally
        async def _run_cli() -> None:
            assert agent is not None
            async with agent:
                await agent.to_cli()

        try:
            asyncio.run(_run_cli())
        except BaseExceptionGroup as exc:
            print("\n❌ Encountered errors while running the CLI:")
            for idx, sub_exc in enumerate(exc.exceptions, start=1):
                print(f"  [{idx}] {type(sub_exc).__name__}: {sub_exc}")
            raise
        finally:
            if http_client is not None:
                try:
                    asyncio.run(http_client.aclose())
                except RuntimeError:
                    # Event loop already closed, create a new one for cleanup
                    loop = asyncio.new_event_loop()
                    loop.run_until_complete(http_client.aclose())
                    loop.close()
    
    except KeyboardInterrupt:
        print("\n\n🛑 Agent stopped by user")
    except FileNotFoundError:
        print("\n❌ Error: config.json not found")
        print("   Please create config.json with your GitHub OAuth credentials")
        print("   See the example in examples/mcp_server_composer.toml")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
