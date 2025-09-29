from sqlalchemy import Column, text
from sqlalchemy.dialects.postgresql import UUID, CITEXT, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class CitiesModel(Base):
    __tablename__ = 'cities'
    
    id = Column(UUID, primary_key=True, server_default=text('gen_random_uuid()'))
    name = Column(CITEXT, nullable=False, unique=True)
    state = Column(CITEXT, nullable=False)
    country = Column(CITEXT, nullable=False, server_default=text("'Brasil'"))
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('NOW()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('NOW()'))