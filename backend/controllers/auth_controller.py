import os
from dotenv import load_dotenv
from fastapi import HTTPException,Depends
import httpx 
from sqlalchemy.orm import Session
from config.db import SessionLocal 
from models.models import User,Family


load_dotenv()



async def logout():
    return {"message": "Logout successful"}

async def signup(req):

    db = SessionLocal()
    auth0_signup_url = f"https://{os.getenv('AUTH0_DOMAIN')}/dbconnections/signup"

    print("request payloads",req)
    
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
            family_name=req.family_name,
            role="admin",
            family=new_family  # Associate user with family via relationship
            )

            db.add(new_user)
            db.commit()
            db.refresh(new_user)



            return {"message": "User created successfully", "user_id": new_user.id}
        else:
            print("Auth0 signup failed. Status code:", response.status_code)
            print("Auth0 response content:", response.text)
            raise HTTPException(status_code=400, detail=f"Signup failed: {response.text}")
   



