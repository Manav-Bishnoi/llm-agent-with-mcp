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

def suggest_plan(goal, context=""):
    prompt_str = f"""You are a financial planning assistant. Based on the user's goal and conversation history, provide a financial plan.\n\nContext: {context}\nCurrent Goal: {goal}\nPlease provide a step-by-step plan to achieve this financial goal, considering any previous discussions."""
    output = query_ollama_with_context(prompt_str, context, model="gemma3:4b")
    return {
        "success": True,
        "data": output,
        "agent": "finance_agent",
        "command": "suggest_plan"
    }

def run_command_with_context(command, params, context=""):
    if command == "suggest_plan":
        return suggest_plan(params.get("goal", ""), context)
    else:
        return {
            "success": False,
            "error": f"Unknown command: {command}",
            "agent": "finance_agent",
            "command": command
        }

def run_command(command, params):
    return run_command_with_context(command, params, "")
