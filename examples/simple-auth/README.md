# Simple MCP Server with GitHub OAuth Authentication

A clear, educational example demonstrating OAuth2 authentication for MCP (Model Context Protocol) servers using GitHub as the identity provider.

## 📚 What You'll Learn

- **OAuth2** - Authorization Code flow with PKCE
- **MCP Authorization** - Official specification (2025-06-18)
- **Security** - Token validation, CSRF protection, resource indicators
- **MCP SDK** - Building servers with FastMCP and clients with MCP SDK
- **AI Agents** - Building interactive AI agents with pydantic-ai and MCP tools

## 📖 Documentation

| File | Purpose | Start Here If... |
|------|---------|------------------|
| **[docs/QUICKSTART.md](docs/QUICKSTART.md)** | Get running in 5 minutes | You want to try it immediately |
| **[docs/GITHUB.md](docs/GITHUB.md)** | GitHub OAuth app setup | Setting up for the first time |
| **[docs/FLOW_EXPLAINED.md](docs/FLOW_EXPLAINED.md)** | Detailed OAuth flow | You want to understand how it works |
| **[docs/DIAGRAMS.md](docs/DIAGRAMS.md)** | Visual explanations | You prefer diagrams |
| **[docs/IMPLEMENTATION.md](docs/IMPLEMENTATION.md)** | Technical details | You're implementing your own |

## 📁 Project Structure

```
simple-auth/
├── simple_auth/           # Python package
│   ├── server.py         # MCP server with OAuth2 (FastMCP + FastAPI)
│   ├── client.py         # MCP client with OAuth2 flow
│   ├── agent.py          # Pydantic AI agent with MCP tools
│   ├── oauth_client.py   # Shared OAuth authentication logic
│   ├── __main__.py       # CLI entry point
│   └── __init__.py
├── docs/                  # Documentation
│   ├── GITHUB.md         # GitHub OAuth app setup
│   ├── QUICKSTART.md     # 5-minute getting started
│   ├── FLOW_EXPLAINED.md # Detailed OAuth flow walkthrough
│   ├── DIAGRAMS.md       # Visual diagrams
│   └── IMPLEMENTATION.md # Technical implementation details
├── tests/                 # Tests
│   └── test_auth.py      # Basic tests
├── README.md             # This file - complete reference
├── Makefile              # Convenient make targets
├── config.json           # OAuth credentials (template)
└── requirements.txt      # Dependencies
```

## 🔧 Components

### 1. **MCP Server** (`simple_auth/server.py`)
   - Built with **official MCP Python SDK** (FastMCP)
   - Protected MCP server with OAuth2 integration
   - Implements MCP Authorization specification (2025-06-18)
   - Exposes OAuth metadata endpoints (RFC 9728, RFC 8414)
   - Validates access tokens before serving tools
   - Provides MCP tools via HTTP/SSE transport
   - Tools: calculator (add, multiply), greeter (hello, goodbye), server info

### 2. **MCP Client** (`simple_auth/client.py`)
   - Handles OAuth2 flow with GitHub
   - Automatically opens browser for user authentication
   - Manages access tokens
   - Connects to MCP server using **MCP SDK client**
   - Makes authenticated requests via MCP protocol (SSE transport)
   - Demonstrates proper MCP tool invocation

### 3. **Pydantic AI Agent** (`simple_auth/agent.py`) ✨ NEW
   - Interactive CLI agent powered by **pydantic-ai**
   - Uses **Anthropic Claude Sonnet 4.5** model
   - Automatically authenticates with OAuth2
   - Connects to MCP server with authenticated tools
   - Natural language interface to MCP tools
   - Example: "What is 15 + 27?" → Uses calculator_add tool

### 4. **OAuth Client** (`simple_auth/oauth_client.py`)
   - Shared authentication logic (used by both client.py and agent.py)
   - Implements OAuth2 with PKCE (RFC 7636)
   - Metadata discovery (RFC 8414, RFC 9728)
   - Token management and validation
   - Reusable for any MCP client implementation

### 5. **Configuration** (`config.json`)
   - GitHub OAuth app credentials
   - Server settings

## 🚀 Quick Start

1. **Create GitHub OAuth app** → [docs/GITHUB.md](docs/GITHUB.md)
2. **Configure** → Edit `config.json` with your Client ID and Secret
3. **Install** → `make install` (or `pip install -r requirements.txt`)
4. **Run server** → `make server` (or `python -m simple_auth server`)
5. **Run client** → `make client` (or `python -m simple_auth client`) in a new terminal
6. **Run agent** → `make agent` (or `python -m simple_auth agent`) for interactive AI 🤖

👉 **Detailed walkthrough**: [docs/QUICKSTART.md](docs/QUICKSTART.md)

## 🎬 How It Works

1. **Client connects** → Server responds with 401 and OAuth metadata
2. **Discovery** → Client fetches authorization server configuration
3. **Authentication** → Browser opens for GitHub authorization (with PKCE)
4. **Token exchange** → Client receives access token
5. **MCP access** → Client invokes tools via SSE with Bearer token
6. **Validation** → Server validates every request with GitHub

👉 **Detailed flow**: [docs/FLOW_EXPLAINED.md](docs/FLOW_EXPLAINED.md)

## 🛠️ Available Tools

