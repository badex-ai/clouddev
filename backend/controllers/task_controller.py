import os
from dotenv import load_dotenv
from fastapi import HTTPException, Depends
import httpx 
from sqlalchemy.orm import Session
from backend.models.models import Task
from config.db import get_db
from schemas.schemas import (
    UserCreate, UserResponse, UserUpdate,
    TaskCreate, TaskResponse, TaskUpdate
)

load_dotenv()

async def create_task(request: TaskCreate, db: Session = Depends(get_db)) -> TaskResponse:
    try:
        new_task = Task(
            title=request.title,
            description=request.description,
            owner_id=request.owner_id
        )
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        return TaskResponse.from_orm(new_task)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating task: {str(e)}")






