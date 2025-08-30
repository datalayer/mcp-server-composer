# MCP Server Composer

A generic Python library for composing Model Context Protocol (MCP) servers based on dependencies defined in `pyproject.toml` files.

## Overview

The MCP Server Composer automatically discovers MCP server packages from your project dependencies and composes them into a unified server instance. This enables powerful combinations of MCP tools and prompts from multiple sources without manual integration.

## Features

- **Automatic Discovery**: Finds MCP servers in your `pyproject.toml` dependencies
- **Intelligent Composition**: Combines tools, prompts, and resources from multiple servers
- **Conflict Resolution**: Handles naming conflicts with configurable strategies
- **CLI Interface**: Easy-to-use command-line tools
- **Comprehensive Testing**: Full test suite with 85% coverage
- **FastMCP Integration**: Built on the robust FastMCP framework

## Installation

```bash
pip install mcp-server-composer
```

## Quick Start

### Using the Library

```python
from mcp_server_composer import MCPServerComposer, ConflictResolution

# Create a composer
composer = MCPServerComposer(
    composed_server_name="my-unified-server",
    conflict_resolution=ConflictResolution.PREFIX
)

# Compose servers from pyproject.toml dependencies
unified_server = composer.compose_from_pyproject()

# Get composition summary
summary = composer.get_composition_summary()
print(f"Composed {summary['total_tools']} tools from {summary['source_servers']} servers")
```

### Using the CLI

```bash
# Discover MCP servers in dependencies
python -m mcp_server_composer discover

# Compose servers into a unified server
python -m mcp_server_composer compose

# Compose with specific options
python -m mcp_server_composer compose --name my-server --conflict-resolution prefix

# Compose only specific servers
python -m mcp_server_composer compose --include server1 server2 --exclude server3

# Output results as JSON
python -m mcp_server_composer discover --output-format json
```

## Detailed Usage

### CLI Commands

#### `discover` - Find MCP Servers

Analyzes your `pyproject.toml` to find and analyze MCP server dependencies:

```bash
# Basic discovery
python -m mcp_server_composer discover

# Specify custom pyproject.toml location
python -m mcp_server_composer discover --pyproject /path/to/pyproject.toml

# Output as JSON for programmatic use
python -m mcp_server_composer discover --output-format json
```

**Example Output:**
```
MCP Server Discovery Results
============================

Found 2 MCP servers:

📦 jupyter-mcp-server (v1.0.0)
   🔧 Tools: 5 (notebook_create, notebook_run, etc.)
   💬 Prompts: 2 (analyze_notebook, debug_code)
   📁 Resources: 1 (notebook_templates)

📦 earthdata-mcp-server (v0.1.0)
   🔧 Tools: 3 (search_datasets, download_granules, etc.)
   💬 Prompts: 1 (analyze_climate_data)
   📁 Resources: 0

Total: 8 tools, 3 prompts, 1 resource across 2 servers
```

#### `compose` - Create Unified Server

Combines multiple MCP servers into a single unified server:

```bash
# Basic composition
python -m mcp_server_composer compose

# Custom server name and conflict resolution
python -m mcp_server_composer compose \
  --name "my-unified-server" \
  --conflict-resolution prefix

# Include/exclude specific servers
python -m mcp_server_composer compose \
  --include jupyter-mcp-server earthdata-mcp-server \
  --exclude old-server

# Save composed server to file
python -m mcp_server_composer compose \
  --output composed_server.py \
  --output-format json
```

### Programmatic Usage

#### Basic Composition

```python
from mcp_server_composer import MCPServerComposer, ConflictResolution

# Create composer with custom settings
composer = MCPServerComposer(
    composed_server_name="unified-data-server",
    conflict_resolution=ConflictResolution.PREFIX
)

# Compose from current directory's pyproject.toml
unified_server = composer.compose_from_pyproject()

# Get detailed composition information
summary = composer.get_composition_summary()
print(f"Created server with {summary['total_tools']} tools")
```

#### Advanced Configuration

