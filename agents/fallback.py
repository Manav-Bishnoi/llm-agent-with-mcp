import requests

def fallback_command(agent_name, user_query=None):
    """
    Fallback function selector for agents not found in tool_info.
    If no agent/function is found, use gemma3:12b-it-qat from Ollama to answer directly.
    """
    if agent_name == 'food_agent':
        return 'suggest_meal'
    elif agent_name == 'fitness_agent':
        return 'suggest_plan'
    else:
        # Use Ollama's gemma3:12b-it-qat to answer directly
        if user_query is None:
            raise ValueError(f"No fallback command for agent '{agent_name}' and no user_query provided.")
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "gemma3:12b-it-qat",
                "prompt": user_query,
                "stream": False
            }
        )
        try:
            return response.json()["response"]
        except Exception:
            return "[Fallback LLM could not generate a response]"
