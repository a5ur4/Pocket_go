from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class CitiesBase(BaseModel):
    name: str
    state: str
    country: Optional[str] = "Brasil"

class CitiesCreate(CitiesBase):
    pass

class CitiesUpdate(BaseModel):
    name: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None

class CitiesResponse(CitiesBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True