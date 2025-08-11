import os
from dotenv import load_dotenv
from fastapi import HTTPException, Depends, Request
import httpx 
from sqlalchemy.orm import Session,joinedload
from sqlalchemy.exc import IntegrityError
from models.models import User, Family
from config.db import SessionLocal, test_connection
from schemas.schemas import (
    UserCreate, UserResponse, UserUpdate, UserRequest,GetMeResponse,
     TaskResponse, TaskUpdate, FamilyResponse, FamilyRequest, FamilyUsers
)
# Add this to see the actual SQL queries
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

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

# -> UserResponse
async def get_user(req:UserRequest) -> GetMeResponse:
    
    
    print('it reach here too',req)
    
    try:
        user = db.query(User).options(joinedload(User.family).joinedload(Family.users)).filter(User.email == req.user_email).first()
        
        

        print(f"Query successful, user: {user}")
        print(f"User role: {user.role}")
        print(f"User created_at: {user.created_at}")
        print(f"User family: {user.family}")
        
        # Try accessing the family relationship
        if user.family:
            print(f"Family name: {user.family.name}")
            print(f"Family created_at: {user.family.created_at}")

        # Combine the user and family members into a single response


        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        
        return user

        print('it reach here too',db)
        

        
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Error getting user: {str(e)}")
    finally: 
        db.close()

async def get_user_family(req:FamilyRequest)-> FamilyUsers:
    print(f"Family Object: ",req)
    try:
        family = db.query(Family).options(joinedload(Family.users)).filter(Family.id == req.family_id).first()
        
        print(f"User Email: {family.users}")
       
    
        if not family:
            raise HTTPException(status_code=404, detail="family not found")
        
        return FamilyUsers.model_validate(family)
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Error getting family: {str(e)}")
    finally: 
        db.close


async def get_family(req:id)-> FamilyResponse:
    try:
        family = db.query(Family).filter(Family.id == req.id).first()
        
        if not family:
            raise HTTPException(status_code=404, detail="Family not found")
        
        return FamilyResponse.model_validate(family)
    
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Error getting family: {str(e)}")
    finally: 
        db.close



