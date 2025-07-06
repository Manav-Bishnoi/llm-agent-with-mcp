def build_prompt_from_registry(registry, user_query):
    prompt = "You are a JSON tool-calling assistant. You must respond ONLY with valid JSON.\n\n"
    prompt += "Available tools:\n"
    for name, agent in registry.items():
        prompt += f"- {name}: {agent['description']}\n"
        for func, func_info in agent["functions"].items():
            param_str = ", ".join(func_info["params"].keys())
            desc = func_info.get("description", "")
            prompt += f"    - {func}({param_str})  # {desc}\n"
    
    prompt += "\nIMPORTANT: Respond ONLY with valid JSON in this exact format:\n"
    prompt += '{"agent": "<agent_name>", "command": "<function_name>", "params": {...}}'"\n"
    prompt += "All required parameters must be present in 'params'.\n"
    prompt += "If no specific agent is needed, use 'healthcare_agent' with 'suggest_advice' command.\n"
    prompt += "DO NOT include any explanatory text, only the JSON response.\n"
    prompt += f"\nUser Query: {user_query}"
    return prompt
