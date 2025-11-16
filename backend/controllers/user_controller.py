import os
import secrets
from fastapi import HTTPException, Depends, Request, status
import httpx
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from models.models import User, Family
from schemas.schemas import (
    UserCreate,
    UserResponse,
    UserUpdate,
    UserRequest,
    TaskResponse,
    TaskUpdate,
    FamilyResponse,
    FamilyRequest,
    FamilyUsers,
    UserRole,
)
import string
from utils import utils

from config.env import get_config
from utils.utils import get_management_api_token
from utils.error_handler import AppError, ErrorCode  # ← ADDED
from controllers.tasks import send_welcome_email_task, send_password_reset_task
from config.db import get_redis
import json
from structlog import get_logger

import logging
import traceback
from utils.utils import send_email, get_management_api_token

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)


logger = get_logger()
config = get_config()

auth0_domain = config["auth0_domain"]
auth0_client_id = config["auth0_client_id"]
auth0_m2m_client_id = config["auth0_m2m_client_id"]
auth0_m2m_client_secret = config["auth0_m2m_client_secret"]


# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def generate_random_password(length: int = 16) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(secrets.choice(alphabet) for _ in range(length))


async def check_idempotency(key: str, redis_client) -> dict | None:
    cached = await redis_client.get(f"idempotency:{key}")
    if cached:
        logger.info("idempotency_hit", key=key)
        return json.loads(cached)
    return None


async def store_idempotency(key: str, data: dict, redis_client, ttl: int = 3600):
    await redis_client.setex(f"idempotency:{key}", ttl, json.dumps(data))


def check_user_exists(db: Session, email: str) -> bool:
    return db.query(User).filter(User.email == email).first() is not None


# ==============================================================================
# AUTH0 INTEGRATION FUNCTIONS - With proper error handling
# ==============================================================================

async def create_auth0_user(
    email: str, name: str, family_name: str, family_id: str, m2m_token: str
) -> tuple[str, str]:
    """
    Create user in Auth0 Management API.
    
    BIG TECH PATTERN:
    - Convert Auth0 HTTP errors to AppError
    - Add context for debugging
    - User-friendly messages
    """
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
            "family_id": family_id,
        },
    }

    headers = {
        "Authorization": f"Bearer {m2m_token}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                management_api_url, json=payload, headers=headers
            )
            response.raise_for_status()
            user_data = response.json()

            logger.info("auth0_user_created", email=email, user_id=user_data["user_id"])
            return user_data["user_id"], m2m_token

        except httpx.HTTPStatusError as e:
            # Auth0 returned an error response
            try:
                error_data = e.response.json()
                error_message = (
                    error_data.get("message") 
                    or error_data.get("error_description")
                    or str(e)
                )
            except:
                error_message = str(e)
            
            logger.error("auth0_user_creation_failed", email=email, error=error_message)
            
            raise AppError(
                code=ErrorCode.BAD_REQUEST if e.response.status_code < 500 else ErrorCode.INTERNAL_SERVER_ERROR,
                status_code=e.response.status_code,
                technical_message=f"Auth0 user creation failed: {error_message}",
                user_message="Unable to create user account. Please try again.",
                is_operational=True,
                details={"email": email, "auth0_status": e.response.status_code}
            )
        
        except httpx.RequestError as e:
            # Network error connecting to Auth0
            logger.error("auth0_network_error", email=email, error=str(e))
            
            raise AppError(
                code=ErrorCode.SERVICE_UNAVAILABLE,
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                technical_message=f"Auth0 network error: {str(e)}",
                user_message="Authentication service is temporarily unavailable. Please try again later.",
                is_operational=True,
                details={"email": email}
            )


