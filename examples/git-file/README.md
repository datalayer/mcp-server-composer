# Git + File MCP Server Example

This example demonstrates how to run Git and Filesystem MCP servers individually or use them together.

## 🎯 Overview

This example shows two MCP servers:

1. **Git MCP Server** - Git operations (status, log, diff, commit, etc.)
2. **Filesystem MCP Server** - File system operations (read, write, list, etc.)

**Note:** The full MCP Server Composer with web UI and unified orchestration is under development. This example shows how to work with individual MCP servers using the official MCP SDK.

## 📋 Features

- **Multiple Servers**: Git and Filesystem servers running together
- **Anonymous Access**: No authentication required
- **Unified Interface**: Access both servers through a single API
- **Tool Prefixing**: Tools are prefixed with server name (e.g., `git:log`, `filesystem:read_file`)
- **Web UI**: Manage and monitor servers through browser interface
- **REST API**: Full programmatic control via HTTP endpoints

## 🚀 Quick Start

### 1. Install MCP Servers

```bash
make install
```

This will install:
- `mcp-server-git` (Git operations)
- `mcp-server-filesystem` (File operations)

### 2. Run Git MCP Server

In one terminal:

```bash
make start-git
```

### 3. Run Filesystem MCP Server

In another terminal:

```bash
make start-fs
```

### 4. Connect a Client

You can connect MCP clients (like Claude Desktop, Continue, or custom applications) to these servers using STDIO transport.

