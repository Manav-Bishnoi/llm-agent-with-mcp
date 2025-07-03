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
    prompt_str = f"""You are an AI fitness assistant. Based on the user's query answer.
{goal}
Please provide a detailed workout plan to help achieve the goal of {goal}."""
    output = query_ollama(prompt_str, model="gemma3:4b")
    return {"plan": f"Here’s a workout plan to help you achieve: {output}."}


def run_command(command, params):
    if command == "suggest_plan":
        return suggest_plan(params["goal"])
    else:
        return {"error": f"Unknown command: {command}"}
