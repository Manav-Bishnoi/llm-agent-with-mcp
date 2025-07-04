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

# Query Ollama LLM with a prompt, context, and model
# Returns the generated response as a string
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

# Suggest a healthcare plan based on a symptom
# Returns a dictionary with the advice string
def suggest_advice(symptom, context=""):
    prompt_str = f"""You are a healthcare assistant. Based on the user's symptom and conversation history, provide advice.\n\nContext: {context}\nCurrent Symptom: {symptom}\nPlease provide a possible cause and recommended next steps, considering any previous health discussions."""
    output = query_ollama_with_context(prompt_str, context, model="gemma3:4b")
    return {
        "success": True,
        "data": output,
        "agent": "healthcare_agent",
        "command": "suggest_advice"
    }

# Standard API entry point for this agent
# Handles all API calls for this agent
def run_command_with_context(command, params, context=""):
    if command == "suggest_advice":
        return suggest_advice(params.get("symptom", ""), context)
    else:
        return {
            "success": False,
            "error": f"Unknown command: {command}",
            "agent": "healthcare_agent",
            "command": command
        }

def run_command(command, params):
    return run_command_with_context(command, params, "")
