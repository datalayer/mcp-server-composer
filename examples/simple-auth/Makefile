.PHONY: help install server client test clean

# Default target
help:
	@echo "MCP Server with GitHub OAuth - Available targets:"
	@echo ""
	@echo "  make install    - Install Python dependencies"
	@echo "  make server     - Start the MCP server (port 8080)"
	@echo "  make client     - Run the MCP client demo"
	@echo "  make test       - Run tests"
	@echo "  make clean      - Remove Python cache files"
	@echo ""
	@echo "Quick start:"
	@echo "  1. Configure config.json with GitHub OAuth credentials"
	@echo "  2. make install"
	@echo "  3. make server    (in one terminal)"
	@echo "  4. make client    (in another terminal)"

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt
	@echo "✅ Dependencies installed"

# Run the MCP server
server:
	@echo "🚀 Starting MCP server on http://localhost:8080..."
	python -m simple_auth server

# Run the MCP client
client:
	@echo "🔐 Starting MCP client..."
	python -m simple_auth client

# Run tests
test:
	@echo "🧪 Running tests..."
	python -m pytest tests/test_auth.py -v || python tests/test_auth.py

# Clean Python cache files
clean:
	@echo "🧹 Cleaning cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleaned"
