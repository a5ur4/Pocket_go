from enum import Enum
from sqlalchemy import Column, ForeignKey, Integer, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, CITEXT, TEXT, TIMESTAMP
from sqlalchemy import text
from database.engine_db import Base

class BillingCycleType(Enum):
    NIGHTLY = "NIGHTLY"  # For Hotels
    HOURLY = "HOURLY"    # For Motels
    FIXED = "FIXED"      # For Motels

class RoomTypesModel(Base):
    __tablename__ = 'room_types'
    
    id = Column(UUID, primary_key=True, server_default=text('gen_random_uuid()'))
    hotel_id = Column(UUID, ForeignKey('hotels.id', ondelete='CASCADE'), nullable=False)
    name = Column(CITEXT, nullable=False)
    description = Column(TEXT, nullable=True)
    capacity = Column(Integer, nullable=False)  # Number of guests
    image_url = Column(CITEXT, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('NOW()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('NOW()'))