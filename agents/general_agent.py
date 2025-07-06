import requests
from context_manager import ContextManager

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

Please provide a helpful, general-purpose response considering the conversation history above.
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

def answer(query, context_list=None):
    if context_list is None:
        context_list = []
    cm = ContextManager()
    context_str = cm.format_context_for_agent(context_list)
    prompt_str = f"You are a helpful general-purpose assistant.\n\n{context_str}\nUser Query: {query}\nPlease provide a helpful, relevant answer."
    output = query_ollama(prompt_str, model="gemma3:4b")
    return {
        "success": True,
        "data": output,
        "agent": "general_agent",
        "command": "answer"
    }

def run_command_with_context(command, params, context_list=None):
    if context_list is None:
        context_list = []
    if command == "answer":
        return answer(params.get("query", ""), context_list)
    else:
        return {
            "success": False,
            "error": f"Unknown command: {command}",
            "agent": "general_agent",
            "command": command
        }

def run_command(command, params):
    return run_command_with_context(command, params, []) 