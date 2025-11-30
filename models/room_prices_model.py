from enum import Enum
from sqlalchemy import Column, ForeignKey, Boolean, Numeric, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, CITEXT, JSONB, TIMESTAMP
from sqlalchemy import text
from database.engine_db import Base

class RoomPricesModel(Base):
    __tablename__ = 'room_prices'
    
    id = Column(UUID, primary_key=True, server_default=text('gen_random_uuid()'))
    room_type_id = Column(UUID, ForeignKey('room_types.id', ondelete='CASCADE'), nullable=False)
    rate_plan_id = Column(UUID, ForeignKey('rate_plans.id', ondelete='CASCADE'), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)  # Price amount
    currency = Column(CITEXT, nullable=False)  # Ex: "USD", "BRL"
    days_of_week = Column(JSONB, nullable=False, server_default=text("'[0,1,2,3,4,5,6]'::JSONB"))  # Days of the week this price applies (0=Sun, 1=Mon, ..., 6=Sat)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('NOW()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('NOW()'))