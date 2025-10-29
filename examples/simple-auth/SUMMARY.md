# Summary

## What is This?

A **simple, didactic example** demonstrating OAuth2 authentication for Model Context Protocol (MCP) servers using GitHub as the OAuth provider.

## What You Get

### 📁 Files Created

1. **README.md** - Complete documentation with examples, troubleshooting, and learning exercises
2. **docs/QUICKSTART.md** - Get running in 5 minutes
3. **docs/FLOW_EXPLAINED.md** - Detailed step-by-step explanation of the OAuth flow
4. **docs/DIAGRAMS.md** - Visual ASCII diagrams of the authentication process
5. **docs/IMPLEMENTATION.md** - Implementation details
6. **simple_auth/server.py** - MCP server built with official FastMCP SDK + OAuth2 protection
7. **simple_auth/client.py** - MCP client using official MCP SDK with OAuth2 flow
8. **simple_auth/__init__.py** - Package initialization
9. **simple_auth/__main__.py** - CLI entry point for running server/client
10. **config.json** - Configuration file (template provided)
11. **requirements.txt** - Python dependencies (mcp, fastapi, uvicorn, requests)
12. **test_auth.py** - Basic tests to verify setup
13. **.gitignore** - Protects secrets from being committed

### 🎯 What You Learn

1. **OAuth2 Fundamentals**
   - Authorization Code flow
   - PKCE (Proof Key for Code Exchange)
   - Token management
   - State parameter for CSRF protection

2. **MCP Authorization Specification (2025-06-18)**
   - Protected Resource Metadata (RFC 9728)
   - Authorization Server Metadata (RFC 8414)
   - Resource Indicators (RFC 8707)
   - Token validation requirements

3. **Security Best Practices**
   - Why PKCE is essential
   - Token audience binding
   - Bearer token in headers (not URLs)
   - Token validation on every request
   - State parameter for CSRF protection

4. **Implementation Details**
   - Metadata discovery process
   - Browser-based authorization flow
   - Token exchange with PKCE
   - Authenticated API requests
   - Error handling

## How It Works

### The Flow in 4 Steps

1. **Discovery** 
   - Client tries to access server without token
   - Server returns 401 with metadata URL
   - Client fetches OAuth configuration

2. **Authentication**
   - Client generates PKCE parameters
   - Opens browser for user to authorize with GitHub
   - Exchanges authorization code for access token

3. **Access**
   - Client includes token in Authorization header
   - Server validates token with GitHub
   - Server processes request and returns result

4. **Tools**
   - Calculator: add and multiply numbers
   - Greeter: hello and goodbye messages

## Quick Reference

### Start Server
```bash
python -m simple_auth server
```

### Run Client Demo
```bash
python -m simple_auth client
```

### Run Tests
```bash
python test_auth.py
```

### Configuration
Edit `config.json` with your GitHub OAuth credentials:
- Get from: https://github.com/settings/developers
- Callback URL: `http://localhost:8080/callback`

## Key Endpoints

### Server Endpoints

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/.well-known/oauth-protected-resource` | GET | No | Protected resource metadata |
| `/.well-known/oauth-authorization-server` | GET | No | Authorization server metadata |
| `/sse` | GET | Yes | MCP SSE endpoint (Server-Sent Events) |
| `/messages` | POST | Yes | MCP messages endpoint |
| `/tools` | GET | Yes | List available tools (convenience) |
| `/callback` | GET | No | OAuth callback handler |
| `/health` | GET | No | Health check |
| `/` | GET | No | Server information |

### OAuth Endpoints (GitHub)

| Endpoint | Description |
|----------|-------------|
| `https://github.com/login/oauth/authorize` | User authorization |
| `https://github.com/login/oauth/access_token` | Token exchange |
| `https://api.github.com/user` | Token validation |

## Security Features Demonstrated

✅ **PKCE** - Prevents authorization code interception  
✅ **State Parameter** - CSRF protection  
✅ **Resource Parameter** - Token audience binding  
✅ **Token Validation** - Verify every request with GitHub  
✅ **Bearer Token in Header** - Never in URL  
✅ **No Session Storage** - Stateless validation  

## Code Structure

