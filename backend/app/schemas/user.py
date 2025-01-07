from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class OrganizationBase(BaseModel):
    name: str
    subscription_tier: str = "basic"

class OrganizationCreate(OrganizationBase):
    pass

class Organization(OrganizationBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    password: str
    organization_name: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class User(UserBase):
    id: int
    organization_id: int
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None