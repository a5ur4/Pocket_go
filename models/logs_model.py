from sqlalchemy import Column, text
from sqlalchemy.dialects.postgresql import UUID, CITEXT, TIMESTAMP, JSONB
from database.engine_db import Base

class LogsModel(Base):
    __tablename__ = 'logs'
    
    id = Column(UUID, primary_key=True, server_default=text('gen_random_uuid()'))
    action = Column(CITEXT, nullable=False)
    entity = Column(CITEXT, nullable=False)
    entity_id = Column(UUID, nullable=True)
    details = Column(JSONB, nullable=True)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('NOW()'))