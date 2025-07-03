import requests

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

def suggest_itinerary(destination):
    try:
        prompt_str = f"""You are a travel assistant. Based on the user's destination, provide a travel itinerary.\nDestination: {destination}\nPlease provide a 3-day itinerary for this destination."""
        output = query_ollama(prompt_str, model="gemma3:4b")
        return {
            "success": True,
            "data": output,
            "agent": "travel_agent",
            "command": "suggest_itinerary"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "agent": "travel_agent",
            "command": "suggest_itinerary"
        }

def run_command(command, params):
    if command == "suggest_itinerary":
        return suggest_itinerary(params.get("destination", ""))
    else:
        return {
            "success": False,
            "error": f"Unknown command: {command}",
            "agent": "travel_agent",
            "command": command
        }
