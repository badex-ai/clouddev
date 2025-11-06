import os
import secrets
from dotenv import load_dotenv
from fastapi import HTTPException, Depends, Request
import httpx 
from sqlalchemy.orm import Session,joinedload,selectinload
from sqlalchemy.exc import IntegrityError,SQLAlchemyError
from models.models import User, Family
from schemas.schemas import (
    UserCreate, UserResponse, UserUpdate, UserRequest,GetMeResponse,
     TaskResponse, TaskUpdate, FamilyResponse, FamilyRequest, FamilyUsers, UserRole
)
import secrets
import string
from config.env import get_config
from utils import utils

import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
import traceback
from utils.utils import send_email, get_management_api_token 

load_dotenv()


config = get_config()

auth0_domain = config["auth0_domain"]
auth0_client_id = config["auth0_client_id"]
auth0_m2m_client_id = config["auth0_m2m_client_id"]
auth0_m2m_client_secret = config["auth0_m2m_client_secret"]  # SECRET







async def send_password_reset_with_auth0(user_id,m2m_token):
    """Let Auth0 send password reset email using their templates"""
    
    # m2m_token = await get_management_api_token()
    ticket_url = f"https://{auth0_domain}/api/v2/tickets/password-change"
    
    payload = {
        "user_id": user_id,
        "ttl_sec": 604800,  # 7 days
        "mark_email_as_verified": True
    }
    
    headers = {
        "Authorization": f"Bearer {m2m_token}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(ticket_url, json=payload, headers=headers)
            response.raise_for_status()


            
        
            print("Password reset email sent by Auth0")
            print(response.json())

            
            return response.json()
            
    except httpx.HTTPStatusError as e:
        print(f"Error creating password reset ticket: {e.response.text}")
        raise



family_member_welcome_email = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; }}
    </style>
</head>
<body>
    <h1>Welcome to Kaban App, {name}! 👋</h1>
    <p>You've been added to a family on <strong>Kaban App</strong> by {admin_name}.</p>
    <p><strong>Next Steps:</strong></p>
    <p><strong>Set Your Password:</strong></p>
    <p>Click the button below to set your password and activate your account:</p>
    
    <p>
        <a href="{password_reset_url}" style="background-color: #4F46E5; color: #FFFFFF; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 20px 0;">Set My Password</a>
    </p>
    
    <p>Or copy and paste this link into your browser:</p>
    <p style="word-break: break-all; color: #4F46E5;">{password_reset_url}</p>
    
    <p><strong>This link will expire in 7 days.</strong></p>
    <hr>
    <p style="color: #666; font-size: 12px;">
        If you didn't expect this invitation, please contact {admin_name}.
    </p>
