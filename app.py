# Import FastAPI and pydantic for API and data validation
from fastapi import FastAPI
from pydantic import BaseModel
# Import main pipeline and agent router
from main import run_agent_full
from agent_router import router as agent_router

# Create FastAPI app
app = FastAPI()

# Define request schema for /ask endpoint
class QueryRequest(BaseModel):
    user_query: str  # The user's question or prompt
    agent: str       # The agent to use (e.g., 'healthcare_agent')
    
# Endpoint to ask an agent a question using the main pipeline
@app.post("/ask")
def ask_agent(req: QueryRequest):
    # Calls the main pipeline, which will route to the agent via API
    result = run_agent_full(req.user_query, req.agent)
    return {"response": result}

# Register agent_router for /tools endpoints (agent API calls)
app.include_router(agent_router)
