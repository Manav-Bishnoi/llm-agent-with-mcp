from agents.fallback import fallback_command, fallback_agent_execution
import importlib  # Used for dynamic import of agent modules by name
from pydantic import create_model  # Used for dynamic parameter validation
from fastapi import APIRouter, HTTPException, Request  # FastAPI components for API routing and error handling
import requests  # Used for making HTTP requests to remote agents
import logging
from context_manager import ContextManager
import traceback

# Create FastAPI router for agent endpoints
router = APIRouter()
logger = logging.getLogger("agent_router")

class AgentExecutionError(Exception):
    pass
class AgentTimeoutError(Exception):
    pass

# This function normalizes the agent call structure from LLM or user input.
# It ensures the result is a dict with 'agent', 'command', and 'params' keys.
# If the input is not in this format, it tries to extract the agent name and params,
# and infers the command from the registry or uses a fallback.
def normalize_agent_call(parsed, registry=None):
    # If the parsed result is wrapped in a 'response' key, unwrap it
    if 'response' in parsed:
        parsed = parsed['response']
    # If already in the correct format, return as is
    if all(k in parsed for k in ('agent', 'command', 'params')):
        return parsed
    # If only one key (agent name), try to extract command and params
    elif len(parsed) == 1:
        agent_name = list(parsed.keys())[0]  # Get agent name
        agent_data = parsed[agent_name]  # Get agent data (params or nested response)
        # If agent_data is a dict with 'response', use that as params
        params = agent_data['response'] if isinstance(agent_data, dict) and 'response' in agent_data else agent_data
        command = None
        # If registry is provided and agent is in registry, try to infer command
        if registry and agent_name in registry:
            funcs = list(registry[agent_name]["functions"].keys())  # List of possible commands
            if len(funcs) == 1:
                command = funcs[0]  # Only one command, use it
                meta = registry[agent_name]["functions"][command]
            else:
                # Try to match command by number of params
                for func, meta in registry[agent_name]["functions"].items():
                    if isinstance(params, dict) and len(meta['params']) == len(params):
                        command = func
                        break
                if not command:
                    command = funcs[0]  # Default to first command
                    meta = registry[agent_name]["functions"][command]
            # Fill in missing parameters with 'no value' if needed
            if isinstance(params, dict):
                param_names = meta['params'] if 'params' in meta else []
                for pname in param_names:
                    if pname not in params:
                        params[pname] = 'no value'
        else:
            # If agent not in registry, use fallback command
            command = fallback_command(agent_name)
        # Return normalized structure
        return {
            'agent': agent_name,
            'command': command,
            'params': params
        }
    else:
        # If cannot normalize, raise error
        raise ValueError('Could not normalize agent call from LLM output')

# This function runs the specified agent command with given params.
# It dynamically imports the agent module and calls the function by name.
def run_agent(normalized, registry=None):
    try:
        # Optionally validate params using registry
        if registry is not None:
            validate_params(normalized, registry)
        # Dynamically import agent module (e.g., agents.healthcare_agent)
        agent_module = importlib.import_module(f"agents.{normalized['agent']}")
        # Get the function to call (e.g., suggest_advice)
        agent_func = getattr(agent_module, normalized["command"])
        # Call the function with params and return result
        return agent_func(**normalized["params"])
    except ModuleNotFoundError:
        # If agent module not found, return error
        return {"result": "no agent"}
    except Exception as e:
        # Return any other error as string
        return {"error": str(e)}

# This function validates parameters for agent commands using pydantic.
# It dynamically builds a schema from the registry and checks the params.
def validate_params(parsed, registry):
    agent = registry[parsed["agent"]]  # Get agent info from registry
    func = agent["functions"][parsed["command"]]  # Get function info
    # Build param definitions for pydantic
    param_defs = {
        key: (eval(spec["type"]), ...)
        for key, spec in func["params"].items()
    }
    Schema = create_model("Params", **param_defs)  # Create pydantic model
    Schema(**parsed["params"])  # Validate params

# This function executes the agent with context, handling errors and fallback logic.
def run_agent_with_context(normalized, context_manager, conversation_id=None, topic=None):
    try:
        context = context_manager.get_filtered_context(
            topic=topic,
            conversation_id=conversation_id,
            exclude_main_model=True
        )
        agent_module = importlib.import_module(f"agents.{normalized['agent']}")
        if hasattr(agent_module, "run_command_with_context"):
            return agent_module.run_command_with_context(
                normalized["command"],
                normalized["params"],
                context
            )
        else:
            agent_func = getattr(agent_module, normalized["command"])
            return agent_func(**normalized["params"])
    except Exception as e:
        return {"success": False, "error": str(e), "agent": normalized.get('agent', 'unknown')}

# This function runs the agent with error handling and fallback to ensure robustness.
def run_agent_with_error_handling(normalized, context_manager, conversation_id=None, topic=None):
    agent_name = normalized.get('agent', 'unknown')
    command = normalized.get('command', 'unknown')
    try:
        context = context_manager.get_filtered_context(
            topic=topic,
            conversation_id=conversation_id,
            exclude_main_model=True
        )
        try:
            agent_module = importlib.import_module(f"agents.{agent_name}")
        except ModuleNotFoundError:
            logger.error(f"Agent module not found: {agent_name}")
            return fallback_agent_execution(
                agent_name, command, normalized.get('params', {}),
                context_manager.get_last_user_query(), context
            )
        try:
            if hasattr(agent_module, "run_command_with_context"):
                result = agent_module.run_command_with_context(
                    command,
                    normalized["params"],
                    context
                )
            else:
                result = agent_module.run_command(command, normalized["params"])
            if not isinstance(result, dict):
                raise AgentExecutionError(f"Agent returned invalid result type: {type(result)}")
            if not result.get('success', False):
                logger.warning(f"Agent {agent_name} reported failure: {result.get('error', 'Unknown error')}")
                return fallback_agent_execution(
                    agent_name, command, normalized.get('params', {}),
                    context_manager.get_last_user_query(), context
                )
            return result
        except Exception as e:
            logger.error(f"Agent execution error for {agent_name}: {str(e)}")
            logger.error(traceback.format_exc())
            return fallback_agent_execution(
                agent_name, command, normalized.get('params', {}),
                context_manager.get_last_user_query(), context
            )
    except Exception as e:
        logger.error(f"Critical error in agent execution: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": f"Critical system error: {str(e)}",
            "agent": agent_name,
            "command": command,
            "fallback_attempted": True
        }

# API endpoint to run agent commands (local or remote)
# This endpoint is called by the main pipeline for all agent actions.
@router.post("/tools/{agent}/run")
async def run_agent_api(agent: str, request: Request):
    try:
        data = await request.json()  # Parse JSON body
        command = data.get("command")  # Get command name
        params = data.get("params", {})  # Get params dict
        conversation_id = data.get("conversation_id")  # Get conversation ID
        topic = data.get("topic")  # Get topic
        context = data.get("context", "")  # Get context
        context_manager = ContextManager()  # Initialize context manager
        try:
            agent_module = importlib.import_module(f"agents.{agent}")
            if hasattr(agent_module, "run_command_with_context"):
                # If agent supports context, run with context
                result = agent_module.run_command_with_context(command, params, context)
            else:
                # Otherwise, run normal command
                result = agent_module.run_command(command, params)
            logger.info(f"Agent {agent} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Agent execution error: {e}")
            raise HTTPException(status_code=500, detail=f"Agent error: {e}")
    except Exception as e:
        logger.error(f"Request processing error: {e}")
        raise HTTPException(status_code=400, detail=f"Request processing error: {e}")
