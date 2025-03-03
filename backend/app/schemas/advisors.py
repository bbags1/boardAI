from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

class ConversationCreate(BaseModel):
    topic: str
    advisor_roles: List[str]

class ConversationResponse(BaseModel):
    id: int
    topic: str
    discussion: Dict
    timestamp: datetime
    organization_id: int

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str
    organization_name: str

class UserResponse(UserBase):
    id: int
    organization_id: int

    class Config:
        from_attributes = True

class DocumentBase(BaseModel):
    type: str
    content: Optional[str] = None
    doc_metadata: Optional[Dict[str, Any]] = None

class DocumentCreate(DocumentBase):
    pass

class DocumentResponse(DocumentBase):
    id: int
    timestamp: datetime
    organization_id: int
    
    class Config:
        from_attributes = True
        
        @classmethod
        def from_orm(cls, obj):
            # Ensure doc_metadata is treated as a dictionary
            if hasattr(obj, 'doc_metadata_dict'):
                obj.doc_metadata = obj.doc_metadata_dict
            return super().from_orm(obj)

class FolderCreate(BaseModel):
    name: str
    parent_id: Optional[int] = None

class PersonalityBase(BaseModel):
    name: str
    description: str
    prompt_template: str

class PersonalityCreate(PersonalityBase):
    pass

class PersonalityResponse(PersonalityBase):
    id: int
    organization_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class AdvisorQuery(BaseModel):
    query: str
    advisor_roles: List[str] = Field(default_factory=list)

class AdvisorResponse(BaseModel):
    response: str