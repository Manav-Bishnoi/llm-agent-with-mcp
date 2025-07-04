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

def suggest_plan(subject, context=""):
    prompt_str = f"""You are an education assistant. Based on the user's subject and conversation history, provide a study plan.\n\nContext: {context}\nCurrent Subject: {subject}\nPlease provide a detailed study plan for this subject, considering any previous discussions."""
    output = query_ollama_with_context(prompt_str, context, model="gemma3:4b")
    return {
        "success": True,
        "data": output,
        "agent": "education_agent",
        "command": "suggest_plan"
    }

def run_command_with_context(command, params, context=""):
    if command == "suggest_plan":
        return suggest_plan(params.get("subject", ""), context)
    else:
        return {
            "success": False,
            "error": f"Unknown command: {command}",
            "agent": "education_agent",
            "command": command
        }

def run_command(command, params):
    return run_command_with_context(command, params, "")
