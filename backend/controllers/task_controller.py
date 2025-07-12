import os
from dotenv import load_dotenv
from fastapi import HTTPException, Depends
import httpx 
from sqlalchemy.orm import Session
from models.task import Task
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

            (User.email == request.email) | (User.username == request.username)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=400, 
                detail="User with this email or username already exists"
            )
        
        # Hash the password
        hashed_password = hash_password(request.password)
        
        # Create new user instance
        new_user = User(
            username=request.username,
            email=request.email,
            full_name=request.full_name,
            hashed_password=hashed_password,
            role=request.role
            # is_active, created_at, updated_at will use defaults
        )
        
        # Add to database
        db.add(new_user)
        db.commit()
        db.refresh(new_user)  # Refresh to get the ID and timestamps
        
        # Convert to Pydantic model and return
        return UserResponse.from_orm(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, 
            detail="User with this email or username already exists"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")



