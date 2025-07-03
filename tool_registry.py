import os
import json

def load_tool_registry():
    tool_registry = {}
    for f in os.listdir("agents"):
        if f.endswith("_agent.json"):
            with open(os.path.join("agents", f)) as file:
                data = json.load(file)
                tool_registry[data["name"]] = data
    return tool_registry

def validate_params(registry, parsed):
    agent = registry.get(parsed["agent"])
    if not agent:
        raise ValueError("Unknown agent.")
    func = agent["functions"].get(parsed["command"])
    if not func:
        raise ValueError("Unknown function.")
    expected = set(func["params"].keys())
    provided = set(parsed["params"].keys())
    if not expected.issubset(provided):
        raise ValueError("Missing parameters.")
