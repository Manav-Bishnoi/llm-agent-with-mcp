# Import FastAPI and pydantic for API and data validation
from fastapi import FastAPI, HTTPException, Request, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional
import sqlite3
import os
from datetime import datetime
import importlib
import requests
from backend.main import main as main_func
import logging
from fastapi.middleware.cors import CORSMiddleware
from backend.core.context_manager import ContextManager
from backend.core.enhanced_pipeline import EnhancedPipeline
from backend.core.prompt_builder import build_prompt_from_registry
from backend.core.tool_registry import load_tool_registry
from backend.utils.llm_utils import query_ollama
from backend.utils.response_utils import parse_and_validate_response
from backend.config.mcp_config import MCPConfig
from backend.utils.mcp_client import MCPClient
import uuid
import json

# Create FastAPI app
app = FastAPI()

# Mount static files for frontend
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# Initialize pipeline and MCP configuration
pipeline = EnhancedPipeline()
mcp_config = MCPConfig()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root route redirects to frontend
@app.get("/")
async def root():
    return RedirectResponse(url="/frontend/")

# Define request schema for /ask endpoint
class EnhancedQueryRequest(BaseModel):
    user_query: str  # The user's question or prompt
    conversation_id: Optional[str] = None  # Optional conversation ID for context
    topic: Optional[str] = None  # Optional topic for the query

# Define request schema for dynamic MCP server management
class MCPServerRequest(BaseModel):
    name: str  # Name of the MCP server
    url: str   # URL of the MCP server
    description: Optional[str] = ""  # Optional description of the MCP server

@app.on_event("startup")
async def startup_event():
    # Initialize MCP servers on startup
    for name, config in mcp_config.servers["servers"].items():
        if config["enabled"]:
            try:
                await pipeline.add_mcp_server(name, config["url"])
                logger.info(f"Connected to MCP server: {name}")
            except Exception as e:
                logger.error(f"Failed to connect to {name}: {e}")

