from pydantic import BaseModel
from typing import Dict, Any, Optional

class AgentRequest(BaseModel):
    command: str
    params: Dict[str, Any]
    conversation_id: Optional[str] = None
    topic: Optional[str] = None
    context: Optional[str] = ""

class AgentResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    agent: str
    command: str
