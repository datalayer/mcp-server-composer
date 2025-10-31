"""
Tool Proxy Module.

This module handles communication with child MCP servers via STDIO
and proxies tool calls to them.
"""

import asyncio
import json
import logging
from typing import Any, Dict, Optional

from mcp.server.fastmcp.tools.base import Tool
from .process import Process
from .process_manager import ProcessManager

logger = logging.getLogger(__name__)


class ToolProxy:
    """
    Proxies MCP tool calls to child STDIO processes.
    
    Handles MCP protocol communication over STDIO to discover tools
    and execute them on child servers.
    """
    
    def __init__(self, process_manager: ProcessManager, composer: Any):
        """
        Initialize tool proxy.
        
        Args:
            process_manager: ProcessManager instance managing child processes
            composer: MCPServerComposer instance for registering discovered tools
        """
        self.process_manager = process_manager
        self.composer = composer
        self.server_tools: Dict[str, Dict[str, Any]] = {}
        
    async def discover_tools(self, server_name: str, process: Process) -> None:
        """
        Discover tools from a child MCP server via STDIO.
        
        Args:
            server_name: Name of the server
            process: Process instance running the MCP server
        """
        try:
            logger.info(f"Starting tool discovery for {server_name}")
            
            # Send MCP initialize request
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "clientInfo": {
                        "name": "mcp-server-composer",
                        "version": "0.1.0"
                    }
                }
            }
            
            logger.debug(f"Sending initialize request to {server_name}")
            response = await self._send_request(process, init_request)
            
            if not response:
                logger.error(f"No response to initialize from {server_name}")
                return
                
            if "error" in response:
                logger.error(f"Failed to initialize {server_name}: {response.get('error')}")
                return
            
            logger.debug(f"Initialize response from {server_name}: {response}")
            
            # Send initialized notification
            initialized_notification = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            }
            await self._send_notification(process, initialized_notification)
            
            # Request tools list
            tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            logger.debug(f"Requesting tools list from {server_name}")
            tools_response = await self._send_request(process, tools_request)
            
            if not tools_response:
                logger.error(f"No response to tools/list from {server_name}")
                return
            
            logger.debug(f"Tools list response from {server_name}: {tools_response}")
            
            if tools_response and "result" in tools_response:
                tools = tools_response["result"].get("tools", [])
                logger.info(f"Discovered {len(tools)} tools from {server_name}: {[t.get('name') for t in tools]}")
                
                # Register each tool as a proxy
                for tool in tools:
                    tool_name = tool.get("name")
                    if tool_name:
                        # Create proxy function for this tool
                        self._register_tool_proxy(server_name, tool_name, tool, process)
                
                logger.info(f"Registered {len(tools)} proxy tools from {server_name}")
                
        except Exception as e:
            logger.error(f"Error discovering tools from {server_name}: {e}", exc_info=True)
    
    def _register_tool_proxy(self, server_name: str, tool_name: str, tool_def: Dict[str, Any], process: Process) -> None:
        """
        Register a proxy function for a tool.
        
        Args:
            server_name: Name of the server providing the tool
            tool_name: Name of the tool
            tool_def: Tool definition from MCP protocol
            process: Process instance to communicate with
        """
        # Apply name prefix based on conflict resolution
        from .composer import ConflictResolution
        
        if self.composer.conflict_resolution == ConflictResolution.PREFIX:
            prefixed_name = f"{server_name}:{tool_name}"
        else:
            prefixed_name = tool_name
        
        # Create a closure to capture the current values
        def make_proxy_tool(srv_name: str, tl_name: str, proc: Process):
            async def proxy_tool(**kwargs) -> str:
                """Proxy function that forwards tool calls to child process."""
                try:
                    request = {
                        "jsonrpc": "2.0",
                        "id": "tool-call",
                        "method": "tools/call",
                        "params": {
                            "name": tl_name,
                            "arguments": kwargs
                        }
                    }
                    
                    response = await self._send_request(proc, request)
                    
                    if response and "result" in response:
                        result = response["result"]
                        # Handle MCP protocol response format
                        if isinstance(result, dict) and "content" in result:
                            content = result["content"]
                            if isinstance(content, list) and len(content) > 0:
                                # Return the text from the first content item
                                return content[0].get("text", str(content))
                            return str(content)
                        return str(result)
                    elif response and "error" in response:
                        error = response["error"]
                        raise RuntimeError(f"Tool execution error: {error.get('message', 'Unknown error')}")
                    else:
                        raise RuntimeError("No response from tool execution")
                        
                except Exception as e:
                    logger.error(f"Error calling tool {tl_name} on {srv_name}: {e}")
                    raise
            
            return proxy_tool
        
        # Create the proxy function with closure
        proxy_func = make_proxy_tool(server_name, tool_name, process)
        
        # Set function metadata (for Python introspection)
        # Note: Function name must be valid Python identifier
        safe_name = prefixed_name.replace(":", "_").replace("-", "_")
        proxy_func.__name__ = safe_name
        proxy_func.__doc__ = tool_def.get("description", "")
        
        # Register with FastMCP server - create a Tool object with the prefixed name
        # FastMCP's ToolManager stores Tool objects, not raw functions
        try:
            # Use the prefixed_name (with colons) for the MCP tool name
            tool_obj = Tool.from_function(
                proxy_func,
                name=prefixed_name,  # This is the MCP protocol name (can have colons)
                description=tool_def.get("description", "")
            )
            self.composer.composed_server._tool_manager._tools[tool_obj.name] = tool_obj
            logger.info(f"Registered proxy tool: {tool_obj.name} (maps to {tool_name} on {server_name})")
        except Exception as e:
            logger.error(f"Failed to register tool {prefixed_name}: {e}", exc_info=True)
            raise
        
        # Also track in composer's composed_tools dict
        self.composer.composed_tools[prefixed_name] = {
            "description": tool_def.get("description", ""),
            "inputSchema": tool_def.get("inputSchema", {})
        }
        self.composer.source_mapping[prefixed_name] = server_name
        
    async def _send_request(self, process: Process, request: Dict[str, Any], timeout: float = 5.0) -> Optional[Dict[str, Any]]:
        """
        Send a JSON-RPC request to a child process and wait for response.
        
        Args:
            process: Process instance to send to
            request: JSON-RPC request dict
            timeout: Timeout in seconds
            
        Returns:
            Response dict or None if timeout/error
        """
        if not process._stdin_writer or not process._stdout_reader:
            logger.error(f"Process {process.name} has no stdin/stdout")
            return None
        
        try:
            # Send request
            request_json = json.dumps(request) + "\n"
            process._stdin_writer.write(request_json.encode())
            await process._stdin_writer.drain()
            
            # Read response with timeout
            try:
                response_line = await asyncio.wait_for(
                    process._stdout_reader.readline(),
                    timeout=timeout
                )
                
                if response_line:
                    response = json.loads(response_line.decode().strip())
                    return response
                else:
                    logger.warning(f"Empty response from {process.name}")
                    return None
                    
            except asyncio.TimeoutError:
                logger.warning(f"Timeout waiting for response from {process.name}")
                return None
                
        except Exception as e:
            logger.error(f"Error sending request to {process.name}: {e}")
            return None
    
    async def _send_notification(self, process: Process, notification: Dict[str, Any]) -> None:
        """
        Send a JSON-RPC notification to a child process (no response expected).
        
        Args:
            process: Process instance to send to
            notification: JSON-RPC notification dict
        """
        if not process._stdin_writer:
            logger.error(f"Process {process.name} has no stdin")
            return
        
        try:
            notification_json = json.dumps(notification) + "\n"
            process._stdin_writer.write(notification_json.encode())
            await process._stdin_writer.drain()
        except Exception as e:
            logger.error(f"Error sending notification to {process.name}: {e}")
