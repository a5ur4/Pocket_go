from enum import Enum
from sqlalchemy import Column, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, CITEXT, TEXT, TIMESTAMPTZ
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import text
from geoalchemy2 import Geography

Base = declarative_base()

class HotelType(Enum):
    HOTEL = "hotel"
    HOSTEL = "hostel"
    POUSADA = "pousada"
    RESORT = "resort"
    APARTAMENTO = "apartamento"
    MOTEL = "motel"

class HotelsModel(Base):
    __tablename__ = 'hotels'
    
    id = Column(UUID, primary_key=True, server_default=text('gen_random_uuid()'))
    name = Column(CITEXT, nullable=False)
    description = Column(TEXT, nullable=True)
    type = Column(SQLEnum(HotelType, name='hotel_type'), nullable=False)
    address = Column(CITEXT, nullable=False)
    city_id = Column(UUID, ForeignKey('cities.id', ondelete='SET NULL'), nullable=True)
    location = Column(Geography('POINT', srid=4326), nullable=False)
    phone = Column(CITEXT, nullable=True)
    email = Column(CITEXT, nullable=True)
    website = Column(CITEXT, nullable=True)
    is_promoted = Column(Boolean, nullable=False, server_default=text('FALSE'))
    created_at = Column(TIMESTAMPTZ, nullable=False, server_default=text('NOW()'))
    updated_at = Column(TIMESTAMPTZ, nullable=False, server_default=text('NOW()'))