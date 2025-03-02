from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db.session import Base
import json

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
    
    def __init__(self, **kwargs):
        if 'doc_metadata' in kwargs and isinstance(kwargs['doc_metadata'], dict):
            kwargs['doc_metadata'] = json.dumps(kwargs['doc_metadata'])
        super().__init__(**kwargs)
        
    @property
    def doc_metadata_dict(self):
        """Return doc_metadata as a dictionary"""
        if isinstance(self.doc_metadata, str):
            try:
                return json.loads(self.doc_metadata)
            except:
                return {}
        return self.doc_metadata or {}