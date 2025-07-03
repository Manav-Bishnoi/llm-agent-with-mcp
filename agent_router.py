from agents.fallback import fallback_command
import importlib
from pydantic import create_model
from fastapi import APIRouter, HTTPException, Request
import requests
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI router for agent endpoints
router = APIRouter()

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
        return {"success": False, "error": "Agent not found", "agent": normalized.get('agent', 'unknown')}
    except Exception as e:
        # Return any other error as string
        return {"success": False, "error": str(e), "agent": normalized.get('agent', 'unknown')}

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

# API endpoint to run agent commands (local or remote)
# This endpoint is called by the main pipeline for all agent actions.
@router.post("/tools/{agent}/run")
async def run_agent_api(agent: str, request: Request):
    try:
        data = await request.json()  # Parse JSON body
        command = data.get("command")  # Get command name
        params = data.get("params", {})  # Get params dict
        
        logger.info(f"Running agent: {agent}, command: {command}")
        
        # Dictionary for remote agent URLs (add remote agents here)
        REMOTE_AGENTS = {
            # 'remote_agent_name': 'http://remote-agent-url/tools/remote_agent_name/run'
        }
        
        if agent in REMOTE_AGENTS:
            # If agent is remote, forward request to remote API
            try:
                logger.info(f"Calling remote agent: {agent}")
                resp = requests.post(
                    REMOTE_AGENTS[agent], 
                    json={"command": command, "params": params}, 
                    timeout=30
                )
                resp.raise_for_status()
                return resp.json()
            except requests.exceptions.ConnectionError:
                logger.error(f"Connection failed to remote agent: {agent}")
                raise HTTPException(status_code=503, detail=f"Remote agent '{agent}' is unavailable")
            except requests.exceptions.Timeout:
                logger.error(f"Timeout calling remote agent: {agent}")
                raise HTTPException(status_code=504, detail=f"Remote agent '{agent}' timed out")
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed to remote agent {agent}: {e}")
                raise HTTPException(status_code=502, detail=f"Remote agent error: {e}")
        
        try:
            # For local agents
            agent_module = importlib.import_module(f"agents.{agent}")
            # Check if agent has run_command entry point
            if hasattr(agent_module, "run_command"):
                # Call run_command with command and params
                result = agent_module.run_command(command, params)
                logger.info(f"Agent {agent} completed successfully")
                return result
            else:
                logger.error(f"Agent {agent} does not support API calls")
                raise HTTPException(status_code=404, detail=f"Agent '{agent}' does not support API calls.")
        except ModuleNotFoundError:
            logger.error(f"Agent module not found: {agent}")
            raise HTTPException(status_code=404, detail=f"Agent '{agent}' not found.")
        except ImportError as e:
            logger.error(f"Import error for agent {agent}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to load agent '{agent}': {e}")
        except Exception as e:
            logger.error(f"Unexpected error in agent {agent}: {e}")
            raise HTTPException(status_code=500, detail=f"Agent error: {e}")
            
    except Exception as e:
        logger.error(f"Request processing error: {e}")
        raise HTTPException(status_code=400, detail=f"Request processing error: {e}")
