from sqlalchemy import Column, text, ForeignKey, Numeric, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, TEXT, TIMESTAMP, CITEXT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class EvaluationsModel(Base):
    __tablename__ = "evaluations"
    
    id = Column(UUID, primary_key=True, server_default=text('gen_random_uuid()'))
    hotel_id = Column(UUID, ForeignKey("hotels.id", ondelete='CASCADE'), nullable=False)
    rating = Column(Numeric(2, 1), nullable=False)
    comment = Column(TEXT, nullable=True)
    author_name = Column(CITEXT, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('NOW()'))
    
    __table_args__ = (
        CheckConstraint('rating >= 1.0 AND rating <= 5.0', name='check_rating_range'),
    )