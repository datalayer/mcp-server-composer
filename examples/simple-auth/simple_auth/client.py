#!/usr/bin/env python3
"""
MCP Client with GitHub OAuth2 Authentication

This client demonstrates how to:
1. Discover OAuth metadata from an MCP server
2. Perform OAuth2 authorization flow with GitHub
3. Handle PKCE for security
4. Connect to MCP server via SSE transport with authentication
5. Invoke MCP tools with proper authentication

Learning Objectives:
1. Understand OAuth2 discovery process
2. Implement PKCE (Proof Key for Code Exchange)
3. Handle browser-based authentication flow
4. Use MCP SDK client with authenticated transport
"""

import json
import hashlib
import secrets
import base64
import webbrowser
from typing import Dict, Optional, Any
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse, urlencode
import requests
import threading
import time
import asyncio

# MCP client imports
try:
    from mcp import ClientSession
    from mcp.client.sse import sse_client
    HAS_MCP = True
except ImportError:
    HAS_MCP = False
    print("⚠️  MCP SDK not installed. Install with: pip install mcp")


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
    def server_url(self) -> str:
        host = self.config["server"]["host"]
        port = self.config["server"]["port"]
        return f"http://{host}:{port}"
    
    @property
    def callback_url(self) -> str:
        return f"{self.server_url}/callback"


