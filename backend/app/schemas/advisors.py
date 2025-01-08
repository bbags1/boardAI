from pydantic import BaseModel
from typing import List, Optional, Dict
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

class DocumentCreate(BaseModel):
    type: str
    content: str
    doc_metadata: Optional[Dict] = None

class DocumentResponse(BaseModel):
    id: int
    type: str
    content: str
    doc_metadata: Dict
    timestamp: datetime
    organization_id: int

    class Config:
        from_attributes = True

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