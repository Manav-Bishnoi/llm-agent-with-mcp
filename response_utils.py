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
                
                # Try to fix missing parameters by providing defaults
                if "Missing parameters" in str(e):
                    print("Attempting to fix missing parameters...")
                    params = parsed.get("params", {})
                    for param in required:
                        if param not in params:
                            if param == "symptom":
                                params[param] = user_query
                            elif param == "goal":
                                params[param] = user_query
                            elif param == "query":
                                params[param] = user_query
                            elif param == "destination":
                                params[param] = user_query
                            elif param == "topic":
                                params[param] = user_query
                            else:
                                params[param] = user_query
                    parsed["params"] = params
                    print(f"Fixed parameters: {params}")
                    return parsed
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
        # Provide a simple fallback when LLM fails
        print("LLM failed to provide valid JSON. Using simple fallback...")
        # Try to determine the best agent based on keywords
        user_query_lower = user_query.lower()
        if any(word in user_query_lower for word in ['health', 'sick', 'pain', 'doctor', 'medicine']):
            return {"agent": "healthcare_agent", "command": "suggest_advice", "params": {"symptom": user_query}}
        elif any(word in user_query_lower for word in ['exercise', 'workout', 'fitness', 'gym']):
            return {"agent": "fitness_agent", "command": "suggest_plan", "params": {"goal": user_query}}
        elif any(word in user_query_lower for word in ['money', 'finance', 'investment', 'budget']):
            return {"agent": "finance_agent", "command": "suggest_plan", "params": {"query": user_query}}
        elif any(word in user_query_lower for word in ['travel', 'trip', 'vacation', 'hotel']):
            return {"agent": "travel_agent", "command": "suggest_itinerary", "params": {"destination": user_query}}
        elif any(word in user_query_lower for word in ['learn', 'study', 'education', 'course']):
            return {"agent": "education_agent", "command": "suggest_plan", "params": {"topic": user_query}}
        elif any(word in user_query_lower for word in ['law', 'legal', 'contract', 'rights']):
            return {"agent": "law_agent", "command": "suggest_advice", "params": {"query": user_query}}
        else:
            # Default to healthcare agent for general queries
            return {"agent": "healthcare_agent", "command": "suggest_advice", "params": {"symptom": user_query}}
