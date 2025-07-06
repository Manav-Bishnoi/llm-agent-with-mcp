# Import required modules for registry, LLM, and agent routing
from backend.core.tool_registry import load_tool_registry  # Loads agent/tool registry from JSON
from backend.utils.llm_utils import query_ollama  # Function to query the LLM
from backend.api.agent_router import normalize_agent_call  # Normalizes agent call structure
from backend.core.prompt_builder import build_prompt_from_registry  # Builds prompt for LLM
from backend.utils.response_utils import parse_and_validate_response  # Parses and validates LLM response
import json  # For pretty-printing output
import requests  # For making HTTP API calls to agents
from backend.core.context_manager import ContextManager
import uuid

# Get user query from input (for CLI mode)
def get_user_query():
    query = input("Enter your query: ")  # Prompt user for input
    if query.strip().lower() == "/bye":  # Exit on /bye
        print("Exiting...")
        exit(0)
    return query

# Query the LLM with a prompt
def get_llm_response(prompt):
    return query_ollama(prompt)

# Print agent output in a readable way
def print_agent_output(result):
    # If result is a dict with a single string value, print it directly
    if isinstance(result, dict) and len(result) == 1 and isinstance(list(result.values())[0], str):
        print(list(result.values())[0])
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))

# Call agent via API endpoint (always uses HTTP, even for local agents)
def run_agent_via_api(normalized, api_url="http://localhost:8000"): 
    agent = normalized["agent"]  # Agent name
    command = normalized["command"]  # Command to run
    params = normalized["params"]  # Parameters for command
    try:
        # Send POST request to agent API endpoint
        resp = requests.post(f"{api_url}/tools/{agent}/run", json={"command": command, "params": params}, timeout=15)
        resp.raise_for_status()  # Raise error if HTTP error
        return resp.json()  # Return JSON response
    except Exception as e:
        return {"error": f"API call failed: {e}"}

# Main pipeline: builds prompt, parses LLM, and calls agent via API
def run_agent_full(user_query, agent=None, api_url="http://localhost:8000"):
    registry = load_tool_registry()  # Load agent registry
    prompt = build_prompt_from_registry(registry, user_query)  # Build prompt for LLM
    response = get_llm_response(prompt)  # Query LLM
    parsed = parse_and_validate_response(response, registry, user_query)  # Parse LLM response
    if not parsed:
        return 'Invalid response format from main llm. Please try again.'
    normalized = normalize_agent_call(parsed, registry)  # Normalize agent call
    # If agent is specified, override
    if agent:
        normalized['agent'] = agent
    try:
        result = run_agent_via_api(normalized, api_url=api_url)  # Call agent via API
        return result
    except Exception as e:
        return f"Error: {e}"

# CLI main loop for testing and debugging
def main(user_query=None, conversation_id=None, topic="general"):
    registry = load_tool_registry()
    if conversation_id is None:
        conversation_id = str(uuid.uuid4())
    cm = ContextManager()
    if user_query is None:
        user_query = get_user_query()
    # Save user query to context
    cm.save_context(topic=topic, conversation_id=conversation_id, user_input=user_query, response_type="user")
    prompt = build_prompt_from_registry(registry, user_query)
    response = get_llm_response(prompt)
    parsed = parse_and_validate_response(response, registry, user_query)
    if not parsed:
        return {'error': 'Invalid response format from main llm. Please try again.'}
    normalized = normalize_agent_call(parsed, registry)
    try:
        # Call agent directly instead of through API to avoid circular calls
        result = run_agent_directly(normalized)
        # Save agent response to context
        if result and result.get('success'):
            cm.save_context(topic=topic, conversation_id=conversation_id, agent_response=json.dumps(result.get('data', str(result))), response_type="agent")
        return result
    except Exception as e:
        return {'error': str(e)}

def run_agent_directly(normalized):
    """Run agent directly without going through API"""
    agent = normalized["agent"]
    command = normalized["command"]
    params = normalized["params"]
    
    try:
        # Import and run the agent directly
        import importlib
        agent_module = importlib.import_module(f"agents.{agent}")
        
        # Check if agent has the required function
        if hasattr(agent_module, command):
            agent_func = getattr(agent_module, command)
            result = agent_func(**params)
            return {"success": True, "data": result, "agent": agent, "command": command}
        elif hasattr(agent_module, "run_command"):
            result = agent_module.run_command(command, params)
            return {"success": True, "data": result, "agent": agent, "command": command}
        else:
            return {"success": False, "error": f"Command '{command}' not found in agent '{agent}'"}
            
    except ImportError:
        return {"success": False, "error": f"Agent '{agent}' not found"}
    except Exception as e:
        return {"success": False, "error": f"Agent execution failed: {str(e)}"}

if __name__ == "__main__":
    conversation_id = str(uuid.uuid4())
    topic = "general"
    while True:
        try:
            user_query = get_user_query()
            result = main(user_query, conversation_id=conversation_id, topic=topic)
            print_agent_output(result)
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"An error occurred: {e}. Please try again.")

