import os
from dotenv import load_dotenv
from fastapi import HTTPException, Depends
import httpx 
from sqlalchemy.orm import Session
from config.env import get_config
from models.models import User, Family, UserRole
import logging
from utils.utils import send_email


load_dotenv()

config = get_config()

auth0_domain = config["auth0_domain"]
auth0_client_id = config["auth0_client_id"]
auth0_m2m_client_id = config["auth0_m2m_client_id"]
auth0_m2m_client_secret = config["auth0_m2m_client_secret"]
brevo_api_key = config.get("brevo_api_key")  # Get from config


async def logout():
    return {"message": "Logout successful"}


verification_email = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        .button {{
            background-color: #4F46E5;
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 6px;
            display: inline-block;
        }}
    </style>
</head>
<body>
    <h1>Welcome, {name}! 👋</h1>
    <p>Thank you for signing up for <strong>Kaban App</strong>!</p>
    <p>A verification email has been sent to your address through Auth0.</p>
    <p>If you don’t see the email in your inbox, please check your spam or junk folder.</p>
    <hr>
    <p style="color: #666; font-size: 12px;">
        If you didn’t create this account, you can safely ignore this message.
    </p>
</body>
</html>
"""


async def signup(req, db):
    """Handle user signup"""
    
    auth0_signup_url = f"https://{auth0_domain}/dbconnections/signup"

    print("request payloads", req)
    
    # Check if user already exists in your database first
    existing_user = db.query(User).filter(
        (req.email == User.email) | (req.name == User.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=400, 
            detail="User with this email or username already exists"
        )
    
    # Prepare Auth0 signup payload
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

    print('Creating Auth0 user...')
    
    # Create user in Auth0
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(auth0_signup_url, json=payload)
            response.raise_for_status()  # This will raise exception for 4xx/5xx
            
        except httpx.HTTPStatusError as e:
            error_detail = e.response.text if e.response.text else str(e)
            print(f"Auth0 signup failed: {error_detail}")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Signup failed: {error_detail}"
            )
        except Exception as e:
            print(f"Unexpected error during Auth0 signup: {e}")
            raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")
    
    # Auth0 signup successful
    auth0_user = response.json()
    print("Auth0 user created:", auth0_user)
    
    # Create user in database
    try:
        # Create family in your database
        new_family = Family(
            name=req.family_name,
        )
        db.add(new_family)
        db.commit()
        db.refresh(new_family)
        
        # Create user and associate with the new family
        new_user = User(
            username=req.name,
            email=req.email,
            name=req.name,
            family_id=new_family.public_id,  # Use public_id not id
            role=UserRole.admin,  # Correct: lowercase 'admin'
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"User created in database: {new_user.id}")
        
        # Send verification email
       
        try:
            formatted_email = verification_email.format(name=req.name)

            await  send_email(req,formatted_email) 
            print(f"Verification email sent to {req.email}")
        except Exception as e:
            print(f"Failed to send verification email: {e}")
            # Don't fail signup if email fails
        
        return {
            "message": "User created successfully. Please check your email to verify your account.",
            "user_id": new_user.id
        }
        
    except Exception as e:
        db.rollback()
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")