```python
from pathlib import Path
from mcp_server_composer import MCPServerComposer, ConflictResolution

# Specify custom pyproject.toml location
composer = MCPServerComposer(
    composed_server_name="my-server",
    conflict_resolution=ConflictResolution.SUFFIX
)

# Compose with filtering
unified_server = composer.compose_from_pyproject(
    pyproject_path=Path("custom/pyproject.toml"),
    include_servers=["jupyter-mcp-server", "earthdata-mcp-server"],
    exclude_servers=["deprecated-server"]
)

# Access composed tools and prompts
tools = composer.list_tools()
prompts = composer.list_prompts()
source_info = composer.get_source_info()

print(f"Tools: {', '.join(tools)}")
print(f"Sources: {', '.join(source_info.keys())}")
```

#### Discovery Only

```python
from mcp_server_composer import MCPServerDiscovery

# Discover MCP servers without composing
discovery = MCPServerDiscovery()
servers = discovery.discover_from_pyproject("pyproject.toml")

for name, info in servers.items():
    print(f"{name}: {len(info.tools)} tools, {len(info.prompts)} prompts")
```

## Configuration

### Conflict Resolution Strategies

When multiple servers provide tools or prompts with the same name, you can choose how to resolve conflicts:

- **PREFIX** (default): Add server name as prefix (`server1_tool_name`)
- **SUFFIX**: Add server name as suffix (`tool_name_server1`)
- **OVERRIDE**: Last server wins (overwrites previous)
- **IGNORE**: Skip conflicting items
- **ERROR**: Raise an error on conflicts

### Example Conflict Resolution

```python
# If two servers both have a "search" tool:
# PREFIX: jupyter_mcp_server_search, earthdata_mcp_server_search
# SUFFIX: search_jupyter_mcp_server, search_earthdata_mcp_server
# OVERRIDE: Only the last server's "search" tool is kept
```

## Real-World Examples

### Data Science Workflow

Create a unified MCP server combining Jupyter notebook capabilities with Earth science data access:

```toml
# pyproject.toml
[project]
dependencies = [
    "jupyter-mcp-server>=1.0.0",
    "earthdata-mcp-server>=0.1.0",
    "weather-mcp-server>=2.0.0"
]
```

```bash
# Discover available tools
python -m mcp_server_composer discover

# Create unified server for data science workflow
python -m mcp_server_composer compose \
  --name "data-science-server" \
  --conflict-resolution prefix \
  --output unified_server.py
```

This creates a server with tools like:
- `jupyter_create_notebook` - Create analysis notebooks
- `earthdata_search_datasets` - Find Earth science data
- `weather_get_forecast` - Access weather data
- Combined prompts for data analysis workflows

### Development Environment

Combine development tools and documentation servers:

```python
from mcp_server_composer import MCPServerComposer, ConflictResolution

composer = MCPServerComposer(
    composed_server_name="dev-environment",
    conflict_resolution=ConflictResolution.PREFIX
)

# Compose development-focused servers
dev_server = composer.compose_from_pyproject(
    include_servers=[
        "code-review-mcp-server",
        "documentation-mcp-server", 
        "testing-mcp-server"
    ]
)

# Access all development tools in one place
print("Available tools:", composer.list_tools())
```

### Custom Integration

```python
from mcp_server_composer import MCPServerComposer
from my_custom_server import MyMCPServer

# Create composer
composer = MCPServerComposer()

# Compose discovered servers
unified_server = composer.compose_from_pyproject()

# Add your custom server manually if needed
composer.add_server("custom", MyMCPServer())

# Get final composition summary
summary = composer.get_composition_summary()
print(f"Final server has {summary['total_tools']} tools from {summary['source_servers']} sources")
```

## Project Structure

When using MCP Server Composer, structure your project like this:

```
my-project/
├── pyproject.toml          # Define MCP server dependencies
├── src/
│   └── my_project/
│       ├── __init__.py
│       └── main.py         # Use composed server
├── composed_server.py      # Generated unified server (optional)
└── README.md
```

### Sample pyproject.toml

