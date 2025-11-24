from sqlalchemy import Column, text, Boolean
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from database.engine_db import Base

class HotelDetailsModel(Base):
    __tablename__ = 'hotel_details'
    
    id = Column(UUID, primary_key=True, server_default=text('gen_random_uuid()'))
    hotel_id = Column(UUID, nullable=False, unique=True)
    animals_allowed = Column(Boolean, nullable=False, server_default=text('FALSE'))
    wifi_available = Column(Boolean, nullable=False, server_default=text('FALSE'))
    breakfast_included = Column(Boolean, nullable=False, server_default=text('FALSE'))
    gym_available = Column(Boolean, nullable=False, server_default=text('FALSE'))
    parking_available = Column(Boolean, nullable=False, server_default=text('FALSE'))
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('NOW()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('NOW()'))