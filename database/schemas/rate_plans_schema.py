from pydantic import BaseModel, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime
from database.schemas.room_types_schema import BillingCycleTypeEnum

class RatePlansBase(BaseModel):
    hotel_id: UUID
    name: str
    billing_cycle: BillingCycleTypeEnum
    duration_minutes: int
    
    @field_validator('duration_minutes')
    @classmethod
    def validate_duration_minutes(cls, v):
        if v <= 0:
            raise ValueError('Duration must be greater than 0 minutes')
        
        # Validate reasonable duration limits based on billing cycle
        if v > 43200:  # 30 days in minutes
            raise ValueError('Duration cannot exceed 30 days (43,200 minutes)')
            
        return v
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Rate plan name cannot be empty')
        return v.strip()
    
    class Config:
        from_attributes = True

class RatePlansCreate(RatePlansBase):
    pass

class RatePlansUpdate(BaseModel):
    name: Optional[str] = None
    billing_cycle: Optional[BillingCycleTypeEnum] = None
    duration_minutes: Optional[int] = None
    
    @field_validator('duration_minutes')
    @classmethod
    def validate_duration_minutes(cls, v):
        if v is not None:
            if v <= 0:
                raise ValueError('Duration must be greater than 0 minutes')
            if v > 43200:  # 30 days in minutes
                raise ValueError('Duration cannot exceed 30 days (43,200 minutes)')
        return v
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Rate plan name cannot be empty')
            return v.strip()
        return v

class RatePlansResponse(RatePlansBase):
    id: UUID
    created_at: datetime
    updated_at: datetime