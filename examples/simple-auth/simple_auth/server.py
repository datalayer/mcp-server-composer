#!/usr/bin/env python3
"""
MCP Server with GitHub OAuth2 Authentication

This server combines:
1. OAuth2 authorization server (GitHub-based)
2. MCP server with FastMCP SDK exposing protected tools

Implements MCP Authorization specification (2025-06-18):
- Protected Resource Metadata (RFC 9728)
- Authorization Server Metadata (RFC 8414)
- Resource Indicators (RFC 8707)
- Bearer token authentication

The server exposes MCP tools via HTTP transport while requiring
OAuth2 authentication for all tool invocations.
"""

import json
import asyncio
from typing import Dict, Optional, Any
from contextlib import asynccontextmanager
import requests

from fastapi import FastAPI, Request, Response, HTTPException, Header
from fastapi.responses import JSONResponse, HTMLResponse
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel


class Config:
    """Configuration management"""
    
    def __init__(self, config_file: str = "config.json"):
        with open(config_file) as f:
            self.config = json.load(f)
    
    @property
    def github_client_id(self) -> str:
        return self.config["github"]["client_id"]
    
    @property
    def github_client_secret(self) -> str:
        return self.config["github"]["client_secret"]
    
    @property
    def server_host(self) -> str:
        return self.config["server"]["host"]
    
    @property
    def server_port(self) -> int:
        return self.config["server"]["port"]
    
    @property
    def server_url(self) -> str:
        return f"http://{self.server_host}:{self.server_port}"


class TokenValidator:
    """Validates OAuth tokens with GitHub"""
    
    def __init__(self):
        self.cache: Dict[str, Dict[str, Any]] = {}
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate token with GitHub API
        
        Returns user info if valid, None otherwise
        """
        # Check cache first
        if token in self.cache:
            return self.cache[token]
        
        # Validate with GitHub
        try:
            response = requests.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                timeout=5
            )
            
            if response.status_code == 200:
                user_info = response.json()
                self.cache[token] = user_info
                return user_info
            else:
                return None
        except Exception as e:
            print(f"Token validation error: {e}")
            return None
    
    def clear_cache(self):
        """Clear token cache"""
        self.cache.clear()


# Global instances
config = Config()
token_validator = TokenValidator()

# Create FastMCP server for tools
mcp = FastMCP("github-auth-mcp-server")


# ============================================================================
# MCP TOOLS - Protected by OAuth2
# ============================================================================

@mcp.tool()
def calculator_add(a: int, b: int) -> int:
    """
    Add two numbers
    
    Args:
        a: First number
        b: Second number
    
    Returns:
        Sum of a and b
    """
    return a + b


@mcp.tool()
def calculator_multiply(a: int, b: int) -> int:
    """
    Multiply two numbers
    
    Args:
        a: First number
        b: Second number
    
    Returns:
        Product of a and b
    """
    return a * b


@mcp.tool()
def greeter_hello(name: str) -> str:
    """
    Greet someone
    
    Args:
        name: Name of the person to greet
    
    Returns:
        Greeting message
    """
    return f"Hello, {name}! Welcome to the authenticated MCP server!"


@mcp.tool()
def greeter_goodbye(name: str) -> str:
    """
    Say goodbye to someone
    
    Args:
        name: Name of the person
    
    Returns:
        Goodbye message
    """
    return f"Goodbye, {name}! Thanks for using our secure MCP server!"


@mcp.tool()
def get_server_info() -> Dict[str, Any]:
    """
    Get information about the MCP server
    
    Returns:
        Server information including name, version, and capabilities
    """
    return {
        "name": "github-auth-mcp-server",
        "version": "1.0.0",
        "authentication": "GitHub OAuth2",
        "transport": "HTTP with SSE",
        "tools": ["calculator_add", "calculator_multiply", "greeter_hello", "greeter_goodbye", "get_server_info"],
        "specification": "MCP Authorization 2025-06-18"
    }


# ============================================================================
# AUTHENTICATION MIDDLEWARE
# ============================================================================

async def verify_token(authorization: Optional[str]) -> Dict[str, Any]:
    """
    Verify OAuth token from Authorization header
    
    Args:
        authorization: Authorization header value
    
    Returns:
        User information if token is valid
    
    Raises:
        HTTPException: If token is missing or invalid
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": f'Bearer realm="{config.server_url}/.well-known/oauth-protected-resource"'}
        )
    
    # Extract Bearer token
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": f'Bearer realm="{config.server_url}/.well-known/oauth-protected-resource"'}
        )
    
    token = authorization[7:]  # Remove "Bearer " prefix
    
    # Validate token
    user_info = token_validator.validate_token(token)
    
    if not user_info:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": f'Bearer realm="{config.server_url}/.well-known/oauth-protected-resource"'}
        )
    
    return user_info