The server exposes these example MCP tools:
- `calculator_add(a, b)` - Add two numbers
- `calculator_multiply(a, b)` - Multiply two numbers
- `greeter_hello(name)` - Say hello
- `greeter_goodbye(name)` - Say goodbye
- `get_server_info()` - Get server information

## 🔧 Configuration

Create `config.json` in the example directory:

```json
{
  "github": {
    "client_id": "YOUR_GITHUB_CLIENT_ID",
    "client_secret": "YOUR_GITHUB_CLIENT_SECRET"
  },
  "server": {
    "host": "localhost",
    "port": 8080
  }
}
```

See [docs/GITHUB.md](docs/GITHUB.md) for how to get these credentials.

**Note on ports**:
- **Port 8080**: MCP server (configured in `config.json`)
- **Port 8081**: OAuth callback listener (used by client during authentication)
- The client runs a temporary HTTP server on port 8081 to receive the OAuth callback from GitHub

## 💻 Running the Example

### Start the Server

```bash
pip install -r requirements.txt
python -m simple_auth server
# Or use make:
make server
```

Server starts on `http://localhost:8080` with OAuth metadata and MCP endpoints.

### Run the Client

In a new terminal:

```bash
python -m simple_auth client
# Or use make:
make client
```

The client will:
1. Connect to MCP server (receives 401)
2. Fetch OAuth metadata
3. Open browser for GitHub authentication
4. Exchange authorization code for access token
5. Connect via SSE with Bearer token
6. List and invoke MCP tools

## 📖 Understanding the Code

For detailed code explanations and flow diagrams, see:
- **[docs/FLOW_EXPLAINED.md](docs/FLOW_EXPLAINED.md)** - Step-by-step OAuth flow
- **[docs/DIAGRAMS.md](docs/DIAGRAMS.md)** - Visual diagrams  
- **[docs/IMPLEMENTATION.md](docs/IMPLEMENTATION.md)** - Technical implementation details

### Key Components

**Server** (`simple_auth/server.py`):
- Uses FastMCP SDK with `@mcp.tool()` decorators
- FastAPI for HTTP/SSE transport
- JWT token validation middleware
- OAuth metadata endpoints (RFC 9728, RFC 8414)

**Client** (`simple_auth/client.py`):
- OAuth2 flow with PKCE (RFC 7636)
- Browser-based GitHub authentication
- MCP SDK client with SSE transport
- Proper MCP tool invocation

## 🔐 Security Features

✅ **PKCE** - Prevents authorization code interception (RFC 7636)  
✅ **State Parameter** - CSRF protection  
✅ **Resource Indicators** - Token audience binding (RFC 8707)  
✅ **Token Validation** - Every request verified with GitHub  
✅ **Bearer Token in Header** - Never in URL

## 📝 Standards Compliance

- ✅ MCP Authorization Specification (2025-06-18)
- ✅ OAuth 2.1 with PKCE
- ✅ RFC 9728 - Protected Resource Metadata
- ✅ RFC 8414 - Authorization Server Metadata
- ✅ RFC 8707 - Resource Indicators
- ✅ RFC 7636 - PKCE

## 🎓 Use Cases

This authentication pattern enables:
- **Secure MCP servers** - Protect tools with user authentication
- **Multi-tenant deployments** - Different users, different access
- **Audit logging** - Track which user invoked which tool
- **Rate limiting** - Limit requests per user, not just per IP
- **Fine-grained authorization** - Control tool access by user identity

## 💡 Learning Exercises

### Exercise 1: Add Tool Authorization
Modify the server to restrict certain tools to specific users:
```python
def check_tool_permission(user: str, tool: str) -> bool:
    # Only admin users can use sensitive tools
    if tool.startswith("admin:"):
        return user in ADMIN_USERS
    return True
```

### Exercise 2: Token Caching
Implement token caching in the client to avoid re-authentication:
```python
def get_cached_token():
    if os.path.exists("token_cache.json"):
        with open("token_cache.json") as f:
            data = json.load(f)
            if data["expires_at"] > time.time():
                return data["access_token"]
    return None
```

### Exercise 3: Refresh Tokens
Add support for refresh tokens to extend sessions:
```python
def refresh_access_token(refresh_token: str) -> str:
    response = requests.post(token_url, data={
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id
    })
    return response.json()["access_token"]
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `redirect_uri_mismatch` | Verify callback URL in [GitHub OAuth app](docs/GITHUB.md) is exactly `http://localhost:8081/callback` (client uses port 8081) |
| Token validation fails | GitHub tokens expire - restart authentication flow |
| Browser doesn't open | Copy URL from terminal and open manually |
| Port already in use | Change port in `config.json` or use `lsof -i :8080` to find/kill process |

More troubleshooting: [docs/GITHUB.md](docs/GITHUB.md)

## 📚 Resources

- [MCP Authorization Specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)
- [OAuth 2.1 Draft](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1-13)
- [GitHub OAuth Documentation](https://docs.github.com/en/developers/apps/building-oauth-apps)
- RFC 7636 (PKCE), RFC 8414 (Auth Server Metadata), RFC 8707 (Resource Indicators), RFC 9728 (Protected Resource Metadata)

---

**🎓 You now have a working example of OAuth2-protected MCP server!**  
Start with [docs/QUICKSTART.md](docs/QUICKSTART.md) to get running in 5 minutes. 🚀