```toml
[project]
name = "my-data-project"
dependencies = [
    "jupyter-mcp-server>=1.0.0",
    "earthdata-mcp-server>=0.1.0",
    "fastmcp>=1.2.0"
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "mcp-server-composer>=1.0.0"
]
```

## Error Handling

The library provides comprehensive error handling:

```python
from mcp_server_composer import MCPServerComposer, MCPComposerError, MCPDiscoveryError

try:
    composer = MCPServerComposer()
    server = composer.compose_from_pyproject()
except MCPDiscoveryError as e:
    print(f"Discovery failed: {e}")
    print(f"Search paths: {e.search_paths}")
except MCPComposerError as e:
    print(f"Composition failed: {e}")
    print(f"Server count: {e.server_count}")
```

## Troubleshooting

### Common Issues

1. **No MCP servers found**: Ensure your dependencies include packages with "mcp" in the name
2. **Import errors**: Check that MCP server packages are properly installed
3. **Naming conflicts**: Use appropriate conflict resolution strategy
4. **Missing tools**: Verify that server packages export an `app` variable

### Debug Mode

```bash
# Enable verbose logging
python -m mcp_server_composer discover --verbose

# Check specific package
python -c "
from mcp_server_composer import MCPServerDiscovery
discovery = MCPServerDiscovery()
result = discovery._analyze_mcp_server('your-package-name')
print(result)
"
```

```

## API Reference

### MCPServerComposer

Main class for composing MCP servers:

```python
MCPServerComposer(
    composed_server_name: str = "composed-mcp-server",
    conflict_resolution: ConflictResolution = ConflictResolution.PREFIX
)
```

**Methods:**
- `compose_from_pyproject(pyproject_path, include_servers, exclude_servers)` - Compose servers from dependencies
- `get_composition_summary()` - Get summary of composition results
- `list_tools()` - List all available tools
- `list_prompts()` - List all available prompts
- `get_source_info()` - Get mapping of tools/prompts to source servers

### MCPServerDiscovery

Class for discovering MCP servers:

```python
MCPServerDiscovery(mcp_server_patterns: List[str] = None)
```

**Methods:**
- `discover_from_pyproject(pyproject_path)` - Discover servers from pyproject.toml
- `get_package_version(dependency_spec)` - Extract version from dependency string

### ConflictResolution

Enum for conflict resolution strategies:
- `PREFIX` - Add server name as prefix
- `SUFFIX` - Add server name as suffix  
- `OVERRIDE` - Last server wins
- `IGNORE` - Skip conflicting items
- `ERROR` - Raise error on conflicts

## Requirements

- Python 3.8+
- FastMCP >= 1.2.0
- TOML parsing support

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Ensure all tests pass (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.

## Support

- 📖 **Documentation**: Full API documentation and examples in this README
- 🐛 **Issues**: Report bugs and request features on [GitHub Issues](https://github.com/datalayer/mcp-server-composer/issues)
- 💬 **Discussions**: Join the conversation in [GitHub Discussions](https://github.com/datalayer/mcp-server-composer/discussions)

## Related Projects

- [FastMCP](https://github.com/modelcontextprotocol/python-sdk) - Python SDK for Model Context Protocol
- [MCP Specification](https://spec.modelcontextprotocol.io/) - Official MCP specification
- [Jupyter MCP Server](https://github.com/datalayer/jupyter-mcp-server) - MCP server for Jupyter functionality
- [Earthdata MCP Server](https://github.com/datalayer/earthdata-mcp-server) - MCP server for NASA Earthdata access

---

**Made with ❤️ by the Datalayer team**
- [Earthdata MCP Server](https://github.com/your-org/earthdata-mcp-server) - MCP server for NASA Earthdata

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes.

## Support

- GitHub Issues: [Report bugs or request features](https://github.com/your-org/mcp-server-composer/issues)
- Documentation: [Full documentation](https://your-org.github.io/mcp-server-composer/)
- Community: [Join the discussion](https://github.com/your-org/mcp-server-composer/discussions)
