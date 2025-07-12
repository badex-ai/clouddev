import os
from dotenv import load_dotenv
from fastapi import HTTPException,Depends
import httpx 
from sqlalchemy.orm import Session
from config.db import get_db
from models.user import User


load_dotenv()

async def login(credentials):
    auth0_token_url = f"https://{os.getenv('AUTH0_DOMAIN')}/oauth/token"
    

    print("i am in the auth login spot")
    
    payload = {
        "grant_type": "password",
        "username": credentials.email,
        "password": credentials.password,
        "client_id": os.getenv('AUTH0_CLIENT_ID'),
        "client_secret": os.getenv('AUTH0_CLIENT_SECRET'),
        "audience": os.getenv('AUTH0_API_AUDIENCE'),
        "scope": "openid profile email"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(auth0_token_url, json=payload)
        
        if response.status_code == 200:
            tokens = response.json()
            return {
                "access_token": tokens["access_token"],
                "id_token": tokens["id_token"],
                "token_type": tokens["token_type"],
                "expires_in": tokens["expires_in"]
            }
        else:
            raise HTTPException(status_code=401, detail="Login failed")
    
    return {"message": "Login successful"}

async def logout():
    return {"message": "Logout successful"}

async def signup(user_data,db: Session = Depends(get_db)):
    auth0_signup_url = f"https://{os.getenv('AUTH0_DOMAIN')}/dbconnections/signup"
    
    payload = {
        "client_id": os.getenv('AUTH0_CLIENT_ID'),
        "connection": "Username-Password-Authentication",
        "email": user_data.email,
        "password": user_data.password,
        "user_metadata": {
            "name": user_data.name,
            "family_name": user_data.family_name
        }
    }

    existing_user = db.query(User).filter(
            (user_data.email == user_data.email) | (user_data.username == user_data.username)
        ).first()
        
    if existing_user:
        raise HTTPException(
            status_code=400, 
            detail="User with this email or username already exists"
        )

    

    async with httpx.AsyncClient() as client:
        response = await client.post(auth0_signup_url, json=payload)
        if response.status_code == 200:
            auth0_user = response.json()
            
            # Create user in your database
            new_user = User(
                username=user_data.username,
                email=user_data.email,
                full_name=user_data.name,
                hashed_password=hashed_password,
                role="admin" if is_first_user() else "user"
            )
        
        
            # Add to database
            db.add(new_user)
            db.commit()
            db.refresh(new_user) 

            
            
            return {"message": "User created successfully", "user_id": db_user.id}
        else:
            raise HTTPException(status_code=400, detail="Signup failed")


     
        
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
