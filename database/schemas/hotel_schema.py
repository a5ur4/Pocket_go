from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from enum import Enum

class HotelTypeEnum(str, Enum):
    HOTEL = "hotel"
    HOSTEL = "hostel"
    POUSADA = "pousada"
    APARTAMENTO = "apartamento"
    RESORT = "resort"
    MOTEL = "motel"

class HotelsBase(BaseModel):
    name: str
    description: Optional[str] = None
    type: HotelTypeEnum
    address: str
    city_id: Optional[str] = None
    location: str  # WKT format for POINT
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    is_promoted: Optional[bool] = False
    
class HotelsCreate(HotelsBase):
    pass

class HotelsUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[HotelTypeEnum] = None
    address: Optional[str] = None
    city_id: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    is_promoted: Optional[bool] = None

class HotelsResponse(HotelsBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True