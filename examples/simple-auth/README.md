# Simple MCP Server with GitHub OAuth Authentication

This is a didactic example demonstrating how to implement OAuth2 authentication with GitHub for an MCP (Model Context Protocol) server. The server requires users to authenticate via GitHub before they can access any tools.

## 📚 What You'll Learn

1. How OAuth2 authentication works with MCP servers
2. How to implement the MCP Authorization specification (2025-06-18)
3. How to protect MCP tools with access token verification
4. How to create a simple client that handles the OAuth flow

## 🏗️ Architecture Overview

```
┌─────────────┐         ┌──────────────────┐         ┌─────────────┐
│   Client    │────────>│   MCP Server     │<────────│   GitHub    │
│             │         │  (Protected)     │         │   OAuth     │
└─────────────┘         └──────────────────┘         └─────────────┘
      │                         │                           │
      │ 1. Request without      │                           │
      │    token                │                           │
      │─────────────────────────>                           │
      │                         │                           │
      │ 2. 401 + WWW-Authenticate                           │
      │    with metadata URL    │                           │
      │<─────────────────────────                           │
      │                         │                           │
      │ 3. Fetch metadata       │                           │
      │─────────────────────────>                           │
      │                         │                           │
      │ 4. OAuth metadata       │                           │
      │<─────────────────────────                           │
      │                         │                           │
      │ 5. Start OAuth flow     │                           │
      │─────────────────────────────────────────────────────>
      │                         │                           │
      │ 6. User authorizes in browser                       │
      │<─────────────────────────────────────────────────────
      │                         │                           │
      │ 7. Exchange code for    │                           │
      │    access token         │                           │
      │─────────────────────────────────────────────────────>
      │                         │                           │
      │ 8. Access token         │                           │
      │<─────────────────────────────────────────────────────
      │                         │                           │
      │ 9. Request with         │                           │
      │    Bearer token         │                           │
      │─────────────────────────>                           │
      │                         │                           │
      │ 10. Validate token &    │                           │
      │     return response     │                           │
      │<─────────────────────────                           │
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

### 3. **Configuration** (`config.json`)
   - GitHub OAuth app credentials
   - Server settings

## 🚀 Setup Instructions

### Step 1: Create GitHub OAuth App

1. Go to https://github.com/settings/developers
2. Click "New OAuth App"
3. Fill in the details:
   - **Application name**: `MCP Auth Example`
   - **Homepage URL**: `http://localhost:8080`
   - **Authorization callback URL**: `http://localhost:8080/callback`
4. Click "Register application"
5. Note your **Client ID**
6. Generate a new **Client Secret**

### Step 2: Configure the Application

Create or update `config.json`:

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

### Step 3: Install Dependencies

```bash
# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### Step 4: Run the Server

```bash
python -m simple_auth server
# or
python -m simple_auth.server
```

You should see:
```
🔐 MCP Server with GitHub OAuth2 Authentication
======================================================================

📋 Server Information:
   Server URL: http://localhost:8080
   MCP Transport: HTTP with SSE
   Authentication: GitHub OAuth2

🔗 OAuth Metadata Endpoints:
   Protected Resource: http://localhost:8080/.well-known/oauth-protected-resource
   Authorization Server: http://localhost:8080/.well-known/oauth-authorization-server

🔗 MCP Endpoints:
   SSE Endpoint: http://localhost:8080/sse
   Messages Endpoint: http://localhost:8080/messages

🛠️  Available Tools:
   - calculator_add - Add two numbers
   - calculator_multiply - Multiply two numbers
   - greeter_hello - Greet someone
   - greeter_goodbye - Say goodbye
   - get_server_info - Get server information

✅ Server is ready! All MCP tools require authentication.
```

### Step 5: Run the Client

In a new terminal:

```bash
python -m simple_auth client
# or
python -m simple_auth.client
```

The client will:
1. ✅ Attempt to connect to the MCP server
2. ✅ Receive a 401 Unauthorized response
3. ✅ Fetch OAuth metadata
4. ✅ Open your browser for GitHub authentication
5. ✅ Exchange authorization code for access token
6. ✅ Connect to MCP server via SSE transport with authentication
7. ✅ List available MCP tools
8. ✅ Invoke MCP tools using the official MCP protocol

## 📖 Understanding the Flow

### 1. Initial Request (No Token)

```python
# Client makes request without token
response = requests.get("http://localhost:8080/tools")
# Status: 401 Unauthorized
```

### 2. Server Returns WWW-Authenticate Header

```http
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer realm="http://localhost:8080/.well-known/oauth-protected-resource"
```

This tells the client where to find the protected resource metadata.

### 3. Client Discovers Authorization Server

```python
# Fetch protected resource metadata
metadata = requests.get("http://localhost:8080/.well-known/oauth-protected-resource").json()
# Returns: {"authorization_servers": ["http://localhost:8080"]}

