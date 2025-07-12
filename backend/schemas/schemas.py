from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, EmailStr

# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

# Task schemas
class TaskBase(BaseModel):
    title: str
    content: str
    published: bool = False

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    published: Optional[bool] = None

class TaskResponse(TaskBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    author_id: int
    created_at: datetime
    updated_at: datetime
    author: UserResponse




class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    confirm_password: Optional[str] = None

class LogoutRequest(BaseModel):
    token: Optional[str] = None
#