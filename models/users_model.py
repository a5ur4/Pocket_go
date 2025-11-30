from sqlalchemy import Column, text
from sqlalchemy.dialects.postgresql import UUID, CITEXT, TIMESTAMP
from database.engine_db import Base

class UsersModel(Base):
    __tablename__ = 'users'
    
    id = Column(UUID, primary_key=True, server_default=text('gen_random_uuid()'))
    phone = Column(CITEXT, nullable=True, unique=True)
    telegram_id = Column(CITEXT, nullable=True, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('NOW()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('NOW()'))