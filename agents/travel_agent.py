import requests
from backend.core.context_manager import ContextManager

def query_ollama(prompt, model="gemma3:4b"):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        }
    )
    return response.json()["response"]

def suggest_itinerary(destination, context_list=None):
    if context_list is None:
        context_list = []
    cm = ContextManager()
    context_str = cm.format_context_for_agent(context_list)
    prompt_str = f"You are a travel assistant. Based on the user's destination and conversation history, provide a travel itinerary.\n\n{context_str}\nDestination: {destination}\nPlease provide a detailed itinerary, considering any previous discussions."
    output = query_ollama(prompt_str, model="gemma3:4b")
    return {
        "success": True,
        "data": output,
        "agent": "travel_agent",
        "command": "suggest_itinerary"
    }

def run_command_with_context(command, params, context_list=None):
    if context_list is None:
        context_list = []
    if command == "suggest_itinerary":
        return suggest_itinerary(params.get("destination", ""), context_list)
    else:
        return {
            "success": False,
            "error": f"Unknown command: {command}",
            "agent": "travel_agent",
            "command": command
        }

def run_command(command, params):
    return run_command_with_context(command, params, [])
