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
    prompt_str = f"""You are a travel assistant. Based on the user's destination, provide a travel itinerary.\nDestination: {destination}\nPlease provide a 3-day itinerary for this destination."""
    output = query_ollama(prompt_str, model="gemma3:4b")
    return {"itinerary": f"Travel itinerary: {output}"}

def run_command(command, params):
    if command == "suggest_itinerary":
        return suggest_itinerary(params["destination"])
    else:
        return {"error": f"Unknown command: {command}"}
