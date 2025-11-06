import os
import secrets
from fastapi import HTTPException, Depends, Request, status
import httpx 
from sqlalchemy.orm import Session,joinedload,selectinload
from sqlalchemy.exc import IntegrityError,SQLAlchemyError
from models.models import User, Family
from schemas.schemas import (
    UserCreate, UserResponse, UserUpdate, UserRequest,
     TaskResponse, TaskUpdate, FamilyResponse, FamilyRequest, FamilyUsers, UserRole
)
import string
from utils import utils

from config.env import get_config
from utils.utils import get_management_api_token
# from utils.error_handler import ErrorHandler
from controllers.tasks import send_welcome_email_task, send_password_reset_task
from config.db import get_redis
import json
from structlog import get_logger

import logging

import traceback
from utils.utils import send_email, get_management_api_token 

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)



logger = get_logger()
config = get_config()

auth0_domain = config["auth0_domain"]
auth0_client_id = config["auth0_client_id"]
auth0_m2m_client_id = config["auth0_m2m_client_id"]
auth0_m2m_client_secret = config["auth0_m2m_client_secret"]  # SECRET






def generate_random_password(length: int = 16) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


async def check_idempotency(key: str, redis_client) -> dict | None:
    cached = await redis_client.get(f"idempotency:{key}")
    if cached:
        logger.info("idempotency_hit", key=key)
        return json.loads(cached)
    return None


async def store_idempotency(key: str, data: dict, redis_client, ttl: int = 3600):
    await redis_client.setex(
        f"idempotency:{key}",
        ttl,
        json.dumps(data)
    )


def check_user_exists(db: Session, email: str) -> bool:
    return db.query(User).filter(User.email == email).first() is not None


async def create_auth0_user(
    email: str,
    name: str,
    family_name: str,
    family_id: str,
    m2m_token: str
) -> tuple[str, str]:
    temporary_password = generate_random_password()
    management_api_url = f"https://{auth0_domain}/api/v2/users"
    
    payload = {
        "email": email,
        "name": name,
        "family_name": family_name,
        "connection": "Username-Password-Authentication",
        "password": temporary_password,
        "email_verified": False,
        "verify_email": False,
        "app_metadata": {
            "created_by_admin": True,
            "setup_required": True,
            "family_id": family_id
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
            
            logger.info("auth0_user_created", email=email, user_id=user_data['user_id'])
            return user_data['user_id'], m2m_token
            
        except httpx.HTTPStatusError as e:
            ErrorHandler.handle_auth0_error(e, {"email": email})
        except httpx.RequestError as e:
            ErrorHandler.handle_network_error(e, {"email": email})


async def create_password_reset_ticket(user_id: str, m2m_token: str) -> str:
    ticket_url = f"https://{auth0_domain}/api/v2/tickets/password-change"
    
    payload = {
        "user_id": user_id,
        "ttl_sec": 604800,
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
            result = response.json()
            
            logger.info("password_reset_ticket_created", user_id=user_id)
            return result.get('ticket')
            
    except httpx.HTTPStatusError as e:
        ErrorHandler.handle_auth0_error(e, {"user_id": user_id})
    except httpx.RequestError as e:
        ErrorHandler.handle_network_error(e, {"user_id": user_id})


async def delete_auth0_user(user_id: str, m2m_token: str):
    delete_url = f"https://{auth0_domain}/api/v2/users/{user_id}"
    headers = {"Authorization": f"Bearer {m2m_token}"}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.delete(delete_url, headers=headers)
            response.raise_for_status()
            logger.info("auth0_user_deleted", user_id=user_id)
        except Exception as e:
            logger.warning("auth0_user_deletion_failed", user_id=user_id, error=str(e))


def create_db_user(
    db: Session,
    name: str,
    email: str,
    family_id: str
) -> User:
    new_user = User(
        username=name,
        email=email,
        name=name,
        role="member",
        family_id=family_id,
    )
    
    db.add(new_user)
    db.flush()
    
    logger.info("db_user_created", email=email, user_id=new_user.public_id)
    return new_user


async def create_family_member(req: UserCreate, db: Session, idempotency_key: str = None):
    logger.info("create_family_member_started", email=req.email)
    
    redis_client = await get_redis()
    
    if idempotency_key:
        cached = await check_idempotency(idempotency_key, redis_client)
        if cached:
            return UserResponse(**cached)
    
    auth0_user_id = None
    db_user_created = False
    
    # try:
    if check_user_exists(db, req.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    m2m_token = await get_management_api_token()
    
    auth0_user_id, m2m_token = await create_auth0_user(
        email=req.email,
        name=req.name,
        family_name=req.family_name,
        family_id=req.family_id,
        m2m_token=m2m_token
    )
    
    try:
        ticket_url = await create_password_reset_ticket(auth0_user_id, m2m_token)
    except Exception as e:
        logger.error("password_reset_failed", user_id=auth0_user_id, error=str(e))
        await delete_auth0_user(auth0_user_id, m2m_token)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send password setup email. User creation cancelled."
        )
    
    send_welcome_email_task.delay(
        email=req.email,
        name=req.name,
        password_reset_url=ticket_url,
        admin_name="Admin"
    )
    
    # try:
    new_user = create_db_user(db, req.name, req.email, req.family_id)
    db.commit()
    db_user_created = True
    
    response_data = UserResponse.model_validate(new_user).model_dump()
    
    if idempotency_key:
        await store_idempotency(idempotency_key, response_data, redis_client)
    
    logger.info("create_family_member_completed", email=req.email)
    return UserResponse(**response_data)
            
    
        
 


async def get_user(req: UserRequest, db: Session):
    logger.info("get_user_started", email=req.user_email)
    
    user = db.query(User).filter(User.email == req.user_email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    family_members = db.query(User).filter(
        User.family_id == user.family_id,
        User.is_active == True
    ).all()
    
    family = db.query(Family).filter(Family.public_id == user.family_id).first()
    
    if not family:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Family not found"
        )
    
    response_data = {
        "id": user.public_id,
        "username": user.username,
        "email": user.email,
        "name": user.name,
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
    
    logger.info("get_user_completed", email=req.user_email)
    return response_data
    
   


def deactivate_user(user_id: str, db: Session) -> int:
    logger.info("deactivate_user_started", user_id=user_id)
    
    
    result = db.query(User).filter(User.public_id == user_id).update({"is_active": False})
    
    if result == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db.commit()
    logger.info("deactivate_user_completed", user_id=user_id)
    return result
        
    


def reactivate_user(user_id: str, db: Session) -> int:
    logger.info("reactivate_user_started", user_id=user_id)
    
    
    result = db.query(User).filter(User.public_id == user_id).update({"is_active": True})
    
    if result == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db.commit()
    logger.info("reactivate_user_completed", user_id=user_id)
    return result
        
    
