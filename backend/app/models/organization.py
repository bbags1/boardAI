from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..db.session import Base

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    subscription_tier = Column(String, default="basic")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    users = relationship("User", back_populates="organization")
    documents = relationship("Document", back_populates="organization")
    # Add this relationship if you have a Personality model
    personalities = relationship("Personality", back_populates="organization", cascade="all, delete-orphan", passive_deletes=True) 