# ============================================================================
# FASTAPI APP WITH MCP + OAUTH2
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    print("\n" + "=" * 70)
    print("🔐 MCP Server with GitHub OAuth2 Authentication")
    print("=" * 70)
    print()
    print("📋 Server Information:")
    print(f"   Server URL: {config.server_url}")
    print(f"   MCP Transport: HTTP with SSE")
    print(f"   Authentication: GitHub OAuth2")
    print()
    print("🔗 OAuth Metadata Endpoints:")
    print(f"   Protected Resource: {config.server_url}/.well-known/oauth-protected-resource")
    print(f"   Authorization Server: {config.server_url}/.well-known/oauth-authorization-server")
    print()
    print("🔗 MCP Endpoints:")
    print(f"   SSE Endpoint: {config.server_url}/sse")
    print(f"   Messages Endpoint: {config.server_url}/messages")
    print()
    print("🛠️  Available Tools:")
    print("   - calculator_add - Add two numbers")
    print("   - calculator_multiply - Multiply two numbers")
    print("   - greeter_hello - Greet someone")
    print("   - greeter_goodbye - Say goodbye")
    print("   - get_server_info - Get server information")
    print()
    print("✅ Server is ready! All MCP tools require authentication.")
    print("=" * 70)
    print()
    yield
    print("\n🛑 Shutting down server...")


# Create FastAPI app
app = FastAPI(
    title="MCP Server with GitHub OAuth2",
    description="Model Context Protocol server with OAuth2 authentication",
    version="1.0.0",
    lifespan=lifespan
)


# ============================================================================
# OAUTH2 METADATA ENDPOINTS (RFC 9728, RFC 8414)
# ============================================================================

@app.get("/.well-known/oauth-protected-resource")
async def protected_resource_metadata():
    """
    Protected Resource Metadata (RFC 9728)
    
    Indicates which authorization server(s) protect this resource
    """
    return {
        "resource": config.server_url,
        "authorization_servers": [config.server_url],
        "bearer_methods_supported": ["header"],
        "resource_documentation": "https://github.com/datalayer/mcp-server-composer/tree/main/examples/simple-auth"
    }


@app.get("/.well-known/oauth-authorization-server")
async def authorization_server_metadata():
    """
    Authorization Server Metadata (RFC 8414)
    
    Describes OAuth endpoints and capabilities
    This server proxies to GitHub OAuth
    """
    return {
        "issuer": config.server_url,
        "authorization_endpoint": "https://github.com/login/oauth/authorize",
        "token_endpoint": "https://github.com/login/oauth/access_token",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code"],
        "code_challenge_methods_supported": ["S256"],
        "token_endpoint_auth_methods_supported": ["client_secret_post"],
        "service_documentation": "https://docs.github.com/en/developers/apps/building-oauth-apps"
    }


# ============================================================================
# OAUTH2 CALLBACK ENDPOINT
# ============================================================================

