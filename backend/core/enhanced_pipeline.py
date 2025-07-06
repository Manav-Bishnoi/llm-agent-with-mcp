from backend.core.context_manager import ContextManager
from backend.api.agent_router import run_agent_with_error_handling, normalize_agent_call
from backend.utils.response_utils import parse_and_validate_response
from backend.utils.llm_utils import query_ollama
from backend.config.mcp_config import MCPConfig
from backend.utils.mcp_client import MCPClient
from backend.core.tool_registry import load_tool_registry
import uuid
from typing import Optional, Dict, Any

class EnhancedPipeline:
    def __init__(self):
        self.context_manager = ContextManager()
        self.mcp_servers: Dict[str, Any] = {}
        self.current_conversation_id: Optional[str] = None
        self.current_topic: Optional[str] = None

    async def add_mcp_server(self, name: str, url: str):
        """Add MCP server to the pipeline"""
        try:
            client = MCPClient(url)
            await client.connect()
            self.mcp_servers[name] = client
            return {"success": True, "message": f"MCP server {name} added successfully"}
        except Exception as e:
            return {"success": False, "error": f"Failed to add MCP server {name}: {str(e)}"}

    async def run_enhanced_pipeline(self, user_query: str, conversation_id: Optional[str] = None):
        # Generate conversation ID if not provided
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        # Save user query to context (NOT main model output)
        self.context_manager.save_context(
            topic=self.current_topic or "general",
            conversation_id=conversation_id,
            user_input=user_query,
            response_type="user"
        )
        # Get context for LLM (for routing, not agent execution)
        context = self.context_manager.get_filtered_context(
            topic=self.current_topic,
            conversation_id=conversation_id,
            exclude_main_model=True
        )
        # Build routing prompt
        registry = load_tool_registry()
        prompt = self.build_routing_prompt(user_query, context)
        # Get LLM response for routing only
        routing_response = query_ollama(prompt)
        # Parse routing response
        parsed = parse_and_validate_response(routing_response, registry, user_query)
        if not parsed:
            from agents.fallback import fallback_agent_execution
            result = fallback_agent_execution(
                "general", "direct_response", {}, user_query, context
            )
        else:
            normalized = normalize_agent_call(parsed, registry)
            result = run_agent_with_error_handling(
                normalized,
                self.context_manager,
                conversation_id=conversation_id,
                topic=self.current_topic
            )
        # Save agent response to context (NOT main model output)
        if result and result.get('success'):
            self.context_manager.save_context(
                topic=self.current_topic or "general",
                conversation_id=conversation_id,
                agent_response=result.get('data', str(result)),
                response_type="agent"
            )
        return result

    def build_routing_prompt(self, query: str, context: str) -> str:
        registry = load_tool_registry()
        prompt = f"""You are a routing assistant. Based on the user query and context, decide which agent to call.\n\nContext: {context}\n\nAvailable agents:\n"""
        for name, agent in registry.items():
            prompt += f"- {name}: {agent['description']}\n"
            for func, func_info in agent["functions"].items():
                param_str = ", ".join(func_info["params"].keys())
                desc = func_info.get("description", "")
                prompt += f"    - {func}({param_str}): {desc}\n"
        prompt += f"""\nCurrent query: {query}\n\nRespond ONLY in JSON format:\n{{"agent": "<agent_name>", "command": "<function_name>", "params": {{...}}}}\n\nAll required parameters must be present in 'params'.\n"""
        return prompt
