from sqlalchemy import Column, ForeignKey, Integer, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, CITEXT, TIMESTAMP
from sqlalchemy import text
from database.engine_db import Base
from models.room_types_model import BillingCycleType

class RatePlansModel(Base):
    __tablename__ = 'rate_plans'
    
    id = Column(UUID, primary_key=True, server_default=text('gen_random_uuid()'))
    hotel_id = Column(UUID, ForeignKey('hotels.id', ondelete='CASCADE'), nullable=False)
    name = Column(CITEXT, nullable=False)  # Ex: "Standard Rate", "Non-Refundable"
    billing_cycle = Column(SQLEnum(BillingCycleType, name='billing_cycle_type'), nullable=False)
    duration_minutes = Column(Integer, nullable=False)  # Duration in minutes
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('NOW()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('NOW()'))