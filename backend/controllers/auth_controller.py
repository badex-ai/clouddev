import os
from dotenv import load_dotenv
from fastapi import HTTPException,Depends
import httpx 
from sqlalchemy.orm import Session
from config.env import get_config
from models.models import User,Family,UserRole
import logging


load_dotenv()


config = get_config()

auth0_domain = config["auth0_domain"]
auth0_client_id = config["auth0_client_id"]
auth0_m2m_client_id = config["auth0_m2m_client_id"]
auth0_m2m_client_secret = config["auth0_m2m_client_secret"]  # SECRET


async def logout():
    return {"message": "Logout successful"}

async def signup(req, db):

    auth0_signup_url = f"https://{auth0_domain}/dbconnections/signup"

    print("request payloads",req)
    
    payload = {
        "client_id": auth0_client_id,
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

            print("auth0_user", auth0_user)
            
            # Create family in your database
            new_family = Family(
            name=req.family_name,
            )
            db.add(new_family)
            db.commit()
            db.refresh(new_family)  # Refresh to get the new_family.id

            # Create user and associate with the new family
            new_user = User(
            username=req.name,
            email=req.email,
            name=req.name,
            family_id=new_family.id,
            role=UserRole.ADMIN,
           
            )

            db.add(new_user)
            db.commit()
            db.refresh(new_user)



            return {"message": "User created successfully", "user_id": new_user.id}
        else:
            print("Auth0 signup failed. Status code:", response.status_code)
            print("Auth0 response content:", response.text)
            raise HTTPException(status_code=400, detail=f"Signup failed: {response.text}")

async def get_management_api_token():
    token_url = f"https://{auth0_domain}/oauth/token"
    token_payload = {
        "client_id": auth0_m2m_client_id,
        "client_secret": auth0_m2m_client_secret,
        "audience": f"https://{auth0_domain}/api/v2/",
        "grant_type": "client_credentials"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, json=token_payload)
        response.raise_for_status()
        return response.json()["access_token"]



async def sendVerificationEmail(req):
    """Send verification email to the user"""


    auth0_verification_url = f"https://{auth0_domain}/api/v2/jobs/verification-email"

    payload = {
        "client_id": auth0_client_id, 
        # "connection": "Username-Password-Authentication",
        "user_id": req.user_id,
        
    }

    

    print("the email verified", req)

    management_token = await get_management_api_token()

    print("Management API token:", management_token)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {management_token}"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(auth0_verification_url, json=payload,headers=headers)
        except httpx.HTTPStatusError as e:
            print("Error during signup:", e)
            raise HTTPException(status_code=400, detail=f"Verification email failed: {str(e)}")


    
    print("Response status code:", response.status_code)
    print("Response content:", response.text)

    return {"message": "Verification email sent successfully"}


