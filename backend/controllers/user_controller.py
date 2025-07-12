import os
from dotenv import load_dotenv
from fastapi import HTTPException, Depends
import httpx 
from sqlalchemy.orm import Session
from models.user import User
from config.db import get_db
from schemas.schemas import (
    UserCreate, UserResponse, UserUpdate,
    TaskCreate, TaskResponse, TaskUpdate
)

load_dotenv()

async def create_user(request: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    try:


        auth0_signup_url = f"https://{os.getenv('AUTH0_DOMAIN')}/dbconnections/signup"
    
        payload = {
            "client_id": os.getenv('AUTH0_CLIENT_ID'),          # ✅ Used here
            "connection": "Username-Password-Authentication",
            "email": request.email,
            "password": request.password,
            "user_metadata": {
                "name": request.name,
                "family_name": request.family_name
            }
        }

        async with httpx.AsyncClient() as client:
            result = await client.post(auth0_signup_url, json=payload)

        if result.status_code == 200:
            # User created in Auth0, now create in your database
            # Mark as superuser if first user
            pass




        # Check if user already exists
        existing_user = db.query(User).filter(
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


async def create_member(request: UserCreate, db: Session = Depends(get_db)) -> UserResponse:

