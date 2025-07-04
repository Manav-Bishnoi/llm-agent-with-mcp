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
    prompt_str = f"""You are an education assistant. Based on the user's subject, provide a study plan.\nSubject: {subject}\nPlease provide a detailed study plan for this subject."""
    output = query_ollama(prompt_str, model="gemma3:4b")
    return {"plan": f"Study plan: {output}"}

def run_command(command, params):
    if command == "suggest_plan":
        return suggest_plan(params["subject"])
    else:
        return {"error": f"Unknown command: {command}"}