async def create_password_reset_ticket(user_id: str, m2m_token: str) -> str:
    """
    Create password reset ticket in Auth0.
    
    BIG TECH PATTERN:
    - Same error handling as create_auth0_user
    - Consistent error messages
    """
    ticket_url = f"https://{auth0_domain}/api/v2/tickets/password-change"

    payload = {"user_id": user_id, "ttl_sec": 604800, "mark_email_as_verified": True}

    headers = {
        "Authorization": f"Bearer {m2m_token}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(ticket_url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()

            logger.info("password_reset_ticket_created", user_id=user_id)
            return result.get("ticket")

    except httpx.HTTPStatusError as e:
        try:
            error_data = e.response.json()
            error_message = error_data.get("message") or str(e)
        except:
            error_message = str(e)
        
        logger.error("password_reset_ticket_failed", user_id=user_id, error=error_message)
        
        raise AppError(
            code=ErrorCode.BAD_REQUEST if e.response.status_code < 500 else ErrorCode.INTERNAL_SERVER_ERROR,
            status_code=e.response.status_code,
            technical_message=f"Password reset ticket creation failed: {error_message}",
            user_message="Unable to generate password setup link. Please try again.",
            is_operational=True,
            details={"user_id": user_id, "auth0_status": e.response.status_code}
        )
    
    except httpx.RequestError as e:
        logger.error("password_reset_network_error", user_id=user_id, error=str(e))
        
        raise AppError(
            code=ErrorCode.SERVICE_UNAVAILABLE,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            technical_message=f"Network error creating password reset: {str(e)}",
            user_message="Authentication service is temporarily unavailable. Please try again later.",
            is_operational=True,
            details={"user_id": user_id}
        )


async def delete_auth0_user(user_id: str, m2m_token: str):
    """
    Delete user from Auth0 (cleanup operation).
    
    BIG TECH PATTERN:
    - Cleanup operations should not fail the main operation
    - Log warnings but don't raise errors
    """
    delete_url = f"https://{auth0_domain}/api/v2/users/{user_id}"
    headers = {"Authorization": f"Bearer {m2m_token}"}

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.delete(delete_url, headers=headers)
            response.raise_for_status()
            logger.info("auth0_user_deleted", user_id=user_id)
        except Exception as e:
            # Cleanup failure - log but don't raise
            logger.warning("auth0_user_deletion_failed", user_id=user_id, error=str(e))


# ==============================================================================
# DATABASE OPERATIONS
# ==============================================================================

def create_db_user(db: Session, name: str, email: str, family_id: str) -> User:
    """
    Create user in database.
    
    BIG TECH PATTERN:
    - Simple database operation
    - Let SQLAlchemy errors propagate to caller
    """
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


# ==============================================================================
# PUBLIC API FUNCTIONS
# ==============================================================================

async def create_family_member(
    req: UserCreate, db: Session, idempotency_key: str = None
) -> UserResponse:
    """
    Create a new family member (admin adding user).
    
    BIG TECH PATTERN (Netflix/Google):
    1. Check idempotency first
    2. Validate business rules
    3. Create external resources (Auth0)
    4. Create database records
    5. Handle rollback if needed
    6. Let specific errors propagate
    """
    logger.info("create_family_member_started", email=req.email)

    redis_client = await get_redis()

    # Check idempotency
    if idempotency_key:
        cached = await check_idempotency(idempotency_key, redis_client)
        if cached:
            logger.info("idempotency_cache_hit", email=req.email)
            return UserResponse(**cached)

    auth0_user_id = None

    try:
        # Validate: Check if user already exists
        if check_user_exists(db, req.email):
            raise AppError(
                code=ErrorCode.CONFLICT,
                status_code=status.HTTP_409_CONFLICT,
                technical_message=f"User already exists: email={req.email}",
                user_message="A user with this email already exists",
                is_operational=True,
                details={"email": req.email}
            )

        # Get Auth0 management token
        m2m_token = await get_management_api_token()

        # Create Auth0 user (can raise AppError)
        auth0_user_id, m2m_token = await create_auth0_user(
            email=req.email,
            name=req.name,
            family_name=req.family_name,
            family_id=req.family_id,
            m2m_token=m2m_token,
        )

        # Create password reset ticket (can raise AppError)
        try:
            ticket_url = await create_password_reset_ticket(auth0_user_id, m2m_token)
        except AppError as e:
            # Password reset failed - rollback Auth0 user
            logger.error("password_reset_failed_rolling_back", 
                        user_id=auth0_user_id, error=str(e))
            await delete_auth0_user(auth0_user_id, m2m_token)
            
            # Re-raise with better context
            raise AppError(
                code=ErrorCode.INTERNAL_SERVER_ERROR,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                technical_message=f"Password setup failed: {e.technical_message}",
                user_message="Unable to send password setup email. User creation cancelled.",
                is_operational=True,
                details={"email": req.email, "auth0_user_id": auth0_user_id}
            )

        # Send welcome email (async, non-blocking)
        send_welcome_email_task.delay(
            email=req.email,
            name=req.name,
            password_reset_url=ticket_url,
            admin_name="Admin",
        )

        # Create database user
        new_user = create_db_user(db, req.name, req.email, req.family_id)
        db.commit()

        response_data = UserResponse.model_validate(new_user).model_dump()

        # Store in idempotency cache
        if idempotency_key:
            await store_idempotency(idempotency_key, response_data, redis_client)

        logger.info("create_family_member_completed", email=req.email)
        return UserResponse(**response_data)

    except AppError:
        # AppError already has context, just re-raise
        db.rollback()
        raise
    
    except SQLAlchemyError as e:
        # Database error - rollback everything
        db.rollback()
        logger.error("database_error_create_family_member", 
                    email=req.email, error=str(e))
        
        # Cleanup Auth0 user if created
        if auth0_user_id:
            await delete_auth0_user(auth0_user_id, m2m_token)
        
        raise AppError(
            code=ErrorCode.INTERNAL_SERVER_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            technical_message=f"Database error creating user: {str(e)}",
            user_message="Unable to create user account. Please try again.",
            is_operational=True,
            details={"email": req.email}
        )
    
    except Exception as e:
        # Unexpected error - rollback and cleanup
        db.rollback()
        logger.error("unexpected_error_create_family_member", 
                    email=req.email, error=str(e), error_type=type(e).__name__)
        
        # Cleanup Auth0 user if created
        if auth0_user_id:
            await delete_auth0_user(auth0_user_id, m2m_token)
        
        # Let global handler catch it
        raise


async def get_user(req: UserRequest, db: Session):
    """
    Get user with family information.
    
    BIG TECH PATTERN:
    - Simple query with validation
    - Return structured data
    - Let database errors propagate
    """
    logger.info("get_user_started", email=req.user_email)

    try:
        # Query user
        user = db.query(User).filter(User.email == req.user_email).first()

        if not user:
            raise AppError(
                code=ErrorCode.NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND,
                technical_message=f"User not found: email={req.user_email}",
                user_message="User not found",
                is_operational=True,
                details={"email": req.user_email}
            )

        # Query family members
        family_members = (
            db.query(User)
            .filter(User.family_id == user.family_id, User.is_active == True)
            .all()
        )

        # Query family
        family = db.query(Family).filter(Family.public_id == user.family_id).first()

        if not family:
            raise AppError(
                code=ErrorCode.NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND,
                technical_message=f"Family not found: family_id={user.family_id}",
                user_message="Family information not found",
                is_operational=True,
                details={"family_id": user.family_id}
            )

        # Build response
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
                        "role": member.role.value,  # Access enum value
                    }
                    for member in family_members
                ],
            },
        }

        logger.info("get_user_completed", email=req.user_email)
        return response_data

    except AppError:
        # Already has context
        raise
    
    except SQLAlchemyError as e:
        logger.error("database_error_get_user", email=req.user_email, error=str(e))
        
        raise AppError(
            code=ErrorCode.INTERNAL_SERVER_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            technical_message=f"Database error retrieving user: {str(e)}",
            user_message="Unable to retrieve user information",
            is_operational=True,
            details={"email": req.user_email}
        )


