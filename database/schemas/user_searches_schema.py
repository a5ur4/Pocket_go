from pydantic import BaseModel, field_validator
from geoalchemy2 import WKTElement, WKBElement
from typing import Optional
from datetime import datetime
from uuid import UUID

class UserSearchesBase(BaseModel):
    user_identifier: Optional[str] = None  # Can be Telegram ID or WhatsApp number
    search_location: str  # WKT format for POINT
    
    @field_validator('search_location', mode='before')
    @classmethod
    def format_location_to_wkt(cls, v: any) -> str:
        if isinstance(v, WKBElement):
            # Convert WKBElement to WKT string
            return str(v)
        elif isinstance(v, WKTElement):
            return v.wkt
        elif hasattr(v, 'wkt'):
            return v.wkt
        return str(v)
    
    class Config:
        from_attributes = True

class UserSearchesCreate(UserSearchesBase):
    pass

class UserSearchesUpdate(BaseModel):
    user_identifier: Optional[str] = None
    search_location: Optional[str] = None
    
    @field_validator('search_location', mode='before')
    @classmethod
    def format_location_to_wkt(cls, v: any) -> str:
        if isinstance(v, WKBElement):
            #z Convert WKBElement to WKT string
            return str(v)
        elif isinstance(v, WKTElement):
            return v.wkt
        elif hasattr(v, 'wkt'):
            return v.wkt
        return str(v)

class UserSearchesResponse(UserSearchesBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True