import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from fastapi import HTTPException, status
import httpx 
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from config.env import get_config
from models.models import User, Family, UserRole
from utils.error_handler import AppError, ErrorCode
from utils.email_templates import VERIFICATION_EMAIL
from controllers.tasks import send_verification_email_task
from config.db import get_redis
import json
from structlog import get_logger

load_dotenv()

logger = get_logger()
config = get_config()

auth0_domain = config["auth0_domain"]
auth0_client_id = config["auth0_client_id"]
auth0_m2m_client_id = config["auth0_m2m_client_id"]
auth0_m2m_client_secret = config["auth0_m2m_client_secret"]


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


def check_user_exists(db: Session, email: str, username: str) -> bool:
    return db.query(User).filter(
        (User.email == email) | (User.username == username)
    ).first() is not None


async def create_auth0_user(
    email: str,
    password: str,
    name: str,
    family_name: str
) -> dict:
    signup_url = f"https://{auth0_domain}/dbconnections/signup"
    
    payload = {
        "client_id": auth0_client_id,
        "connection": "Username-Password-Authentication",
        "email": email,
        "password": password,
        "user_metadata": {
            "name": name,
            "family_name": family_name
        }
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(signup_url, json=payload)
            response.raise_for_status()
            
            auth0_user = response.json()
            logger.info("auth0_user_created", email=email)
            return auth0_user
            
           


def create_family_record(db: Session, name: str) -> Family:
    new_family = Family(name=name)
    db.add(new_family)
    db.flush()
    
    logger.info("family_created", family_id=new_family.public_id)
    return new_family


def create_user_record(
    db: Session,
    username: str,
    email: str,
    name: str,
    family_id: str
) -> User:
    new_user = User(
        username=username,
        email=email,
        name=name,
        family_id=family_id,
        role=UserRole.admin,
    )
    
    db.add(new_user)
    db.flush()
    
    logger.info("user_created", email=email, user_id=new_user.public_id)
    return new_user


async def logout():
    return {"message": "Logout successful"}


# async def signup(req,db: Session,idempotency_key):
#     logger.info("signup_started", email=req.email)
#     redis_client = await get_redis()
#     print("redis client", redis_client)
#     print("idempotency", idempotency_key)
    
#     if idempotency_key:
#         cached = await check_idempotency(idempotency_key, redis_client)
#         if cached:
#             return cached
    
#         # STEP 1: Check user exists
#         if check_user_exists(db, req.email, req.name):
#             raise HTTPException(status_code=400, detail="User already exists")
        
#         # STEP 2: Create DB records FIRST (can rollback easily)
#         new_family = create_family_record(db, req.family_name)
#         new_user = create_user_record(
#             db=db,
#             username=req.name,
#             email=req.email,
#             name=req.name,
#             family_id=new_family.public_id
#         )
#         db.flush()
        
#         # STEP 3: Now create Auth0 user (only if DB succeeded)
#         try:
#             auth0_user = await create_auth0_user(
#                 email=req.email,
#                 password=req.password,
#                 name=req.name,
#                 family_name=req.family_name
#             )
#         except Exception as e:
#             # Auth0 failed - rollback DB
#             db.rollback()
#             raise HTTPException(500, "Failed to create Auth0 account")
        
#         send_verification_email_task(req.email, req.name)
#         # STEP 4: Everything succeeded - commit DB
#         db.commit()
            
#         response_data = {
#             "message": "User created successfully. Please check your email to verify your account.",
#             "user_id": new_user.public_id,
#             "email": req.email,
#             "created_at": datetime.now(timezone.utc).isoformat(),
#             "requires_verification": True
#         }
        
#         if idempotency_key:
#             await store_idempotency(idempotency_key, response_data, redis_client)
        
#         logger.info("signup_completed", email=req.email)
#         return response_data
        
 

async def signup(req, db: Session, idempotency_key):
    logger.info("signup_started", email=req.email)
    redis_client = await get_redis()
    
    if idempotency_key:
        cached = await check_idempotency(idempotency_key, redis_client)
        if cached:
            return cached
    
    try:
        # Business validation
        if check_user_exists(db, req.email, req.name):
            raise AppError(
                code=ErrorCode.CONFLICT,
                status_code=status.HTTP_409_CONFLICT,
                technical_message=f"User exists: email={req.email}, username={req.name}",
                user_message="An account with this email or username already exists",
                is_operational=True,
                details={"email": req.email}
            )
        
        # Create DB records
        new_family = create_family_record(db, req.family_name)
        new_user = create_user_record(
            db=db,
            username=req.name,
            email=req.email,
            name=req.name,
            family_id=new_family.public_id
        )
        db.flush()
        
        # Create Auth0 user
        try:
            auth0_user = await create_auth0_user(
                email=req.email,
                password=req.password,
                name=req.name,
                family_name=req.family_name
            )
        except httpx.HTTPStatusError as e:
            # Auth0-specific error needs custom handling
            db.rollback()
            try:
                error_data = e.response.json()
                error_message = error_data.get('description') or error_data.get('error_description') or str(e)
            except:
                error_message = str(e)
            
            raise AppError(
                code=ErrorCode.BAD_REQUEST,
                status_code=e.response.status_code,
                technical_message=f"Auth0 signup failed: {error_message}",
                user_message="Failed to create your account. Please check your information and try again.",
                is_operational=True,
                details={"email": req.email, "auth0_status": e.response.status_code}
            )
        except httpx.RequestError as e:
            db.rollback()
            raise AppError(
                code=ErrorCode.SERVICE_UNAVAILABLE,
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                technical_message=f"Auth0 connection error: {str(e)}",
                user_message="Authentication service is temporarily unavailable",
                is_operational=True,
                details={"email": req.email}
            )
        
        # Send verification email (async, non-blocking)
        send_verification_email_task.delay(req.email, req.name)
        
        # Commit everything
        db.commit()
        
        response_data = {
            "message": "User created successfully. Please check your email to verify your account.",
            "user_id": new_user.public_id,
            "email": req.email,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "requires_verification": True
        }
        
        if idempotency_key:
            await store_idempotency(idempotency_key, response_data, redis_client)
        
        logger.info("signup_completed", email=req.email)
        return response_data
    
    except AppError:
        # Re-raise AppErrors as-is
        raise
    except Exception:
        # All other errors bubble to global handler
        db.rollback()
        raise