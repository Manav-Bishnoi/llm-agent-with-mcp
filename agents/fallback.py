import requests
from typing import Optional

def query_ollama_with_context(prompt, context="", model="gemma3:12b-it-qat"):
    """Query Ollama with context for fallback"""
    full_prompt = f"""
Previous conversation context:
{context}

Current request: {prompt}

Please provide a helpful response considering the conversation history.
"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": full_prompt,
                "stream": False
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()["response"]
    except Exception as e:
        return f"[Fallback LLM error: {str(e)}]"

def fallback_command_with_context(agent_name: str, user_query: str, context: str = ""):
    """Enhanced fallback with context support"""
    agent_commands = {
        'food_agent': 'suggest_meal',
        'fitness_agent': 'suggest_plan',
        'healthcare_agent': 'suggest_advice',
        'education_agent': 'suggest_plan',
        'finance_agent': 'suggest_plan',
        'law_agent': 'suggest_advice',
        'travel_agent': 'suggest_itinerary'
    }
    if agent_name in agent_commands:
        return agent_commands[agent_name]
    prompt = f"""
Agent '{agent_name}' was requested but not found.
User query: {user_query}
Context: {context}

Please provide a helpful response to the user's query.
"""
    return query_ollama_with_context(prompt, context)

def fallback_agent_execution(agent_name: str, command: str, params: dict, user_query: str, context: str = ""):
    """Execute fallback when agent fails"""
    try:
        if agent_name in ['food_agent', 'fitness_agent']:
            fallback_prompt = f"""
You are a {agent_name.replace('_', ' ')} assistant.
Context: {context}
User request: {user_query}
Parameters: {params}

Please provide helpful advice for this request.
"""
            response = query_ollama_with_context(fallback_prompt, context)
            return {
                "success": True,
                "data": response,
                "agent": f"{agent_name}_fallback",
                "command": command,
                "note": "Executed via fallback system"
            }
        else:
            response = query_ollama_with_context(user_query, context)
            return {
                "success": True,
                "data": response,
                "agent": "general_fallback",
                "command": "direct_response",
                "note": "Executed via general fallback"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Fallback execution failed: {str(e)}",
            "agent": f"{agent_name}_fallback",
            "command": command
        }

def fallback_command(agent_name, user_query=None):
    # Legacy fallback for compatibility
    return fallback_command_with_context(agent_name, user_query or "", "")