@app.get("/callback")
async def oauth_callback(code: Optional[str] = None, state: Optional[str] = None):
    """
    OAuth callback endpoint
    
    Users are redirected here after authorizing with GitHub
    """
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Authentication Successful</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                text-align: center;
                max-width: 500px;
            }
            h1 { color: #667eea; margin-bottom: 20px; }
            p { color: #666; margin-bottom: 15px; }
            .success-icon { font-size: 60px; margin-bottom: 20px; }
            .code { background: #f4f4f4; padding: 10px; border-radius: 5px; 
                    font-family: monospace; word-break: break-all; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="success-icon">✅</div>
            <h1>Authentication Successful!</h1>
            <p>You have successfully authenticated with GitHub.</p>
            <p>You can now close this window and return to your application.</p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "authentication": "required",
        "oauth_provider": "GitHub"
    }


# ============================================================================
# MCP ENDPOINTS WITH AUTHENTICATION
# ============================================================================

@app.get("/sse")
async def handle_sse(request: Request, authorization: Optional[str] = Header(None)):
    """
    SSE endpoint for MCP protocol
    
    Requires OAuth2 authentication via Bearer token
    """
    # Verify authentication
    user_info = await verify_token(authorization)
    
    # Add user context to request state
    request.state.user = user_info
    
    # Forward to MCP SSE handler
    return await mcp.sse_handler(request)


@app.post("/messages")
async def handle_messages(request: Request, authorization: Optional[str] = Header(None)):
    """
    Messages endpoint for MCP protocol
    
    Requires OAuth2 authentication via Bearer token
    """
    # Verify authentication
    user_info = await verify_token(authorization)
    
    # Add user context to request state
    request.state.user = user_info
    
    # Forward to MCP message handler
    return await mcp.messages_handler(request)


# ============================================================================
# CONVENIENCE ENDPOINTS FOR TESTING
# ============================================================================

@app.get("/tools")
async def list_tools(authorization: Optional[str] = Header(None)):
    """
    List available MCP tools (requires authentication)
    
    This is a convenience endpoint for testing
    """
    # Verify authentication
    user_info = await verify_token(authorization)
    
    # Get tools from MCP server
    tools = []
    for tool_name, tool_func in mcp._tools.items():
        tools.append({
            "name": tool_name,
            "description": tool_func.__doc__.strip() if tool_func.__doc__ else "No description",
            "parameters": str(tool_func.__annotations__) if hasattr(tool_func, "__annotations__") else {}
        })
    
    return {
        "tools": tools,
        "authenticated_user": user_info.get("login"),
        "user_name": user_info.get("name")
    }


@app.get("/")
async def root():
    """Root endpoint with server information"""
    return {
        "name": "MCP Server with GitHub OAuth2",
        "version": "1.0.0",
        "mcp_version": "2024-11-05",
        "authentication": "GitHub OAuth2 (RFC 6749)",
        "authorization_spec": "MCP Authorization 2025-06-18",
        "endpoints": {
            "oauth_metadata": {
                "protected_resource": f"{config.server_url}/.well-known/oauth-protected-resource",
                "authorization_server": f"{config.server_url}/.well-known/oauth-authorization-server"
            },
            "mcp": {
                "sse": f"{config.server_url}/sse",
                "messages": f"{config.server_url}/messages"
            },
            "oauth": {
                "callback": f"{config.server_url}/callback"
            },
            "utility": {
                "health": f"{config.server_url}/health",
                "tools": f"{config.server_url}/tools"
            }
        },
        "documentation": "https://github.com/datalayer/mcp-server-composer/tree/main/examples/simple-auth"
    }


# ============================================================================
# RUN SERVER
# ============================================================================

def main():
    """Main entry point for running the server"""
    import uvicorn
    
    uvicorn.run(
        app,
        host=config.server_host,
        port=config.server_port,
        log_level="info"
    )


if __name__ == "__main__":
    main()
