from context_manager import ContextManager
from mcp_client import MCPClient
from mcp_config import MCPConfig
from response_utils import parse_and_validate_response
from llm_utils import query_ollama
import asyncio
from typing import List, Dict

class EnhancedPipeline:
    def __init__(self):
        self.context_manager = ContextManager()
        self.mcp_servers = {}
        self.current_conversation_id = None
        self.current_topic = None
    
    async def add_mcp_server(self, name: str, url: str):
        client = MCPClient(url)
        await client.connect()
        self.mcp_servers[name] = client
    
    async def run_enhanced_pipeline(self, user_query: str, conversation_id: str = None):
        # Get relevant context
        if self.current_topic:
            context = self.context_manager.get_context(topic=self.current_topic)
        else:
            context = self.context_manager.get_context(conversation_id=conversation_id)
        # Build context-aware prompt
        context_prompt = self.build_context_prompt(user_query, context)
        # Get LLM response
        response = query_ollama(context_prompt)
        # Parse and route to MCP or local agent
        parsed = parse_and_validate_response(response, None, user_query)
        # Save context
        self.context_manager.save_context(
            topic=self.current_topic or "general",
            conversation_id=conversation_id or "default",
            content=f"Query: {user_query}\nResponse: {response}"
        )
        return await self.execute_parsed_command(parsed)
    
    def build_context_prompt(self, query: str, context: List[Dict]) -> str:
        prompt = "You are an AI assistant with access to previous conversation context.\n\n"
        if context:
            prompt += "Previous context:\n"
            for ctx in context[-3:]:
                prompt += f"- {ctx['content'][:200]}...\n"
            prompt += "\n"
        prompt += f"Available tools:\n"
        for server_name, client in self.mcp_servers.items():
            for tool_name, tool_info in client.tools.items():
                prompt += f"- {tool_name} (MCP): {tool_info.get('description', '')}\n"
        prompt += f"\nCurrent query: {query}\n"
        prompt += "Respond in JSON format with tool call or direct answer."
        return prompt
    
    async def execute_parsed_command(self, parsed):
        # Example: expects parsed to have {"tool": ..., "params": ...}
        if not parsed or not isinstance(parsed, dict):
            return {"error": "Invalid parsed command"}
        tool = parsed.get("tool")
        params = parsed.get("params", {})
        # Try all MCP servers for the tool
        for client in self.mcp_servers.values():
            if tool in client.tools:
                return await client.call_tool(tool, params)
        return {"error": f"Tool {tool} not found in any MCP server."}
