from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

class EvaluationsBase(BaseModel):
    hotel_id: UUID
    rating: float = Field(..., ge=1.0, le=5.0, description="Rating must be between 1.0 and 5.0")
    comment: Optional[str] = None
    author_name: Optional[str] = None

class EvaluationsCreate(EvaluationsBase):
    pass

class EvaluationsUpdate(BaseModel):
    rating: Optional[float] = Field(None, ge=1.0, le=5.0, description="Rating must be between 1.0 and 5.0")
    comment: Optional[str] = None
    author_name: Optional[str] = None

class EvaluationsResponse(EvaluationsBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True
