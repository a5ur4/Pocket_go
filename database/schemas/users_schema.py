from pydantic import BaseModel, field_validator
from typing import Optional
from uuid import UUID

class UsersBase(BaseModel):
    phone: Optional[str] = None
    telegram_id: Optional[str] = None
    
    class Config:
        from_attributes = True

class UsersCreate(UsersBase):
    pass

class UsersUpdate(BaseModel):
    phone: Optional[str] = None
    telegram_id: Optional[str] = None

class UsersResponse(UsersBase):
    id: UUID
    
    class Config:
        from_attributes = True