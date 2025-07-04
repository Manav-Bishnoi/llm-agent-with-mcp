import asyncio
import json
from typing import Dict, Any
import httpx

class MCPClient:
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.tools = {}
    
    async def connect(self):
        """Initialize connection and get available tools"""
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.server_url}/initialize")
            self.tools = response.json().get("tools", {})
    
    async def call_tool(self, tool_name: str, params: Dict[str, Any]):
        """Call MCP tool via HTTP"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.server_url}/tools/{tool_name}/call",
                json={"params": params}
            )
            return response.json()

    async def discover_tools(self):
        """Discover available tools from the MCP server."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.server_url}/tools")
            self.tools = response.json().get("tools", {})

    async def health_check(self):
        """Check MCP server health."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.server_url}/health")
            return response.json()
