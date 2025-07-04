def build_prompt_from_registry(registry, user_query):
    prompt = "You are a JSON tool-calling assistant.\n\n"
    prompt += "Available tools:\n"
    for name, agent in registry.items():
        prompt += f"- {name}: {agent['description']}\n"
        for func, func_info in agent["functions"].items():
            param_str = ", ".join(func_info["params"].keys())
            desc = func_info.get("description", "")
            prompt += f"    - {func}({param_str})  # {desc}\n"
    prompt += "\nRespond ONLY in JSON:\n"
    prompt += '{"agent": "<name>", "command": "<function>", "params": {...}}'"\n"
    prompt += "All required parameters must be present in 'params', it can be simply 'not provided', but should be present.\n"
    prompt += "When something of specific field is not required, you can simply call genral agent. ie.'{'agent': 'genral agent', 'command': 'give entire user query', 'params': {...}}'\n"
    prompt += f"\nhere is user Query: {user_query}"
    return prompt
