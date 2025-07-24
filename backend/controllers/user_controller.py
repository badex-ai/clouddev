import os
from dotenv import load_dotenv
from fastapi import HTTPException, Depends, Request
import httpx 
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.models import User
from config.db import SessionLocal 
from schemas.schemas import (
    UserCreate, UserResponse, UserUpdate, UserRequest,
    TaskCreate, TaskResponse, TaskUpdate
)

load_dotenv()
db = SessionLocal()

async def get_management_api_token():
    auth0_token_url = f"https://{os.getenv('AUTH0_DOMAIN')}/oauth/token"
    
    payload = {
        "client_id": os.getenv('AUTH0_M2M_CLIENT_ID'),       
        "client_secret": os.getenv('AUTH0_M2M_CLIENT_SECRET'),
        "audience": f"https://{os.getenv('AUTH0_DOMAIN')}/api/v2/",
        "grant_type": "client_credentials"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(auth0_token_url, json=payload)
        return response.json()["access_token"]


async def create_user(request: UserCreate) -> UserResponse:
    try:

        m2m_token = await get_management_api_token()
    
        # Create user via Management API
        management_api_url = f"https://{os.getenv('AUTH0_DOMAIN')}/api/v2/users"
        
        payload = {
            "email": request.email,
            "name": request.name,
            "family_name": request.family_name,
            "connection": "Username-Password-Authentication",
            "email_verified": False,
            "verify_email": True  # This sends the email invitation
        }
        
        headers = {
            "Authorization": f"Bearer {m2m_token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(management_api_url, json=payload, headers=headers)
            
            if response.status_code == 201:
                # User created in Auth0, now create in your database
                # User will receive email to set password
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
        # hashed_password = hash_password(request.password)
        
        # Create new user instance
        new_user = User(
            username=request.username,
            email=request.email,
            full_name=request.full_name,
            # hashed_password=hashed_password,
            role=request.role
            # is_active, created_at, updated_at will use defaults
        )
        
        # Add to database
        db.add(new_user)
        db.commit()
        db.refresh(new_user)  # Refresh to get the ID and timestamps
        # Convert to Pydantic model and return
        return UserResponse.model_validate(new_user)
       
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, 
            detail="User with this email or username already exists"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")
    finally:
        db.close()

async def get_user(req:UserRequest) -> UserResponse:
    
    print('request', req)
    # email = await req.json()
    try:
        user = db.query(User).filter(User.email == req.user_email).first()
    
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse.model_validate(user)
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Error getting user: {str(e)}")
    finally: 
        db.close




