from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class UserSearchesBase(BaseModel):
    user_identifier: Optional[str] = None  # Can be Telegram ID or WhatsApp number
    search_location: str  # WKT format for POINT

class UserSearchesCreate(UserSearchesBase):
    pass

class UserSearchesUpdate(BaseModel):
    user_identifier: Optional[str] = None
    search_location: Optional[str] = None

class UserSearchesResponse(UserSearchesBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True