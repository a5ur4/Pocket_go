from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class HotelDetailsBase(BaseModel):
    hotel_id: UUID
    animals_allowed: Optional[bool] = None
    wifi_available: Optional[bool] = None
    breakfast_included: Optional[bool] = None
    gym_available: Optional[bool] = None
    parking_available: Optional[bool] = None

    class Config:
        from_attributes = True

class HotelDetailsCreate(HotelDetailsBase):
    pass

class HotelDetailsUpdate(BaseModel):
    animals_allowed: Optional[bool] = None
    wifi_available: Optional[bool] = None
    breakfast_included: Optional[bool] = None
    gym_available: Optional[bool] = None
    parking_available: Optional[bool] = None

class HotelDetailsResponse(HotelDetailsBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True