</body>
</html>
"""



# async def create_family_member(req: UserCreate, db: Session):

#     print('it reach here sha:', req)
#     try:

#          # Check if user already exists
#         existing_user = db.query(User).filter(
#             (User.email == req.email)
#         ).first()
        
#         if existing_user:
#             print('user already exists')
#             raise HTTPException(
#                 status_code=400, 
#                 detail="User with this email or username already exists"
#             )

#         def generate_random_password(length=16):
#                 alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
#                 return ''.join(secrets.choice(alphabet) for i in range(length))
    
#         temporary_password = generate_random_password()
#         m2m_token = await get_management_api_token()
    
#         # Create user via Management API
#         management_api_url = f"https://{auth0_domain}/api/v2/users"
        
#         payload = {
#             "email": req.email,
#             "name": req.name,
#             "family_name": req.family_name,
#             "connection": "Username-Password-Authentication",
#             "password": temporary_password,  
#             "email_verified": False,  
#             "verify_email": False, 
#             "app_metadata": {
#                 "created_by_admin": True,
#                 "setup_required": True
#             }
#         }
        
#         headers = {
#             "Authorization": f"Bearer {m2m_token}",
#             "Content-Type": "application/json"
#         }

      

#         try:

#             async with httpx.AsyncClient(timeout=30.0) as client:
#                 response = await client.post(management_api_url, json=payload, headers=headers)
#                 response.raise_for_status()
                
#                 user_data = response.json()

#                 try:
#                     welcome_email = family_member_welcome_email.format(
#                         name=req.name,
#                         admin_name="Admin"  # Pass the admin's name who invited them
#                     )
#                     await send_email(req, welcome_email)
#                     print(f"Welcome email sent to {req.email}")
#                 except Exception as e:
#                     print(f"Failed to send welcome email: {e}")

#                 await send_password_reset_with_auth0(user_data['user_id'])   
            
#         except httpx.HTTPStatusError as e:
#             raise HTTPException(
#                 status_code=e.response.status_code, 
#                 detail=f"Error creating user in Auth0: {e.response.text}"
#             )

        
#         # Create new user instance
#         new_user = User(
#             username=req.name,
#             email=req.email,
#             name= f"{req.name} {req.family_name}",
#             role=UserRole.member,
#             family_id=req.family_id, 

        
#         )

        
#         # Add to database
#         db.add(new_user)
#         db.commit()
#         db.refresh(new_user)  
#         return UserResponse.model_validate(new_user)


#     except HTTPException as e:
#         logging.error(f"HTTPException: {e.detail}")
#         raise

#     except IntegrityError:
#         db.rollback()
#         raise HTTPException(
#             status_code=400, 
#             detail="User with this email or username already exists"
#         )
#     except Exception as e:
#         print("Error creating user:", str(e))
#         db.rollback()
#         raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

async def create_family_member(req: UserCreate, db: Session) :
    print('Creating family member:', req)
    
    # Variables to track what needs cleanup
    auth0_user_id = None
    db_user_created = False
    
    try:
        # ====== STEP 1: Validation ======
        existing_user = db.query(User).filter(User.email == req.email).first()
        
        if existing_user:
            raise HTTPException(
                status_code=400, 
                detail="User with this email already exists"
            )

        # ====== STEP 2: Create Auth0 User ======
        def generate_random_password(length=16):
            alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
            return ''.join(secrets.choice(alphabet) for i in range(length))
    
        temporary_password = generate_random_password()
        m2m_token = await get_management_api_token()
        management_api_url = f"https://{auth0_domain}/api/v2/users"
        
        payload = {
            "email": req.email,
            "name": req.name,
            "family_name": req.family_name,
            "connection": "Username-Password-Authentication",
            "password": temporary_password,  
            "email_verified": False,  
            "verify_email": False, 
            "app_metadata": {
                "created_by_admin": True,
                "setup_required": True,
                "family_id": req.family_id  # ⭐ Store family_id in Auth0 for reference
            }
        }
        
        headers = {
            "Authorization": f"Bearer {m2m_token}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(management_api_url, json=payload, headers=headers)
                response.raise_for_status()
                user_data = response.json()
                auth0_user_id = user_data['user_id']
                
                print(f"✅ Auth0 user created: {auth0_user_id}")
                
            except httpx.HTTPStatusError as e:
                error_detail = e.response.text if e.response.text else str(e)
                print(f"❌ Auth0 user creation failed: {error_detail}")
                raise HTTPException(
                    status_code=e.response.status_code, 
                    detail=f"Failed to create user in Auth0: {error_detail}"
                )

        # ====== STEP 3: Send Password Reset Email (CRITICAL) ======
        try:
            password_reset_response = await send_password_reset_with_auth0(auth0_user_id,m2m_token)
            print(f"✅ Password reset ticket created: {password_reset_response}")
            ticket_url = password_reset_response.get('ticket')
            
        except Exception as e:
            print(f"❌ Password reset email failed: {e}")
            # ⭐ CRITICAL: If password reset fails, delete Auth0 user
            await rollback_auth0_user(auth0_user_id, m2m_token)
            raise HTTPException(
                status_code=500,
                detail="Failed to send password setup email. User creation cancelled."
            )

        # ====== STEP 4: Send Welcome Email (Optional, non-blocking) ======
        try:
            welcome_email = family_member_welcome_email.format(
                name=req.name,
                admin_name="Admin",
                password_reset_url=ticket_url 
            )
            await send_email(req, welcome_email)
            print(f"✅ Welcome email sent to {req.email}")
        except Exception as e:
            # ⚠️ Welcome email is optional - log but don't fail
            print(f"⚠️ Welcome email failed (non-critical): {e}")

        # ====== STEP 5: Create Database User (ONLY after Auth0 + Email success) ======
        try:
            new_user = User(
                username=req.name,
                email=req.email,
                name=f"{req.name}",
                role=UserRole.member,
                family_id=req.family_id,
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            db_user_created = True
            
            print(f"✅ Database user created: {new_user.public_id}")
            return UserResponse.model_validate(new_user)
            
        except IntegrityError as e:
            db.rollback()

            # ⭐ Extract the full error details
            error_message = str(e.orig) if hasattr(e, 'orig') else str(e)
            error_statement = str(e.statement) if hasattr(e, 'statement') else "No statement"
            error_params = str(e.params) if hasattr(e, 'params') else "No params"
            
            # ⭐ Log everything for debugging
            print(f"🔴 ===== IntegrityError Details =====")
            print(f"🔴 Original error: {error_message}")
            print(f"🔴 SQL statement: {error_statement}")
            print(f"🔴 Parameters: {error_params}")
            print(f"🔴 Full exception: {repr(e)}")
            print(f"🔴 User data attempted:")
            print(f"    - username: {req.name}")
            print(f"    - email: {req.email}")
            print(f"    - family_id: {req.family_id}")
            print(f"🔴 =====================================")
            # ⭐ Database failed - rollback Auth0 user
            await rollback_auth0_user(auth0_user_id, m2m_token)
            raise HTTPException(
                status_code=400, 
                detail="Database constraint violation. User creation rolled back."
            )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        
        # ⭐ Cleanup: Rollback Auth0 if database user wasn't created
        if auth0_user_id and not db_user_created:
            try:
                await rollback_auth0_user(auth0_user_id, m2m_token)
            except Exception as cleanup_error:
                print(f"⚠️ Failed to cleanup Auth0 user: {cleanup_error}")
        
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Error creating user: {str(e)}"
        )


async def rollback_auth0_user(user_id: str, m2m_token: str):
    """Delete Auth0 user if database creation fails"""
    delete_url = f"https://{auth0_domain}/api/v2/users/{user_id}"
    headers = {"Authorization": f"Bearer {m2m_token}"}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.delete(delete_url, headers=headers)
            response.raise_for_status()
            print(f"✅ Rolled back Auth0 user: {user_id}")
        except Exception as e:
            print(f"⚠️ Failed to rollback Auth0 user {user_id}: {e}")
            # Log this for manual cleanup
           

async def get_user(req:UserRequest, db: Session):
    print(req.user_email, 'this is the user sent',)
    
    try:
       # First, get the user
        # print('this is the family member', family_members)
        user = db.query(User).filter(User.email == req.user_email).first()

        if user:
        # Then get all family members including the current user
            family_members = db.query(User).filter(
                User.family_id == user.family_id,
                User.is_active == True
            ).all()

            print('this is the family member', family_members)

            # Get family info
            family = db.query(Family).filter(Family.public_id == user.family_id).first()

            response_data = {
                # User fields directly at root level (only the ones from original structure)
                "id": user.public_id,
                "username": user.username,
                "email": user.email,
                "name": user.name,
                
                # Keep family as nested object for complete family info
                "family": {
                    "id": family.public_id,
                    "name": family.name,
                    "members": [
                        {
                            "id": member.public_id,
                            "name": member.name,
                            "username": member.username,
                            "role": member.role.value
                        }
                        for member in family_members
                    ]
                }
            }

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return response_data

        
    # except Exception as e:
    #      raise HTTPException(status_code=500, detail=f"Error getting user: {str(e)}")
    except Exception as e:
        print("🔴 FULL ERROR TRACEBACK:")
        traceback.print_exc()  # prints the full traceback to console

        raise HTTPException(
            status_code=500,
            detail=f"Error getting user: {str(e)}"
        )
    

   
def deactivate_user(user_id: str, db: Session) -> int:
    """
    Soft delete a user
    """

    try:
        print('e reach here', user_id) 
        result = db.query(User).filter(
            User.public_id == user_id
        ).update({"is_active": False})
        
        db.commit()
        
        # result is an integer (row count)
        if result == 0:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        
        return result  # Returns 1 if successful, 0 if no rows matched
        
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )

# def delete_user(user_id: str, db: Session) -> int:
#     """
#     Soft delete a user
#     """

#     try:
#         print('e reach here', user_id) 
#         result = db.query(User).filter(
#             User.public_id == user_id
#         ).update({"is_active": False})
        
#         db.commit()
        
#         # result is an integer (row count)
#         if result == 0:
#             raise HTTPException(
#                 status_code=404,
#                 detail="User not found"
#             )
        
#         return result  # Returns 1 if successful, 0 if no rows matched
        
#     except SQLAlchemyError as e:
#         db.rollback()
#         raise HTTPException(
#             status_code=500,
#             detail=f"Database error: {str(e)}"
#         )



def reactivate_user(user_id: str, db: Session) -> int:
    """
    Soft delete a user
    """

    try:
        print('e reach here', user_id) 
        result = db.query(User).filter(
            User.public_id == user_id
        ).update({"is_active": True})
        
        db.commit()
        
        # result is an integer (row count)
        if result == 0:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        
        return result  # Returns 1 if successful, 0 if no rows matched
        
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )



