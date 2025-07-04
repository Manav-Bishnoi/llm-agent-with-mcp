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

def suggest_advice(question):
    prompt_str = f"""You are a legal assistant. Based on the user's question, provide general legal information.\nQuestion: {question}\nPlease provide a general answer and suggest next steps."""
    output = query_ollama(prompt_str, model="gemma3:4b")
    return {"advice": f"Legal advice: {output}"}

def run_command(command, params):
    if command == "suggest_advice":
        return suggest_advice(params["question"])
    else:
        return {"error": f"Unknown command: {command}"}
