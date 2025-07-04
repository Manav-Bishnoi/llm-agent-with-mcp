from context_manager import ContextManager
from agent_router import run_agent_with_error_handling, normalize_agent_call
from response_utils import parse_and_validate_response
from llm_utils import query_ollama
import uuid

class EnhancedPipeline:
    def __init__(self):
        self.context_manager = ContextManager()
        self.mcp_servers = {}
        self.current_conversation_id = None
        self.current_topic = None

    async def run_enhanced_pipeline(self, user_query: str, conversation_id: str = None):
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
        routing_prompt = self.build_routing_prompt(user_query, context)
        # Get LLM response for routing only
        routing_response = query_ollama(routing_prompt)
        # Parse routing response
        from tool_registry import load_tool_registry
        registry = load_tool_registry()
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
        from tool_registry import load_tool_registry
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