# Endpoint to ask an agent a question using the enhanced pipeline
@app.post("/ask")
async def ask_enhanced(req: EnhancedQueryRequest):
    # Enhanced ask endpoint with context and MCP
    if req.topic:
        pipeline.current_topic = req.topic
    try:
        result = await pipeline.run_enhanced_pipeline(
            req.user_query,
            req.conversation_id
        )
        return {"response": result}
    except Exception as e:
        logger.error(f"Error in /ask endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to add new MCP server dynamically
@app.post("/mcp/add-server")
async def add_mcp_server(req: MCPServerRequest):
    # Add new MCP server dynamically
    try:
        await pipeline.add_mcp_server(req.name, req.url)
        mcp_config.add_server(req.name, req.url, req.description or "")
        logger.info(f"MCP server {req.name} added successfully")
        return {"message": f"MCP server {req.name} added successfully"}
    except Exception as e:
        logger.error(f"Failed to add MCP server {req.name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add server: {e}")

# Endpoint to list all configured MCP servers
@app.get("/mcp/servers")
async def list_mcp_servers():
    # List all configured MCP servers
    return {"servers": mcp_config.servers["servers"]}

# Endpoint to get context for specific topic
@app.get("/context/{topic}")
async def get_context(topic: str):
    # Get context for specific topic
    context = pipeline.context_manager.get_context(topic=topic)
    return {"context": context}

@app.get("/health")
async def health_check():
    """
    Comprehensive health check for all system components
    """
    health_status = {
        "timestamp": datetime.now().isoformat(),
        "overall_status": "healthy",
        "components": {}
    }
    
    # Test Ollama connection
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "gemma3:4b",
                "prompt": "test",
                "stream": False
            },
            timeout=10
        )
        if response.status_code == 200:
            health_status["components"]["ollama"] = {
                "status": "healthy",
                "response_time_ms": response.elapsed.total_seconds() * 1000
            }
        else:
            health_status["components"]["ollama"] = {
                "status": "unhealthy",
                "error": f"HTTP {response.status_code}"
            }
            health_status["overall_status"] = "degraded"
    except Exception as e:
        health_status["components"]["ollama"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["overall_status"] = "degraded"
    
    # Test SQLite database
    try:
        conn = sqlite3.connect("context.db")
        conn.execute("SELECT 1")
        conn.close()
        health_status["components"]["database"] = {
            "status": "healthy",
            "file_exists": os.path.exists("context.db")
        }
    except Exception as e:
        health_status["components"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["overall_status"] = "degraded"
    
    # Test each agent
    agents_to_test = ["healthcare_agent", "fitness_agent", "education_agent", "finance_agent", "law_agent", "travel_agent"]
    
    for agent_name in agents_to_test:
        try:
            # Test basic import
            importlib.import_module(f"agents.{agent_name}")
            health_status["components"][agent_name] = {
                "status": "healthy",
                "module_loaded": True
            }
        except Exception as e:
            health_status["components"][agent_name] = {
                "status": "unhealthy",
                "error": str(e),
                "module_loaded": False
            }
            health_status["overall_status"] = "degraded"
    
    # Test MCP servers if any are configured
    try:
        for name, client in pipeline.mcp_servers.items():
            health_status["components"][f"mcp_{name}"] = {
                "status": "healthy",
                "tools_count": len(client.tools)
            }
    except Exception as e:
        health_status["components"]["mcp_servers"] = {
            "status": "unknown",
            "error": "MCP server check failed"
        }
    
    # Set overall status based on critical components
    critical_components = ["ollama", "database"]
    if any(health_status["components"].get(comp, {}).get("status") == "unhealthy" for comp in critical_components):
        health_status["overall_status"] = "unhealthy"
    
    return health_status

# Endpoint for frontend to call main(user_query)
@app.post("/main_query")
async def main_query(request: Request):
    data = await request.json()
    user_query = data.get("query", "")
    try:
        result = main_func(user_query)
        # Ensure result is JSON serializable
        if not isinstance(result, (dict, list, str, int, float, bool, type(None))):
            result = str(result)
        logger.info(f"/main_query result: {result}")
        return result
    except Exception as e:
        logger.error(f"/main_query error: {e}")
        return {"error": str(e)}

@app.post("/tools/{agent}/run")
async def run_agent_tool(agent: str, request: dict = Body(...)):
    """Run agent tool with proper error handling and agent execution"""
    try:
        command = request.get("command", "")
        params = request.get("params", {})
        conversation_id = request.get("conversation_id") or str(uuid.uuid4())
        topic = request.get("topic") or "general"
        cm = ContextManager()
        # Save user input to context
        cm.save_context(topic=topic, conversation_id=conversation_id, user_input=str(params), response_type="user")
        # Import and run the actual agent
        import importlib
        try:
            agent_module = importlib.import_module(f"agents.{agent}")
            # Check if agent has the required function
            if hasattr(agent_module, command):
                agent_func = getattr(agent_module, command)
                result = agent_func(**params)
                # Save agent response to context
                cm.save_context(topic=topic, conversation_id=conversation_id, agent_response=json.dumps(result), response_type="agent")
                return {"success": True, "data": result, "agent": agent, "command": command}
            elif hasattr(agent_module, "run_command"):
                result = agent_module.run_command(command, params)
                # Save agent response to context
                cm.save_context(topic=topic, conversation_id=conversation_id, agent_response=json.dumps(result), response_type="agent")
                return {"success": True, "data": result, "agent": agent, "command": command}
            else:
                return {"success": False, "error": f"Command '{command}' not found in agent '{agent}'"}
        except ImportError:
            return {"success": False, "error": f"Agent '{agent}' not found"}
        except Exception as e:
            logger.error(f"Agent execution error: {e}")
            return {"success": False, "error": f"Agent execution failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Request processing error: {e}")
        return {"success": False, "error": f"Request processing error: {str(e)}"}
