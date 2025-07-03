# Import FastAPI and pydantic for API and data validation
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import asyncio
# Import enhanced pipeline and MCP configuration
from enhanced_pipeline import EnhancedPipeline
from mcp_config import MCPConfig

# Create FastAPI app
app = FastAPI()
# Initialize pipeline and MCP configuration
pipeline = EnhancedPipeline()
mcp_config = MCPConfig()

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
                print(f"Connected to MCP server: {name}")
            except Exception as e:
                print(f"Failed to connect to {name}: {e}")

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
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to add new MCP server dynamically
@app.post("/mcp/add-server")
async def add_mcp_server(req: MCPServerRequest):
    # Add new MCP server dynamically
    try:
        await pipeline.add_mcp_server(req.name, req.url)
        mcp_config.add_server(req.name, req.url, req.description)
        return {"message": f"MCP server {req.name} added successfully"}
    except Exception as e:
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
