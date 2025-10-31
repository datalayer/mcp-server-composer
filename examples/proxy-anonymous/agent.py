#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pydantic AI Agent with MCP Server Composer

This agent demonstrates how to connect a pydantic-ai agent to the MCP Server Composer.
The composer manages multiple MCP servers and exposes them through a unified endpoint.

Features:
- Connection to MCP Server Composer via SSE transport
- Interactive CLI interface powered by pydantic-ai
- Access to Calculator and Echo server tools through the composer
- Uses Anthropic Claude Sonnet 4.5 model

Usage:
    # First start the composer server:
    make start
    
    # Then in another terminal, run the agent:
    python agent.py

Learning Objectives:
1. Integrate pydantic-ai Agent with MCP Server Composer
2. Access multiple MCP servers through a unified interface
3. Build interactive CLI agents with pydantic-ai

Servers:
- Calculator Server (mcp1.py): add, subtract, multiply, divide
- Echo Server (mcp2.py): ping, echo, reverse, uppercase, lowercase, count_words
"""

import sys
import io
import asyncio

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


def create_agent(server_url: str = "http://localhost:8080") -> Agent:
    """
    Create a pydantic-ai Agent connected to the MCP Server Composer
    
    Args:
        server_url: MCP Server Composer base URL
    
    Returns:
        Configured pydantic-ai Agent
    """
    print("\n" + "=" * 70)
    print("🤖 Pydantic AI Agent with MCP Server Composer")
    print("=" * 70)
    
    print(f"\n📡 Connecting to MCP Server Composer: {server_url}/sse")
    print("   Unified access to Calculator and Echo servers")
    
    # Create MCP server connection with SSE transport
    # No authentication required for this example
    mcp_server = MCPServerSSE(
        url=f"{server_url}/sse",
        # Increase read timeout for long-running tool calls
        read_timeout=300.0,  # 5 minutes
        # Allow retries for transient failures
        max_retries=2
    )
    
    print("\n🤖 Initializing Agent with Anthropic Claude Sonnet 4.5")
    
    # Create Agent with Anthropic Claude Sonnet 4.5
    # The agent will have access to all tools from both servers
    agent = Agent(
        model='anthropic:claude-sonnet-4-0',
        toolsets=[mcp_server],
        system_prompt="""You are a helpful AI assistant with access to Calculator and Echo MCP server tools.

The tools are provided by two MCP servers managed by the composer:
- Calculator server: Math operations (calculator:add, calculator:subtract, calculator:multiply, calculator:divide)
- Echo server: String operations (echo:ping, echo:echo, echo:reverse, echo:uppercase, echo:lowercase, echo:count_words)

Tool names are prefixed with their server name to avoid conflicts.

When users ask you to perform calculations or string operations, use the appropriate tools.
Be friendly and explain what you're doing."""
    )
    
    print("✅ Agent created successfully!")
    print("\n📦 The agent has access to tools from:")
    print("   • Calculator Server - Math operations")
    print("   • Echo Server - String operations")
    print("\n   Tool names are prefixed (e.g., calculator:add, echo:reverse)")
    
    return agent


def main():
    """Main entry point for the AI agent"""
    # Ensure UTF-8 encoding for emoji support
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    try:
        print("\n" + "=" * 70)
        print("🚀 MCP Server Composer Agent")
        print("=" * 70)
        print("\n⚠️  IMPORTANT: Make sure the MCP Server Composer is running!")
        print("   Run in another terminal: make start")
        print("\nConnecting to server at http://localhost:8080...")
        
        # Create agent with MCP server connection
        agent = create_agent()
        
        # Launch interactive CLI
        print("\n" + "=" * 70)
        print("🚀 Launching Interactive CLI")
        print("=" * 70)
        print("\nYou can now chat with the AI agent!")
        print("The agent has access to Calculator and Echo server tools.")
        print("\nCommands:")
        print("  /exit     - Exit the CLI")
        print("  /markdown - Toggle markdown rendering")
        print("  /multiline - Enter multiline mode")
        print("  /cp       - Copy last response to clipboard")
        print("\nExamples:")
        print("  'What is 15 plus 27?'")
        print("  'Multiply 8 by 9'")
        print("  'Reverse the text hello world'")
        print("  'Convert Python to uppercase'")
        print("  'How many words are in the quick brown fox'")
        print("\n" + "=" * 70 + "\n")
        
        # Launch the CLI interface
        async def _run_cli() -> None:
            assert agent is not None
            async with agent:
                await agent.to_cli()

        asyncio.run(_run_cli())
    
    except KeyboardInterrupt:
        print("\n\n🛑 Agent stopped by user")
    except BaseExceptionGroup as exc:
        print("\n❌ Encountered errors while running the CLI:")
        for idx, sub_exc in enumerate(exc.exceptions, start=1):
            print(f"  [{idx}] {type(sub_exc).__name__}: {sub_exc}")
        raise
    except ConnectionError as e:
        print(f"\n❌ Connection Error: {e}")
        print("   Make sure the MCP Server Composer is running on port 8080")
        print("   (Run: make start in another terminal)")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