Example with Python MCP client:

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Connect to git server
server_params = StdioServerParameters(
    command="uvx",
    args=["mcp-server-git", "--repository", "."]
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        tools = await session.list_tools()
        print(f"Available tools: {[t.name for t in tools]}")
```

## 📖 Usage Examples

### List Available Tools

```bash
# All tools
make list-tools

# Git tools only
make list-git

# Filesystem tools only
make list-fs
```

### Test Git Server

```bash
# Get commit log
make test-git

# Get git status
make test-git-status
```

### Test Filesystem Server

```bash
# List directory
make test-fs

# Read a file
make test-fs-read
```

### Manual API Calls

#### Git Operations

**Get commit log:**
```bash
curl -X POST http://localhost:8000/api/v1/tools/git:log/invoke \
  -H "Content-Type: application/json" \
  -d '{"limit": 10}'
```

**Get repository status:**
```bash
curl -X POST http://localhost:8000/api/v1/tools/git:status/invoke \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Show diff:**
```bash
curl -X POST http://localhost:8000/api/v1/tools/git:diff/invoke \
  -H "Content-Type: application/json" \
  -d '{"cached": false}'
```

#### Filesystem Operations

**List directory:**
```bash
curl -X POST http://localhost:8000/api/v1/tools/filesystem:list_directory/invoke \
  -H "Content-Type: application/json" \
  -d '{"path": "/tmp"}'
```

**Read file:**
```bash
curl -X POST http://localhost:8000/api/v1/tools/filesystem:read_file/invoke \
  -H "Content-Type: application/json" \
  -d '{"path": "/tmp/myfile.txt"}'
```

**Write file:**
```bash
curl -X POST http://localhost:8000/api/v1/tools/filesystem:write_file/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/tmp/test.txt",
    "content": "Hello from MCP!"
  }'
```

## 🎨 Web UI Features

Access the Web UI at http://localhost:8000

### Dashboard
- View active servers count
- See total available tools
- Monitor system health
- Quick navigation

### Server Management
- Start/stop individual servers
- View server status and uptime
- Monitor process IDs
- See restart counts

### Tool Browser
- Search and filter tools
- View tool schemas
- Invoke tools interactively
- See results in real-time

### Configuration Editor
- Edit server configuration
- Validate before applying
- Reload from file
- Live updates

### Log Viewer
- Real-time log streaming
- Filter by level and server
- Search log messages
- Download logs

### Metrics Dashboard
- Request rates
- Tool invocations
- Response latency
- System resources

## 🔧 Configuration

The configuration file `mcp_server_composer.toml` defines:

```toml
[composer]
name = "git-file-composer"
conflict_resolution = "prefix"  # Tools are prefixed: git:log, filesystem:read_file

[[servers]]
name = "git"
command = "uvx"
args = ["mcp-server-git", "--repository", "."]
transport = "stdio"
auto_start = true

[[servers]]
name = "filesystem"
command = "uvx"
args = ["mcp-server-filesystem", "/tmp"]
transport = "stdio"
auto_start = true
```

### Customization Options

**Change Git Repository:**
```toml
args = ["mcp-server-git", "--repository", "/path/to/your/repo"]
```

**Change Filesystem Root:**
```toml
args = ["mcp-server-filesystem", "/your/allowed/path"]
```

**Add Environment Variables:**
```toml
[servers.env]
GIT_AUTHOR_NAME = "Bot"
GIT_AUTHOR_EMAIL = "bot@example.com"
```

## 🛠️ Makefile Commands

| Command | Description |
|---------|-------------|
| `make help` | Show all available commands |
| `make install` | Install dependencies |
| `make start` | Start composer (foreground) |
| `make start-bg` | Start composer (background) |
| `make stop` | Stop composer |
| `make restart` | Restart composer |
| `make status` | Check status |
| `make health` | Check health endpoint |
| `make logs` | View real-time logs |
| `make list-tools` | List all tools |
| `make list-git` | List Git tools |
| `make list-fs` | List Filesystem tools |
| `make test-git` | Test Git server |
| `make test-fs` | Test Filesystem server |
| `make test-all` | Run all tests |
| `make open-ui` | Open Web UI |
| `make examples` | Show API examples |
| `make clean` | Clean up files |

## 🔍 Available Tools

### Git Server Tools

The Git MCP server typically provides:

- `git:status` - Get repository status
- `git:log` - Get commit history
- `git:diff` - Show changes
- `git:commit` - Create commits
- `git:add` - Stage files
- `git:branch` - Manage branches
- `git:checkout` - Switch branches
- And more...

### Filesystem Server Tools

The Filesystem MCP server provides:

- `filesystem:read_file` - Read file contents
- `filesystem:write_file` - Write to file
- `filesystem:list_directory` - List directory contents
- `filesystem:create_directory` - Create directories
- `filesystem:delete_file` - Delete files
- `filesystem:move_file` - Move/rename files
- And more...

Run `make list-tools` to see the exact tools available with your versions.

## 📊 Monitoring

### Prometheus Metrics

Metrics are exposed at: http://localhost:8000/metrics

Example metrics:
- `mcp_http_requests_total` - Total HTTP requests
- `mcp_tool_invocations_total` - Tool invocation count
- `mcp_request_duration_seconds` - Request latency

### Health Checks

```bash
# Simple health check
curl http://localhost:8000/api/v1/health

# Detailed status
curl http://localhost:8000/api/v1/status
```

## 🐛 Troubleshooting

### Server Won't Start

1. Check if port 8000 is available:
   ```bash
   lsof -i :8000
   ```

2. View logs:
   ```bash
   make logs
   ```

3. Check server status:
   ```bash
   make status
   ```

### Tools Not Found

1. Verify servers are running:
   ```bash
   curl http://localhost:8000/api/v1/servers
   ```

2. Restart servers:
   ```bash
   make restart
   ```

### Permission Errors (Filesystem)

The filesystem server is limited to `/tmp` by default. To access other directories, update the configuration:

```toml
args = ["mcp-server-filesystem", "/your/allowed/path"]
```

## 🔒 Security Notes

⚠️ **This example runs with NO AUTHENTICATION**

For production use:

1. **Enable authentication** in the config:
   ```toml
   [authentication]
   enabled = true
   providers = ["api_key"]
   
   [authentication.api_key]
   keys = ["your-secret-key"]
   ```

2. **Restrict filesystem access** to specific directories

3. **Use HTTPS** in production

4. **Enable CORS** only for trusted origins

5. **Add rate limiting** for public-facing deployments

See the [Security documentation](../../docs/DEPLOYMENT.md#security-hardening) for more details.

## 📚 Learn More

- **[User Guide](../../docs/USER_GUIDE.md)** - Complete feature documentation
- **[API Reference](../../docs/API_REFERENCE.md)** - REST API documentation  
- **[Deployment Guide](../../docs/DEPLOYMENT.md)** - Production deployment
- **[Architecture](../../ARCHITECTURE.md)** - System design

## 🤝 Contributing

Found an issue or want to improve this example? Please open an issue or PR!

## 📄 License

BSD 3-Clause License - see [LICENSE](../../LICENSE)

---

**Made with ❤️ by [Datalayer](https://datalayer.io)**
