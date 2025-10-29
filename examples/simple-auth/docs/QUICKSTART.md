# Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- A GitHub account
- Basic understanding of OAuth2 (optional, you'll learn as you go!)

## Step 1: Create GitHub OAuth App (2 minutes)

1. Visit https://github.com/settings/developers
2. Click **"New OAuth App"**
3. Fill in:
   - **Application name**: `MCP Auth Demo`
   - **Homepage URL**: `http://localhost:8080`
   - **Authorization callback URL**: `http://localhost:8080/callback`
4. Click **"Register application"**
5. Copy your **Client ID**
6. Click **"Generate a new client secret"** and copy the **Client Secret**

⚠️ **Security Note**: Never commit your client secret to version control!

## Step 2: Configure (1 minute)

Edit `config.json` and replace the placeholders:

```json
{
  "github": {
    "client_id": "Iv1.abc123def456",
    "client_secret": "your_secret_here_1234567890abcdef"
  },
  "server": {
    "host": "localhost",
    "port": 8080
  }
}
```

## Step 3: Install Dependencies (1 minute)

```bash
pip install -r requirements.txt
```

This installs:
- `requests` - HTTP client
- `mcp` - Official MCP Python SDK
- `fastapi` - Web framework for server
- `uvicorn` - ASGI server
- `sse-starlette` - Server-Sent Events support

## Step 4: Run the Server (30 seconds)

```bash
python -m simple_auth server
```

You should see:
```
🔐 MCP Server with GitHub OAuth2 Authentication
======================================================================

📋 Server Information:
   Server URL: http://localhost:8080
   MCP Transport: HTTP with SSE
   ...

✅ Server is ready! All MCP tools require authentication.
```

## Step 5: Run the Client (1 minute)

Open a **new terminal** and run:

```bash
python -m simple_auth client
```

The demo will:

1. ✅ Discover OAuth endpoints from the server
2. ✅ Open your browser for GitHub authentication
3. ✅ Exchange the authorization code for an access token
4. ✅ Connect to MCP server via SSE with authentication
5. ✅ List available tools using MCP protocol
6. ✅ Invoke example tools (calculator, greeter) via MCP protocol

## What Happens?

### First Request (Unauthenticated)
```
Client → Server: GET /tools
Server → Client: 401 Unauthorized + WWW-Authenticate header
```

### Metadata Discovery
```
Client → Server: GET /.well-known/oauth-protected-resource
Server → Client: {"authorization_servers": ["http://localhost:8080"]}

Client → Server: GET /.well-known/oauth-authorization-server
Server → Client: {OAuth endpoints and capabilities}
```

### OAuth Flow
```
1. Client generates PKCE parameters (code_verifier, code_challenge)
2. Client opens browser → GitHub authorization page
3. User authorizes the application
4. GitHub redirects → http://localhost:8080/callback?code=...
5. Client exchanges code + verifier → access_token
```

### Authenticated Requests
```
Client → Server: GET /tools
             Headers: Authorization: Bearer <token>
Server → GitHub: Validate token
Server → Client: 200 OK + list of tools
```

## Testing

Run the test script to verify everything works:

```bash
python test_auth.py
```

## Troubleshooting

### Error: "redirect_uri_mismatch"
- Check that your callback URL in GitHub settings exactly matches `http://localhost:8080/callback`

### Error: "Connection refused"
- Make sure the server is running: `python -m simple_auth server`

### Error: Token validation fails
**Solution**: Get fresh token (they expire). Run `python -m simple_auth client` again to get a fresh token

### Browser doesn't open
- Manually copy the URL from the terminal and paste it in your browser

## Next Steps

🎓 Read the full [README.md](README.md) to understand:
- The complete OAuth2 flow
- Security features (PKCE, token validation)
- MCP Authorization specification details
- How to customize and extend

🔧 Try the exercises:
- Add tool authorization
- Implement token caching
- Support refresh tokens

🚀 Build your own MCP server with authentication!

## Support

- Questions? Check the [README.md](README.md) troubleshooting section
- Issues? Open an issue on GitHub
- Want to learn more? Read the [MCP Authorization Specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)

---

**Time to complete**: ~5 minutes
**Difficulty**: Beginner-friendly
**What you'll learn**: OAuth2, MCP authentication, token validation
