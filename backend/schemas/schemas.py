from datetime import datetime, date
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

class UserRequest(BaseModel):
    user_email: str
    

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None

class FamilyResponse(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)
    

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime
    family: Optional[FamilyResponse] 

# Task schemas
class TaskBase(BaseModel):
    title: str
    content: str
    published: bool = False

class TaskCreate(TaskBase):
    pass
class DeleteTask(TaskBase):
    task_id: str
class GetTasks(BaseModel):
    family_id: int
    date: date
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    published: Optional[bool] = None

class TaskResponse(TaskBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    creator_id: int  
    created_at: datetime
    updated_at: datetime
    creator: UserResponse  




class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    family_name: str

class EmailVerificationRequest(BaseModel):
    user_id: str
    

class ChecklistItem(BaseModel):
    id: str
    title: str
    completed: bool = False

    
class TaskRequest(BaseModel):
    id: str