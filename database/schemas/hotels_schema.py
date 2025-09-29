from datetime import datetime
from pydantic import BaseModel, field_validator
from typing import Optional
from geoalchemy2 import WKTElement, WKBElement
from enum import Enum
from uuid import UUID

class HotelsTypeEnum(str, Enum):
    HOTEL = "HOTEL"
    HOSTEL = "HOSTEL"
    POUSADA = "POUSADA"
    APARTAMENTO = "APARTAMENTO"
    RESORT = "RESORT"
    MOTEL = "MOTEL"

class HotelsBase(BaseModel):
    name: str
    description: Optional[str] = None
    type: HotelsTypeEnum
    address: str
    city_id: Optional[UUID] = None
    location: str
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    is_promoted: Optional[bool] = False
    
    @field_validator('location', mode='before')
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
    
class HotelsCreate(HotelsBase):
    pass

class HotelsUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[HotelsTypeEnum] = None
    address: Optional[str] = None
    city_id: Optional[UUID] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    is_promoted: Optional[bool] = None
    
    @field_validator('location', mode='before')
    @classmethod
    def format_location_to_wkt(cls, v: any) -> str:
        if v is None:
            return v
        if isinstance(v, WKBElement):
            # Convert WKBElement to WKT string
            return str(v)
        elif isinstance(v, WKTElement):
            return v.wkt
        elif hasattr(v, 'wkt'):
            return v.wkt
        return str(v)

class HotelsResponse(HotelsBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        
class HotelsNearbyResponse(BaseModel):
    hotel: HotelsResponse
    distance_km: float
    avg_rating: float
    review_count: int

    class Config:
        from_attributes = True