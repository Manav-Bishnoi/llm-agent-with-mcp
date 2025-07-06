from typing import Optional
from pydantic import BaseModel

class APIError(Exception):
    def __init__(self, message: str, code: str, status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    code: str
    details: Optional[dict] = None
