def parse_and_validate_response(response, registry, user_query):
    from llm_utils import extract_json
    try:
        parsed = extract_json(response)
        print("Parsed JSON:", parsed)
        from tool_registry import validate_params
        try:
            validate_params(registry, parsed)
        except ValueError as e:
            agent = parsed.get("agent")
            command = parsed.get("command")
            if agent and command and agent in registry and command in registry[agent]["functions"]:
                required = list(registry[agent]["functions"][command]["params"].keys())
                print(f"Error extracting JSON or validating params: {e}. Required parameters: {required}")
                return None
            else:
                # Fallback for unknown agent/function
                print(f"Unknown agent or function. Using fallback LLM...")
                from agents.fallback import fallback_command
                fallback_response = fallback_command(agent, user_query)
                print("Fallback LLM Output:")
                print(fallback_response)
                return None
        return parsed
    except ValueError as e:
        print("Error extracting JSON or validating params:", e)
        return None
