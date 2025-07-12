import os
from dotenv import load_dotenv
from fastapi import HTTPException
import httpx 
from sqlalchemy.orm import Session
from config.db import get_db

load_dotenv()

async def login(credentials):
    auth0_token_url = f"https://{os.getenv('AUTH0_DOMAIN')}/oauth/token"
    
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

async def signup(user_data):
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

    async with httpx.AsyncClient() as client:
        response = await client.post(auth0_signup_url, json=payload)
        if response.status_code == 200:
            auth0_user = response.json()
            
            # Create user in your database
            db_user = await create_user_in_db({
                "auth0_id": auth0_user["_id"],
                "email": user_data.email,
                "name": user_data.name,
                "family_name": user_data.family_name,
                "role": "admin" if is_first_user() else "user"
            })

            
            
            return {"message": "User created successfully", "user_id": db_user.id}
        else:
            raise HTTPException(status_code=400, detail="Signup failed")

