from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db.session import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    content = Column(Text)
    doc_metadata = Column(JSON)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    organization_id = Column(Integer, ForeignKey("organizations.id"))

    # Relationships
    organization = relationship("Organization", back_populates="documents")