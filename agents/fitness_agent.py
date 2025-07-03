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


def suggest_plan(goal):
    try:
        prompt_str = f"""You are an AI fitness assistant. Based on the user's query answer.\n{goal}\nPlease provide a detailed workout plan to help achieve the goal of {goal}."""
        output = query_ollama(prompt_str, model="gemma3:4b")
        return {
            "success": True,
            "data": output,
            "agent": "fitness_agent",
            "command": "suggest_plan"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "agent": "fitness_agent",
            "command": "suggest_plan"
        }


def run_command(command, params):
    if command == "suggest_plan":
        return suggest_plan(params.get("goal", ""))
    else:
        return {
            "success": False,
            "error": f"Unknown command: {command}",
            "agent": "fitness_agent",
            "command": command
        }
