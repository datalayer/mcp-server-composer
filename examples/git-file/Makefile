.PHONY: help install start stop clean

# Default target
help:
	@echo "Git-File MCP Server Composer Example - Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  install      - Install mcp-server-composer and MCP servers"
	@echo "  start        - Start the MCP Server Composer (manages both servers)"
	@echo "  stop         - Stop the MCP Server Composer"
	@echo "  clean        - Clean up temporary files"
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

# Start the MCP Server Composer
start:
	@echo "Starting MCP Server Composer..."
	@echo ""
	mcp-server-composer serve --config mcp_server_composer.toml

# Stop the composer (use Ctrl+C in the terminal where it's running)
stop:
	@echo "To stop the composer, press Ctrl+C in the terminal where it's running"

# Clean up
clean:
	@echo "Cleaning up..."
	@rm -f *.log nohup.out
	@rm -f .composer.pid composer.log
	@echo "✓ Cleanup complete"
