import requests

def query_ollama_with_context(prompt, context="", model="gemma3:4b"):
    full_prompt = f"""
Previous conversation context:
{context}

Current request:
{prompt}

Please provide a response that considers the conversation history above.
"""
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": full_prompt,
            "stream": False
        }
    )
    return response.json()["response"]

def suggest_itinerary(destination, context=""):
    prompt_str = f"""You are a travel assistant. Based on the user's destination and conversation history, provide a travel itinerary.\n\nContext: {context}\nCurrent Destination: {destination}\nPlease provide a 3-day itinerary for this destination, considering any previous discussions."""
    output = query_ollama_with_context(prompt_str, context, model="gemma3:4b")
    return {
        "success": True,
        "data": output,
        "agent": "travel_agent",
        "command": "suggest_itinerary"
    }

def run_command_with_context(command, params, context=""):
    if command == "suggest_itinerary":
        return suggest_itinerary(params.get("destination", ""), context)
    else:
        return {
            "success": False,
            "error": f"Unknown command: {command}",
            "agent": "travel_agent",
            "command": command
        }

def run_command(command, params):
    return run_command_with_context(command, params, "")
