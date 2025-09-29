from sqlalchemy import Column, text
from sqlalchemy.dialects.postgresql import UUID, CITEXT, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geography

Base = declarative_base()

class UserSearchesModel(Base):
    __tablename__ = 'user_searches'

    id = Column(UUID, primary_key=True, server_default=text('gen_random_uuid()'))
    user_identifier = Column(CITEXT, nullable=True)  # Can be Telegram ID or WhatsApp number
    search_location = Column(Geography('POINT', srid=4326), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('NOW()'))