### Server (`simple_auth/server.py`)

```python
# Main components:
- Config: Load configuration
- TokenValidator: Validate tokens with GitHub
- FastMCP: Official MCP SDK server
- MCP Tools: Decorated with @mcp.tool()
  - calculator_add, calculator_multiply
  - greeter_hello, greeter_goodbye
  - get_server_info
- FastAPI: HTTP/SSE transport layer
- Authentication Middleware: verify_token()
- OAuth Endpoints: Metadata and callback
- main(): Entry point
```

### Client (`simple_auth/client.py`)

```python
# Main components:
- Config: Load configuration
- PKCEHelper: Generate PKCE parameters
- OAuthCallbackHandler: Handle OAuth callback
- MCPClient: Main client logic
  - discover_metadata(): OAuth discovery
  - authenticate(): OAuth flow
  - list_tools(): Get available tools (HTTP)
  - invoke_tool_mcp(): Call tool via MCP SDK (SSE)
  - demo(): Complete demonstration
- main(): Entry point
```

### Package (`simple_auth/__main__.py`)

```python
# CLI entry point:
- python -m simple_auth server  # Run server
- python -m simple_auth client  # Run client
```

## Standards Compliance

This implementation follows:

- ✅ **MCP Authorization Specification** (2025-06-18)
- ✅ **OAuth 2.1** (draft-ietf-oauth-v2-1-13)
- ✅ **RFC 7636** - PKCE
- ✅ **RFC 8414** - Authorization Server Metadata
- ✅ **RFC 8707** - Resource Indicators
- ✅ **RFC 9728** - Protected Resource Metadata

## Learning Path

1. **Start Here**: Read QUICKSTART.md and get it running
2. **Understand Flow**: Read FLOW_EXPLAINED.md for detailed walkthrough
3. **Visualize**: Study DIAGRAMS.md for visual explanations
4. **Deep Dive**: Read README.md for comprehensive documentation
5. **Experiment**: Modify the code and try the exercises

## Common Use Cases

### 1. Secure MCP Server
Protect your MCP tools with OAuth2 authentication

### 2. Multi-Tenant MCP
Different users access different tools based on their identity

### 3. Audit Logging
Track which user invoked which tool and when

### 4. Rate Limiting
Limit requests per user rather than per IP

### 5. Permission Management
Fine-grained control over tool access

## Extending This Example

### Add Tool Authorization
```python
def check_permission(user: str, tool: str) -> bool:
    # Implement your authorization logic
    if tool.startswith("admin:"):
        return user in ADMIN_USERS
    return True
```

### Add Token Caching
```python
def cache_token(token: str, expires_at: int):
    # Cache tokens to avoid re-authentication
    with open("token_cache.json", "w") as f:
        json.dump({"token": token, "expires": expires_at}, f)
```

### Add More Tools
```python
@staticmethod
def database_query(sql: str) -> Dict[str, Any]:
    """Execute database query (admin only)"""
    # Your implementation
    return {"rows": [...]}
```

### Add Logging
```python
def log_tool_invocation(user: str, tool: str, params: Dict):
    """Log tool usage for audit"""
    print(f"{datetime.now()}: {user} invoked {tool} with {params}")
```

## Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| redirect_uri_mismatch | Check GitHub OAuth app settings |
| Connection refused | Start the server first |
| Token validation fails | Get fresh token (they expire) |
| Browser doesn't open | Copy URL from terminal |
| Port in use | Change port in config.json |

## Resources

- **MCP Spec**: https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization
- **OAuth 2.1**: https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1-13
- **GitHub OAuth**: https://docs.github.com/en/developers/apps/building-oauth-apps
- **RFCs**: See README.md for complete list

## Support & Contributions

- Found a bug? Open an issue
- Have a question? Check the troubleshooting guides
- Want to improve it? Submit a pull request
- Need help? Read the documentation files

## License

This example is part of the mcp-server-composer project.
See the main project LICENSE for details.

---

**🎓 You now have everything you need to:**
- Understand OAuth2 authentication
- Implement MCP Authorization specification
- Build secure MCP servers
- Create authenticated MCP clients
- Apply security best practices

**Happy coding! 🚀**
