# Import required modules for registry, LLM, and agent routing
from tool_registry import load_tool_registry  # Loads agent/tool registry from JSON
from llm_utils import query_ollama  # Function to query the LLM
from agent_router import normalize_agent_call  # Normalizes agent call structure
from prompt_builder import build_prompt_from_registry  # Builds prompt for LLM
from response_utils import parse_and_validate_response  # Parses and validates LLM response
import json  # For pretty-printing output
import requests  # For making HTTP API calls to agents

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
    print("Agent Output:")
    # If result is a dict with a single string value, print it directly
    if isinstance(result, dict) and len(result) == 1 and isinstance(list(result.values())[0], str):
        print(list(result.values())[0])
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))

# Call agent via API endpoint (always uses HTTP, even for local agents)
def run_agent_via_api(normalized, api_url="http://localhost:5000"): 
    agent = normalized["agent"]  # Agent name
    command = normalized["command"]  # Command to run
    params = normalized["params"]  # Parameters for command
    try:
        # Send POST request to agent API endpoint
        resp = requests.post(f"{api_url}/tools/{agent}/run", json={"command": command, "params": params}, timeout=30)
        resp.raise_for_status()  # Raise error if HTTP error
        return resp.json()  # Return JSON response
    except Exception as e:
        return {"error": f"API call failed: {e}"}

# Main pipeline: builds prompt, parses LLM, and calls agent via API
def run_agent_full(user_query, agent=None, api_url="http://localhost:5000"):
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
def main():
    registry = load_tool_registry()  # Load registry (not strictly needed here)
    print("--------------------------------------------------------------------------------------------")
    user_query = get_user_query()  # Get user input
    print("--------------------------------------------------------------------------------------------")
    prompt = build_prompt_from_registry(registry, user_query)  # Build prompt
    print("--------------------------------------------------------------------------------------------")
    print("Prompt sent to LLM:" + prompt)
    print("--------------------------------------------------------------------------------------------")
    response = get_llm_response(prompt)  # Query LLM
    print("--------------------------------------------------------------------------------------------")
    print("Response from LLM:", response)
    print("--------------------------------------------------------------------------------------------")
    parsed = parse_and_validate_response(response, registry, user_query)  # Parse response
    print("--------------------------------------------------------------------------------------------")
    if not parsed:
        return ('Invalid response format from main llm. Please try again.')
    print("--------------------------------------------------------------------------------------------")
    normalized = normalize_agent_call(parsed, registry)  # Normalize call
    print("--------------------------------------------------------------------------------------------")
    print("--------------------------------------------------------------------------------------------")
    try:
        result = run_agent_via_api(normalized)  # Call agent via API
        print_agent_output(result)  # Print result
    except Exception as e:
        print("Error:", e)
    print("--------------------------------------------------------------------------------------------")

if __name__ == "__main__":
    while True:
        try:
            main()  # Run CLI main loop
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"An error occurred: {e}. Please try again.")

