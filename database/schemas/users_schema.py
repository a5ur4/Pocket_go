from pydantic import BaseModel, field_validator
from geoalchemy2 import WKTElement, WKBElement
from typing import Optional
from uuid import UUID

class UsersBase(BaseModel):
    phone: Optional[str] = None
    telegram_id: Optional[str] = None
    first_location: str # WKT format for POINT
    
    @field_validator('first_location', mode='before')
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

class UsersCreate(UsersBase):
    pass

class UsersUpdate(BaseModel):
    phone: Optional[str] = None
    telegram_id: Optional[str] = None
    first_location: Optional[str] = None
    
    @field_validator('first_location', mode='before')
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

class UsersResponse(UsersBase):
    id: UUID
    
    class Config:
        from_attributes = True