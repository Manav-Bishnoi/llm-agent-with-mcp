import requests  # Used for HTTP requests to Ollama and as agent API client

# Query Ollama LLM with a prompt and model
# Returns the generated response as a string
def query_ollama(prompt, model="gemma3:4b"):
    response = requests.post(
        "http://localhost:11434/api/generate",  # Ollama API endpoint
        json={
            "model": model,  # Model name
            "prompt": prompt,  # User/system prompt
            "stream": False  # No streaming, get full response
        }
    )
    return response.json()["response"]  # Extract response text

# Suggest a healthcare plan based on a symptom
# Returns a dictionary with the advice string
def suggest_advice(symptom):
    try:
        prompt_str = f"""You are a healthcare assistant. Based on the user's symptom, provide advice.\nSymptom: {symptom}\nPlease provide a possible cause and recommended next steps."""
        output = query_ollama(prompt_str, model="gemma3:4b")
        return {
            "success": True,
            "data": output,
            "agent": "healthcare_agent",
            "command": "suggest_advice"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "agent": "healthcare_agent",
            "command": "suggest_advice"
        }

# Standard API entry point for this agent
# Handles all API calls for this agent
def run_command(command, params):
    if command == "suggest_advice":
        return suggest_advice(params.get("symptom", ""))
    else:
        return {
            "success": False,
            "error": f"Unknown command: {command}",
            "agent": "healthcare_agent",
            "command": command
        }
