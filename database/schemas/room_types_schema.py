from pydantic import BaseModel, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime
from enum import Enum

class BillingCycleTypeEnum(str, Enum):
    NIGHTLY = "NIGHTLY"
    HOURLY = "HOURLY"
    FIXED = "FIXED"

class RoomTypesBase(BaseModel):
    hotel_id: UUID
    name: str
    description: Optional[str] = None
    capacity: int
    image_url: Optional[str] = None
    
    @field_validator('capacity')
    @classmethod
    def validate_capacity(cls, v):
        if v <= 0:
            raise ValueError('Capacity must be greater than 0')
        if v > 20:  # Reasonable maximum for a room
            raise ValueError('Capacity cannot exceed 20 guests per room')
        return v
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Room type name cannot be empty')
        return v.strip()
    
    class Config:
        from_attributes = True

class RoomTypesCreate(RoomTypesBase):
    pass

class RoomTypesUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    capacity: Optional[int] = None
    image_url: Optional[str] = None
    
    @field_validator('capacity')
    @classmethod
    def validate_capacity(cls, v):
        if v is not None:
            if v <= 0:
                raise ValueError('Capacity must be greater than 0')
            if v > 20:
                raise ValueError('Capacity cannot exceed 20 guests per room')
        return v
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Room type name cannot be empty')
            return v.strip()
        return v

class RoomTypesResponse(RoomTypesBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

class RoomTypesWithHotelResponse(BaseModel):
    """Extended response that includes hotel information"""
    id: UUID
    hotel_id: UUID
    name: str
    description: Optional[str] = None
    capacity: int
    image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Related hotel data (when joined)
    hotel_name: Optional[str] = None
    hotel_address: Optional[str] = None
    
    class Config:
        from_attributes = True