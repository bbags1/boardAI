from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db.session import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String)
    discussion = Column(JSON)  # Stores the full conversation including advisor responses
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    organization_id = Column(Integer, ForeignKey("organizations.id"))

    # Relationships
    organization = relationship("Organization")