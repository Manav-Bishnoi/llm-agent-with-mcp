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

def suggest_plan(subject):
    try:
        prompt_str = f"""You are an education assistant. Based on the user's subject, provide a study plan.\nSubject: {subject}\nPlease provide a detailed study plan for this subject."""
        output = query_ollama(prompt_str, model="gemma3:4b")
        return {
            "success": True,
            "data": output,
            "agent": "education_agent",
            "command": "suggest_plan"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "agent": "education_agent",
            "command": "suggest_plan"
        }

def run_command(command, params):
    if command == "suggest_plan":
        return suggest_plan(params.get("subject", ""))
    else:
        return {
            "success": False,
            "error": f"Unknown command: {command}",
            "agent": "education_agent",
            "command": command
        }
