import os
from dotenv import load_dotenv
from fastapi import HTTPException
import httpx 
from sqlalchemy.orm import Session
from models import User, Task
from schemas.schemas import (
    UserCreate, UserResponse, UserUpdate,
    TaskCreate, TaskResponse, TaskUpdate
)


load_dotenv()

