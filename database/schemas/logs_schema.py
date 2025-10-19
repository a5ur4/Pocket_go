from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class LogsBase(BaseModel):
    action: str
    details: Optional[Dict[str, Any]] = None

class LogsCreate(LogsBase):
    pass

class LogsUpdate(BaseModel):
    action: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class LogsResponse(LogsBase):
    id: UUID
    timestamp: datetime
    
    class Config:
        from_attributes = True