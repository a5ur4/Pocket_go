from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class LogsBase(BaseModel):
    action: str
    entity: str
    entity_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class LogsCreate(LogsBase):
    pass

class LogsUpdate(BaseModel):
    action: Optional[str] = None
    entity: Optional[str] = None
    entity_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class LogsResponse(LogsBase):
    id: str
    timestamp: datetime
    
    class Config:
        from_attributes = True