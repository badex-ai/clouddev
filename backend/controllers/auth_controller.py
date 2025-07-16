import os
from dotenv import load_dotenv
from fastapi import HTTPException,Depends
import httpx 
from sqlalchemy.orm import Session
from config.db import SessionLocal 
from models.models import User


load_dotenv()

async def login(req):
    auth0_token_url = f"https://{os.getenv('AUTH0_DOMAIN')}/oauth/token"
    
    

    print("i am in the auth login spot")
    
    payload = {
        "grant_type": "password",
        "username": req.email,
        "password": req.password,
        "client_id": os.getenv('AUTH0_CLIENT_ID'),
        "client_secret": os.getenv('AUTH0_CLIENT_SECRET'),
        "audience": os.getenv('AUTH0_API_AUDIENCE'),
        "scope": "openid profile email"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(auth0_token_url, json=payload)
        except httpx.HTTPStatusError as e:
            print("Error during login:", e)
            raise HTTPException(status_code=401, detail=f"Login failed: {str(e)}")      
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

async def signup(req):

    db = SessionLocal()
    auth0_signup_url = f"https://{os.getenv('AUTH0_DOMAIN')}/dbconnections/signup"

    print("url: auth0_signup_url",auth0_signup_url)
    
    payload = {
        "client_id": os.getenv('AUTH0_CLIENT_ID'),
        "connection": "Username-Password-Authentication",
        "email": req.email,
        "password": req.password,
        "user_metadata": {
            "name": req.name,
            "family_name": req.family_name
        }
    }

    existing_user = db.query(User).filter(
            (req.email == User.email) | (req.name == User.name)
        ).first()
        
    if existing_user:
        raise HTTPException(
            status_code=400, 
            detail="User with this email or username already exists"
        )

    print('here')
    
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(auth0_signup_url, json=payload)
        except httpx.HTTPStatusError as e:
            print("Error during signup:", e)
            raise HTTPException(status_code=400, detail=f"Signup failed: {str(e)}")
        
        if response.status_code == 200:
            auth0_user = response.json()

            print("auth0_user",auth0_user)
            
            # Create user in your database

            
            new_user = User(
                username=req.name,
                email=req.email,
                name=req.name,
                family_name=req.family_name,
                role="admin" 
            )
        
        
            # Add to database
            db.add(new_user)
            db.commit()
            db.refresh(new_user) 



            return {"message": "User created successfully", "user_id": new_user.id}
        else:
            print("Auth0 signup failed. Status code:", response.status_code)
            print("Auth0 response content:", response.text)
            raise HTTPException(status_code=400, detail=f"Signup failed: {response.text}")
   



