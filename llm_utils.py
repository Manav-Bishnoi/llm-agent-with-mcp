import requests
import re
import json

def query_ollama(prompt, model="gemma3:4b"):
    try:
        res = requests.post("http://localhost:11434/api/generate", json={
            "model": model,
            "prompt": prompt,
            "stream": False
        }, timeout=10)
        return res.json()["response"]
    except Exception as e:
        print(f"Ollama connection failed: {e}")
        # Return a simple mock response for testing
        return mock_llm_response(prompt)

def mock_llm_response(prompt):
    """Provide a mock LLM response when Ollama is not available"""
    # Simple keyword-based routing for testing
    prompt_lower = prompt.lower()
    if any(word in prompt_lower for word in ['health', 'sick', 'pain', 'doctor']):
        return '{"agent": "healthcare_agent", "command": "suggest_advice", "params": {"symptom": "general health inquiry"}}'
    elif any(word in prompt_lower for word in ['exercise', 'workout', 'fitness']):
        return '{"agent": "fitness_agent", "command": "suggest_plan", "params": {"goal": "general fitness"}}'
    elif any(word in prompt_lower for word in ['money', 'finance', 'investment']):
        return '{"agent": "finance_agent", "command": "suggest_plan", "params": {"query": "general financial advice"}}'
    elif any(word in prompt_lower for word in ['travel', 'trip', 'vacation']):
        return '{"agent": "travel_agent", "command": "suggest_itinerary", "params": {"destination": "general travel"}}'
    elif any(word in prompt_lower for word in ['learn', 'study', 'education']):
        return '{"agent": "education_agent", "command": "suggest_plan", "params": {"topic": "general learning"}}'
    elif any(word in prompt_lower for word in ['law', 'legal', 'contract']):
        return '{"agent": "law_agent", "command": "suggest_advice", "params": {"query": "general legal advice"}}'
    else:
        # Default response - extract the actual query from the prompt
        # Find the user query in the prompt
        if "User Query:" in prompt:
            user_query = prompt.split("User Query:")[-1].strip()
        else:
            user_query = "general inquiry"
        return f'{{"agent": "healthcare_agent", "command": "suggest_advice", "params": {{"symptom": "{user_query}"}}}}'

def extract_json(raw):
    json_match = re.search(r'\{.*\}', raw, re.DOTALL)
    if json_match:
        json_str = json_match.group(0)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            raise ValueError("Extracted text is not valid JSON: " + json_str)
    else:
        raise ValueError("No JSON found in model output.")
