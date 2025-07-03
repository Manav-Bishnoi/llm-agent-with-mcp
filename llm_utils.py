import requests
import re
import json

def query_ollama(prompt, model="gemma3:4b"):
    res = requests.post("http://localhost:11434/api/generate", json={
        "model": model,
        "prompt": prompt,
        "stream": False
    })
    return res.json()["response"]

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