class PKCEHelper:
    """Helper for PKCE (Proof Key for Code Exchange)"""
    
    @staticmethod
    def generate_code_verifier() -> str:
        """
        Generate a random code verifier
        
        Per RFC 7636: 43-128 characters, [A-Z] / [a-z] / [0-9] / "-" / "." / "_" / "~"
        """
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    
    @staticmethod
    def generate_code_challenge(verifier: str) -> str:
        """
        Generate code challenge from verifier using S256 method
        
        challenge = BASE64URL(SHA256(verifier))
        """
        digest = hashlib.sha256(verifier.encode('utf-8')).digest()
        return base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Handles OAuth callback from GitHub"""
    
    authorization_code: Optional[str] = None
    state: Optional[str] = None
    
    def do_GET(self):
        """Handle callback from OAuth provider"""
        query_components = parse_qs(urlparse(self.path).query)
        
        # Extract authorization code and state
        if "code" in query_components:
            OAuthCallbackHandler.authorization_code = query_components["code"][0]
        
        if "state" in query_components:
            OAuthCallbackHandler.state = query_components["state"][0]
        
        # Send success response
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Authentication Complete</title>
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
                }
                h1 { color: #667eea; margin-bottom: 20px; }
                p { color: #666; }
                .success-icon { font-size: 60px; margin-bottom: 20px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success-icon">✅</div>
                <h1>Authorization Complete!</h1>
                <p>You can close this window and return to your terminal.</p>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html.encode())
    
    def log_message(self, format, *args):
        """Suppress log messages"""
        pass


class MCPClient:
    """MCP Client with OAuth2 authentication"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config = Config(config_file)
        self.access_token: Optional[str] = None
        self.server_metadata: Optional[Dict] = None
        self.auth_server_metadata: Optional[Dict] = None
    
    def discover_metadata(self) -> bool:
        """
        Step 1: Discover OAuth metadata from MCP server
        
        Following MCP Authorization spec:
        1. Make unauthenticated request to server
        2. Receive 401 with WWW-Authenticate header
        3. Fetch Protected Resource Metadata (RFC 9728)
        4. Fetch Authorization Server Metadata (RFC 8414)
        """
        print("\n" + "=" * 70)
        print("🔍 STEP 1: Discovering OAuth Metadata")
        print("=" * 70)
        
        try:
            # Make unauthenticated request
            print(f"\n📡 Making unauthenticated request to: {self.config.server_url}/tools")
            response = requests.get(f"{self.config.server_url}/tools", timeout=5)
            
            if response.status_code == 401:
                print("✅ Received 401 Unauthorized (expected)")
                
                # Extract WWW-Authenticate header
                www_auth = response.headers.get("WWW-Authenticate")
                if not www_auth:
                    print("❌ Error: No WWW-Authenticate header found")
                    return False
                
                print(f"   WWW-Authenticate: {www_auth}")
                
                # Extract realm (protected resource metadata URL)
                if 'realm=' in www_auth:
                    realm = www_auth.split('realm="')[1].split('"')[0]
                    print(f"   Metadata URL: {realm}")
                else:
                    realm = f"{self.config.server_url}/.well-known/oauth-protected-resource"
                
                # Fetch Protected Resource Metadata
                print(f"\n📡 Fetching Protected Resource Metadata from: {realm}")
                pr_response = requests.get(realm, timeout=5)
                
                if pr_response.status_code != 200:
                    print(f"❌ Error: Failed to fetch protected resource metadata (status: {pr_response.status_code})")
                    return False
                
                self.server_metadata = pr_response.json()
                print("✅ Protected Resource Metadata received:")
                print(f"   {json.dumps(self.server_metadata, indent=3)}")
                
                # Extract authorization server URL
                auth_servers = self.server_metadata.get("authorization_servers", [])
                if not auth_servers:
                    print("❌ Error: No authorization servers found in metadata")
                    return False
                
                auth_server_url = auth_servers[0]
                print(f"\n📡 Authorization Server: {auth_server_url}")
                
                # Fetch Authorization Server Metadata
                as_metadata_url = f"{auth_server_url}/.well-known/oauth-authorization-server"
                print(f"📡 Fetching Authorization Server Metadata from: {as_metadata_url}")
                
                as_response = requests.get(as_metadata_url, timeout=5)
                
                if as_response.status_code != 200:
                    print(f"❌ Error: Failed to fetch authorization server metadata (status: {as_response.status_code})")
                    return False
                
                self.auth_server_metadata = as_response.json()
                print("✅ Authorization Server Metadata received:")
                print(f"   {json.dumps(self.auth_server_metadata, indent=3)}")
                
                return True
            
            else:
                print(f"❌ Error: Expected 401, got {response.status_code}")
                return False
        
        except Exception as e:
            print(f"❌ Error during metadata discovery: {e}")
            return False
    
    def authenticate(self) -> bool:
        """
        Step 2: Perform OAuth2 authentication flow
        
        Following OAuth 2.1 with PKCE:
        1. Generate PKCE parameters
        2. Build authorization URL
        3. Open browser for user authentication
        4. Receive authorization code via callback
        5. Exchange code for access token
        """
        print("\n" + "=" * 70)
        print("🔐 STEP 2: OAuth2 Authentication Flow")
        print("=" * 70)
        
        if not self.auth_server_metadata:
            print("❌ Error: No authorization server metadata. Run discover_metadata() first.")
            return False
        
        # Generate PKCE parameters
        print("\n🔑 Generating PKCE parameters...")
        code_verifier = PKCEHelper.generate_code_verifier()
        code_challenge = PKCEHelper.generate_code_challenge(code_verifier)
        print(f"   Code Verifier: {code_verifier[:20]}... (truncated)")
        print(f"   Code Challenge: {code_challenge[:20]}... (truncated)")
        
        # Generate state for CSRF protection
        state = secrets.token_urlsafe(32)
        print(f"   State: {state[:20]}... (truncated)")
        
        # Build authorization URL
        auth_endpoint = self.auth_server_metadata["authorization_endpoint"]
        
        params = {
            "client_id": self.config.github_client_id,
            "redirect_uri": self.config.callback_url,
            "response_type": "code",
            "scope": "user",
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            # RFC 8707: Resource parameter binds token to MCP server
            "resource": self.config.server_url
        }
        
        auth_url = f"{auth_endpoint}?{urlencode(params)}"
        
        print(f"\n🌐 Opening browser for GitHub authentication...")
        print(f"   URL: {auth_url[:80]}... (truncated)")
        
        # Start local callback server
        callback_server = HTTPServer(
            (self.config.config["server"]["host"], self.config.config["server"]["port"]),
            OAuthCallbackHandler
        )
        
        # Reset class variables
        OAuthCallbackHandler.authorization_code = None
        OAuthCallbackHandler.state = None
        
        # Run callback server in background thread
        server_thread = threading.Thread(target=callback_server.handle_request)
        server_thread.daemon = True
        server_thread.start()
        
        # Open browser
        webbrowser.open(auth_url)
        
        print("⏳ Waiting for user authorization...")
        print("   Please complete the authentication in your browser.")
        
        # Wait for callback
        timeout = 300  # 5 minutes
        start_time = time.time()
        
        while OAuthCallbackHandler.authorization_code is None:
            if time.time() - start_time > timeout:
                print("❌ Timeout waiting for authorization")
                callback_server.shutdown()
                return False
            time.sleep(0.5)
        
        callback_server.shutdown()
        
        # Verify state
        if OAuthCallbackHandler.state != state:
            print("❌ Error: State mismatch (possible CSRF attack)")
            return False
        
        print("✅ Authorization code received")
        
        # Exchange authorization code for access token
        print("\n🔄 Exchanging authorization code for access token...")
        
        token_endpoint = self.auth_server_metadata["token_endpoint"]
        
        token_data = {
            "client_id": self.config.github_client_id,
            "client_secret": self.config.github_client_secret,
            "code": OAuthCallbackHandler.authorization_code,
            "redirect_uri": self.config.callback_url,
            "code_verifier": code_verifier,
            "grant_type": "authorization_code"
        }
        
        token_response = requests.post(
            token_endpoint,
            data=token_data,
            headers={"Accept": "application/json"},
            timeout=10
        )
        
        if token_response.status_code != 200:
            print(f"❌ Error: Token exchange failed (status: {token_response.status_code})")
            print(f"   Response: {token_response.text}")
            return False
        
        token_data = token_response.json()
        self.access_token = token_data.get("access_token")
        
        if not self.access_token:
            print("❌ Error: No access token in response")
            return False
        
        print("✅ Access token received")
        print(f"   Token: {self.access_token[:20]}... (truncated)")
        
        return True
    
    def list_tools(self) -> Optional[Dict[str, Any]]:
        """
        Step 3: Make authenticated request to list tools
        """
        print("\n" + "=" * 70)
        print("🛠️  STEP 3: Listing Available Tools")
        print("=" * 70)
        
        if not self.access_token:
            print("❌ Error: No access token. Run authenticate() first.")
            return None
        
        try:
            response = requests.get(
                f"{self.config.server_url}/tools",
                headers={"Authorization": f"Bearer {self.access_token}"},
                timeout=5
            )
            
            if response.status_code == 200:
                tools = response.json()
                print("✅ Tools retrieved successfully:")
                for tool in tools.get("tools", []):
                    print(f"\n   📦 {tool['name']}")
                    print(f"      {tool['description']}")
                return tools
            else:
                print(f"❌ Error: Failed to list tools (status: {response.status_code})")
                return None
        
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    async def invoke_tool_mcp(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Any]:
        """
        Invoke an MCP tool using the MCP SDK client
        
        Args:
            tool_name: Name of the tool to invoke
            arguments: Tool arguments
        
        Returns:
            Tool result or None on error
        """
        if not HAS_MCP:
            print("❌ Error: MCP SDK not installed")
            return None
        
        if not self.access_token:
            print("❌ Error: No access token")
            return None
        
        print(f"\n🔧 Invoking tool via MCP protocol: {tool_name}")
        print(f"   Arguments: {arguments}")
        
        try:
            # Create headers with authentication
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            # Connect to MCP server via SSE
            async with sse_client(
                url=f"{self.config.server_url}/sse",
                headers=headers
            ) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize the session
                    await session.initialize()
                    
                    # Call the tool
                    result = await session.call_tool(tool_name, arguments)
                    
                    print(f"✅ Tool invoked successfully via MCP:")
                    print(f"   Result: {json.dumps(result.model_dump(), indent=3)}")
                    
                    return result
        
        except Exception as e:
            print(f"❌ Error invoking tool: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def invoke_tool_http(self, tool_name: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Invoke a tool using direct HTTP (for testing/comparison)
        
        Note: This is a simplified version. The proper way is to use MCP protocol.
        """
        print(f"\n🔧 Invoking tool via HTTP: {tool_name}")
        print(f"   Parameters: {params}")
        
        if not self.access_token:
            print("❌ Error: No access token. Run authenticate() first.")
            return None
        
        # This would need a custom endpoint on the server
        # For now, just show that we would use the MCP protocol
        print("   ℹ️  Use invoke_tool_mcp() for proper MCP protocol invocation")
        return None
    
    def demo(self):
        """Run a complete demonstration"""
        print("\n" + "=" * 70)
        print("🚀 MCP Client with GitHub OAuth2 - Complete Demo")
        print("=" * 70)
        print("\nThis demo will:")
        print("1. Discover OAuth metadata from the MCP server")
        print("2. Authenticate you via GitHub OAuth2")
        print("3. List available tools on the MCP server")
        print("4. Invoke example tools using MCP protocol")
        print("\nPress Enter to start...")
        input()
        
        # Step 1: Discover metadata
        if not self.discover_metadata():
            print("\n❌ Demo failed at metadata discovery")
            return
        
        print("\n✅ Metadata discovery complete!")
        print("\nPress Enter to continue with authentication...")
        input()
        
        # Step 2: Authenticate
        if not self.authenticate():
            print("\n❌ Demo failed at authentication")
            return
        
        print("\n✅ Authentication complete!")
        print("\nPress Enter to list tools...")
        input()
        
        # Step 3: List tools
        tools = self.list_tools()
        if not tools:
            print("\n❌ Demo failed at listing tools")
            return
        
        print("\n✅ Tools listed!")
        print("\nPress Enter to invoke example tools...")
        input()
        
        # Step 4: Invoke tools using MCP protocol
        if not HAS_MCP:
            print("\n⚠️  MCP SDK not available, skipping tool invocation")
            print("   Install with: pip install mcp")
        else:
            print("\n" + "=" * 70)
            print("🎯 STEP 4: Invoking Example Tools via MCP Protocol")
            print("=" * 70)
            
            # Run async tool invocations
            asyncio.run(self._demo_invoke_tools())
        
        print("\n" + "=" * 70)
        print("🎉 Demo Complete!")
        print("=" * 70)
        print("\nYou have successfully:")
        print("✅ Discovered OAuth metadata")
        print("✅ Authenticated with GitHub")
        print("✅ Listed available tools")
        if HAS_MCP:
            print("✅ Invoked MCP tools with authentication")
        print("\n🎓 You now understand how MCP authorization works!")
        print("=" * 70)
    
    async def _demo_invoke_tools(self):
        """Internal method to invoke tools for demo"""
        # Calculator examples
        await self.invoke_tool_mcp("calculator_add", {"a": 15, "b": 27})
        await asyncio.sleep(1)
        
        await self.invoke_tool_mcp("calculator_multiply", {"a": 8, "b": 9})
        await asyncio.sleep(1)
        
        # Greeter examples
        await self.invoke_tool_mcp("greeter_hello", {"name": "Alice"})
        await asyncio.sleep(1)
        
        await self.invoke_tool_mcp("greeter_goodbye", {"name": "Bob"})
        await asyncio.sleep(1)
        
        # Server info
        await self.invoke_tool_mcp("get_server_info", {})


def main():
    """Main entry point"""
    try:
        client = MCPClient()
        client.demo()
    except KeyboardInterrupt:
        print("\n\n🛑 Demo cancelled by user")
    except FileNotFoundError:
        print("\n❌ Error: config.json not found")
        print("Please create config.json with your GitHub OAuth credentials")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
