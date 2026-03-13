from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email: str
    name: str
    roles: List[str]
    created_at: datetime


class UserUpdate(BaseModel):
    name: Optional[str] = None


class AssignRoleRequest(BaseModel):
    user_id: int
    role: str