def deactivate_user(user_id: str, db: Session) -> int:
    """
    Deactivate a user.
    
    BIG TECH PATTERN:
    - Simple update operation
    - Validate result
    - Let database errors propagate
    """
    logger.info("deactivate_user_started", user_id=user_id)

    try:
        result = (
            db.query(User)
            .filter(User.public_id == user_id)
            .update({"is_active": False})
        )

        if result == 0:
            raise AppError(
                code=ErrorCode.NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND,
                technical_message=f"User not found for deactivation: user_id={user_id}",
                user_message="User not found",
                is_operational=True,
                details={"user_id": user_id}
            )

        db.commit()
        logger.info("deactivate_user_completed", user_id=user_id)
        return result

    except AppError:
        db.rollback()
        raise
    
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("database_error_deactivate_user", user_id=user_id, error=str(e))
        
        raise AppError(
            code=ErrorCode.INTERNAL_SERVER_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            technical_message=f"Database error deactivating user: {str(e)}",
            user_message="Unable to deactivate user",
            is_operational=True,
            details={"user_id": user_id}
        )


def reactivate_user(user_id: str, db: Session) -> int:
    """
    Reactivate a user.
    
    BIG TECH PATTERN:
    - Same pattern as deactivate_user
    """
    logger.info("reactivate_user_started", user_id=user_id)

    try:
        result = (
            db.query(User)
            .filter(User.public_id == user_id)
            .update({"is_active": True})
        )

        if result == 0:
            raise AppError(
                code=ErrorCode.NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND,
                technical_message=f"User not found for reactivation: user_id={user_id}",
                user_message="User not found",
                is_operational=True,
                details={"user_id": user_id}
            )

        db.commit()
        logger.info("reactivate_user_completed", user_id=user_id)
        return result

    except AppError:
        db.rollback()
        raise
    
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("database_error_reactivate_user", user_id=user_id, error=str(e))
        
        raise AppError(
            code=ErrorCode.INTERNAL_SERVER_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            technical_message=f"Database error reactivating user: {str(e)}",
            user_message="Unable to reactivate user",
            is_operational=True,
            details={"user_id": user_id}
        )