from pydantic import BaseModel, field_validator
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal

class RoomPricesBase(BaseModel):
    room_type_id: UUID
    rate_plan_id: UUID
    amount: Decimal
    currency: str
    days_of_week: List[int]
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        return v
    
    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v):
        # Common currency codes validation
        valid_currencies = ['USD', 'BRL', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'CNY', 'MXN']
        if v.upper() not in valid_currencies:
            raise ValueError(f'Currency must be one of: {", ".join(valid_currencies)}')
        return v.upper()
    
    @field_validator('days_of_week')
    @classmethod
    def validate_days_of_week(cls, v):
        if not v:
            raise ValueError('At least one day of week must be specified')
        
        for day in v:
            if not isinstance(day, int) or day < 0 or day > 6:
                raise ValueError('Days of week must be integers between 0 (Sunday) and 6 (Saturday)')
        
        # Remove duplicates and sort
        return sorted(list(set(v)))
    
    class Config:
        from_attributes = True

class RoomPricesCreate(RoomPricesBase):
    pass

class RoomPricesUpdate(BaseModel):
    amount: Optional[Decimal] = None
    currency: Optional[str] = None
    days_of_week: Optional[List[int]] = None
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Amount must be greater than 0')
        return v
    
    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v):
        if v is not None:
            valid_currencies = ['USD', 'BRL', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'CNY', 'MXN']
            if v.upper() not in valid_currencies:
                raise ValueError(f'Currency must be one of: {", ".join(valid_currencies)}')
            return v.upper()
        return v
    
    @field_validator('days_of_week')
    @classmethod
    def validate_days_of_week(cls, v):
        if v is not None:
            if not v:
                raise ValueError('At least one day of week must be specified')
            
            for day in v:
                if not isinstance(day, int) or day < 0 or day > 6:
                    raise ValueError('Days of week must be integers between 0 (Sunday) and 6 (Saturday)')
            
            return sorted(list(set(v)))
        return v

class RoomPricesResponse(RoomPricesBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

class RoomPricesWithDetailsResponse(BaseModel):
    """Extended response that includes related room type and rate plan information"""
    id: UUID
    room_type_id: UUID
    rate_plan_id: UUID
    amount: Decimal
    currency: str
    days_of_week: List[int]
    created_at: datetime
    updated_at: datetime
    
    # Related data (when joined)
    room_type_name: Optional[str] = None
    rate_plan_name: Optional[str] = None
    
    class Config:
        from_attributes = True