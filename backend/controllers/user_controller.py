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

# Add this to see the actual SQL queries
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

load_dotenv()




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



async def send_password_reset_with_auth0(user_id):
    """Let Auth0 send password reset email using their templates"""
    
    m2m_token = await get_management_api_token()
    ticket_url = f"https://{os.getenv('AUTH0_DOMAIN')}/api/v2/tickets/password-change"
    
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


            
            # Auth0 automatically sends the password reset email
            # No need to send it yourself
            print("Password reset email sent by Auth0")
            print(response.json())

            
            return response.json()
            
    except httpx.HTTPStatusError as e:
        print(f"Error creating password reset ticket: {e.response.text}")
        raise

# async def create_password_setup_ticket(user_id, email, name):
#     """Create password change ticket for new user setup"""
#     m2m_token = await get_management_api_token()
#     ticket_url = f"https://{os.getenv('AUTH0_DOMAIN')}/api/v2/tickets/password-change"
    
#     payload = {
#         "user_id": user_id,
#         "result_url": f"{os.getenv('FRONTEND_URL')}/welcome?setup=complete",
#         "ttl_sec": 604800,  # 7 days
#         "mark_email_as_verified": True,  # Verify email when password is set
#         "includeEmailInRedirect": False
#     }
    
#     headers = {
#         "Authorization": f"Bearer {m2m_token}",
#         "Content-Type": "application/json"
#     }
    
#     try:
#         async with httpx.AsyncClient(timeout=30.0) as client:
#             response = await client.post(ticket_url, json=payload, headers=headers)
#             response.raise_for_status()
            
#             ticket_data = response.json()
            
#             # Send welcome email with setup link
#             await send_setup_email(email, name, ticket_data['ticket'])
            
#             return ticket_data
            
#     except httpx.HTTPStatusError as e:
#         print(f"Error creating password setup ticket: {e.response.text}")
#         raise



# async def send_setup_email(email, name, setup_url):
#     """Send account setup email to new family member"""
    
#     # Replace this with your actual email service
#     # Examples: SendGrid, AWS SES, Mailgun, etc.
    
#     email_subject = "Complete Your Family Account Setup"
#     email_body = f"""
#     Hi {name},
    
#     Welcome to our family platform! An account has been created for you by your family admin.
    
#     To complete your account setup:
#     1. Click this link: {setup_url}
#     2. Create your password
#     3. Your email will be automatically verified
    
#     This link expires in 7 days. If you need a new link, please contact your family admin.
    
#     Best regards,
#     The Family Platform Team
#     """
    
#     # Example implementations:
    
#     # Option 1: Print for testing
#     print(f"TO: {email}")
#     print(f"SUBJECT: {email_subject}")
#     print(f"BODY: {email_body}")
    
#     # Option 2: SendGrid example
#     # import sendgrid
#     # from sendgrid.helpers.mail import Mail
#     # 
#     # sg = sendgrid.SendGridAPIClient(api_key=os.getenv('SENDGRID_API_KEY'))
#     # message = Mail(
#     #     from_email='noreply@yourfamilyapp.com',
#     #     to_emails=email,
#     #     subject=email_subject,
#     #     plain_text_content=email_body
#     # )
#     # response = sg.send(message)
    
#     # Option 3: AWS SES example
#     # import boto3
#     # 
#     # ses = boto3.client('ses', region_name='us-east-1')
#     # ses.send_email(
#     #     Source='noreply@yourfamilyapp.com',
#     #     Destination={'ToAddresses': [email]},
#     #     Message={
#     #         'Subject': {'Data': email_subject},
#     #         'Body': {'Text': {'Data': email_body}}
#     #     }
#     # )
    
#     return True


# UserResponse

async def create_family_member(req: UserCreate, db: Session)-> UserResponse:

    print('it reach here sha:', req)
    try:

         # Check if user already exists
        existing_user = db.query(User).filter(
            (User.email == req.email)
        ).first()
        
        if existing_user:
            print('user already exists')
            raise HTTPException(
                status_code=400, 
                detail="User with this email or username already exists"
            )

        def generate_random_password(length=16):
                alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
                return ''.join(secrets.choice(alphabet) for i in range(length))
    
        temporary_password = generate_random_password()
        m2m_token = await get_management_api_token()
    
        # Create user via Management API
        management_api_url = f"https://{os.getenv('AUTH0_DOMAIN')}/api/v2/users"
        
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
                "setup_required": True
            }
            }
        
        headers = {
            "Authorization": f"Bearer {m2m_token}",
            "Content-Type": "application/json"
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(management_api_url, json=payload, headers=headers)
                response.raise_for_status()
                
                user_data = response.json()

                await send_password_reset_with_auth0(user_data['user_id'])

            
            
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code, 
                detail=f"Error creating user in Auth0: {e.response.text}"
            )

  
        
        # Create new user instance
        new_user = User(
            username=req.name,
            email=req.email,
            name= f"{req.name} {req.family_name}",
            role=UserRole.member,
            family_id=req.family_id, 

            # Assuming family_id is provided in the request
            # is_active, created_at, updated_at will use defaults
        )

        
        # Add to database
        db.add(new_user)
        db.commit()
        db.refresh(new_user)  # Refresh to get the ID and timestamps
        # Convert to Pydantic model and return
        return UserResponse.model_validate(new_user)

    except HTTPException as e:
        logging.error(f"HTTPException: {e.detail}")
        raise

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, 
            detail="User with this email or username already exists"
        )
    except Exception as e:
        print("Error creating user:", str(e))
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")
    

# -> UserResponse
async def get_user(req:UserRequest, db: Session):
   
    
    try:
       # First, get the user
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

        
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Error getting user: {str(e)}")
    

   
def delete_user(user_id: int, db: Session) :
    try:
        print('e reach here',user_id) 
        result = db.query(User).filter(User.public_id == user_id).update({"is_active": False})
        db.commit()
        return result
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500,
    detail={"error": str(e)} )
    



