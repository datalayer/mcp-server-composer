.PHONY: help install install-agent start agent stop clean

# Default target
help:
	@echo "Git-File MCP Server Composer Example - Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  install        - Install mcp-server-composer and MCP servers"
	@echo "  install-agent  - Install pydantic-ai for agent support"
	@echo "  start          - Start the MCP Server Composer (manages both servers)"
	@echo "  agent          - Run the AI agent (requires composer to be running)"
	@echo "  stop           - Stop the MCP Server Composer"
	@echo "  clean          - Clean up temporary files"
	@echo ""

# Install dependencies
install:
	@echo "Installing mcp-server-composer..."
	pip install -e ../..
	@echo ""
	@echo "Installing MCP servers..."
	pip install mcp-server-git mcp-server-filesystem
	@echo ""
	@echo "✓ Installation complete!"
	@echo ""
	@echo "To start:"
	@echo "  make start"
	@echo ""
	@echo "To use the AI agent:"
	@echo "  make install-agent"
	@echo "  make agent"

# Install pydantic-ai for agent support
install-agent:
	@echo "Installing pydantic-ai with MCP support..."
	pip install 'pydantic-ai[mcp]'
	@echo ""
	@echo "✓ Agent dependencies installed!"
	@echo ""
	@echo "Usage:"
	@echo "  1. Start composer: make start"
	@echo "  2. In another terminal: make agent"

# Start the MCP Server Composer
start:
	@echo "Starting MCP Server Composer..."
	@echo ""
	mcp-server-composer serve --config mcp_server_composer.toml

# Run the AI agent
agent:
	@echo "Starting AI Agent..."
	@echo ""
	@echo "⚠️  Make sure the MCP Server Composer is running!"
	@echo "   (Run 'make start' in another terminal)"
	@echo ""
	python agent.py

# Stop the composer (use Ctrl+C in the terminal where it's running)
stop:
	@echo "To stop the composer, press Ctrl+C in the terminal where it's running"

# Clean up
clean:
	@echo "Cleaning up..."
	@rm -f *.log nohup.out
	@rm -f .composer.pid composer.log
	@echo "✓ Cleanup complete"
