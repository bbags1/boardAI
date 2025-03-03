from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import json

from ..db.session import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, index=True)
    content = Column(Text, nullable=True)
    doc_metadata = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    organization_id = Column(Integer, ForeignKey("organizations.id"))

    # Relationships
    organization = relationship("Organization", back_populates="documents")

    def __init__(self, **kwargs):
        # Convert dict to JSON string for doc_metadata if it's a dict
        if "doc_metadata" in kwargs and isinstance(kwargs["doc_metadata"], dict):
            kwargs["doc_metadata"] = json.dumps(kwargs["doc_metadata"])
        super().__init__(**kwargs)

    @property
    def doc_metadata_dict(self):
        """Return doc_metadata as a dictionary"""
        if not self.doc_metadata:
            return {}
        
        if isinstance(self.doc_metadata, dict):
            return self.doc_metadata
        
        try:
            return json.loads(self.doc_metadata)
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @property
    def path(self):
        """Return the full path to this document"""
        if not self.parent_id:
            return "/"
        
        # Get parent path recursively
        parent_path = self.parent.path if self.parent else "/"
        
        # Get document name from metadata
        metadata = self.doc_metadata_dict
        name = metadata.get("name", f"document_{self.id}")
        
        # Combine paths
        if parent_path.endswith("/"):
            return f"{parent_path}{name}"
        else:
            return f"{parent_path}/{name}"