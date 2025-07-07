import requests

def call_agent_api(agent, command, params, context=None):
    url = f"http://localhost:8000/agent/{agent}/"
    payload = params.copy() if params else {}
    payload["command"] = command
    payload["user_id"] = "1"  # Add a dummy user_id for now
    payload["context"] = context
    print("payload: ", payload)
    response = requests.post(url, json=payload, timeout=30)
    print(f"[DEBUG] Response from agent API: {response.json()}", flush=True)
    print("response: ", response.json())
    response.raise_for_status()
    print("response status: ", response.status_code)
    return response.json() 