# Fetch authorization server metadata
auth_metadata = requests.get("http://localhost:8080/.well-known/oauth-authorization-server").json()
# Returns OAuth endpoints and capabilities
```

### 4. OAuth Flow with GitHub

```python
# Generate PKCE parameters for security
code_verifier = generate_code_verifier()
code_challenge = generate_code_challenge(code_verifier)

# Build authorization URL
auth_url = f"{github_authorize_url}?client_id={client_id}&redirect_uri={redirect_uri}&scope=user&state={state}&code_challenge={code_challenge}&code_challenge_method=S256&resource={resource_uri}"

# User authorizes in browser
# GitHub redirects back with authorization code

# Exchange code for token
token_response = requests.post(github_token_url, data={
    "client_id": client_id,
    "client_secret": client_secret,
    "code": authorization_code,
    "redirect_uri": redirect_uri,
    "code_verifier": code_verifier
})

access_token = token_response.json()["access_token"]
```

### 5. Authenticated Requests

```python
# Make request with Bearer token
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.post("http://localhost:8080/tools/calculator:add", 
                        json={"a": 5, "b": 3},
                        headers=headers)
# Status: 200 OK
# Result: {"result": 8}
```

### 6. Token Validation on Server

```python
# Server validates token before processing
def validate_token(token: str) -> bool:
    # Verify token with GitHub
    response = requests.get("https://api.github.com/user", 
                           headers={"Authorization": f"Bearer {token}"})
    return response.status_code == 200
```

## 🔐 Security Features

### 1. **PKCE (Proof Key for Code Exchange)**
   - Protects against authorization code interception
   - Required by MCP specification for public clients
   - Uses SHA256 challenge/verifier pair

### 2. **Resource Parameter**
   - Explicitly binds tokens to the MCP server
   - Prevents token reuse across services
   - Follows RFC 8707

### 3. **Token Validation**
   - Server verifies every token with GitHub
   - Rejects invalid or expired tokens
   - Returns 401 for authentication failures

### 4. **State Parameter**
   - Prevents CSRF attacks
   - Verifies OAuth callback authenticity

## 🧪 Testing the Tools

Once authenticated, the client can use the available tools:

### Calculator Tool
```bash
# The client will automatically call:
POST /tools/calculator:add
{
  "a": 5,
  "b": 3
}

# Response: {"result": 8}
```

### Greeter Tool
```bash
POST /tools/greeter:hello
{
  "name": "Alice"
}

# Response: {"message": "Hello, Alice!"}
```

## 📝 Key MCP Concepts Demonstrated

1. **Protected Resource Metadata** (RFC 9728)
   - `/.well-known/oauth-protected-resource` endpoint
   - Advertises authorization servers

2. **Authorization Server Metadata** (RFC 8414)
   - `/.well-known/oauth-authorization-server` endpoint
   - Provides OAuth configuration

3. **Bearer Token Authentication**
   - All requests include `Authorization: Bearer <token>` header
   - Tokens validated on every request

4. **Tool Protection**
   - Tools only accessible with valid tokens
   - User context available for authorization decisions

5. **Resource Indicators** (RFC 8707)
   - `resource` parameter in OAuth requests
   - Binds tokens to specific MCP server

## 🎓 Learning Exercises

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

### Issue: "redirect_uri_mismatch" error
**Solution**: Ensure the callback URL in your GitHub OAuth app settings exactly matches `http://localhost:8080/callback`

### Issue: Token validation fails
**Solution**: Check that the GitHub access token has not expired. GitHub tokens typically last 8 hours.

### Issue: Browser doesn't open
**Solution**: Manually navigate to the URL printed in the console

### Issue: Port already in use
**Solution**: Change the port in `config.json` or kill the process using port 8080:
```bash
# Find process
lsof -i :8080

# Kill process
kill -9 <PID>
```

## 📚 Additional Resources

- [MCP Authorization Specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)
- [OAuth 2.1 Draft](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1-13)
- [RFC 8707 - Resource Indicators](https://www.rfc-editor.org/rfc/rfc8707.html)
- [RFC 9728 - Protected Resource Metadata](https://datatracker.ietf.org/doc/html/rfc9728)
- [RFC 8414 - Authorization Server Metadata](https://datatracker.ietf.org/doc/html/rfc8414)
- [GitHub OAuth Documentation](https://docs.github.com/en/developers/apps/building-oauth-apps)

## 🎯 Summary

This example demonstrates:
- ✅ Complete OAuth2 flow with GitHub
- ✅ MCP Authorization specification compliance
- ✅ Protected resource metadata
- ✅ Token validation and verification
- ✅ PKCE for security
- ✅ Simple, clear code structure
- ✅ Didactic explanations at every step

You now have a foundation for building secure, authenticated MCP servers! 🚀
