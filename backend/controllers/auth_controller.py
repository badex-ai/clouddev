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


# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

async def check_idempotency(key: str, redis_client) -> dict | None:
    cached = await redis_client.get(f"idempotency:{key}")
    if cached:
        logger.info("idempotency_hit", key=key)
        return json.loads(cached)
    return None


async def store_idempotency(key: str, data: dict, redis_client, ttl: int = 3600):
    await redis_client.setex(f"idempotency:{key}", ttl, json.dumps(data))


def check_user_exists(db: Session, email: str, username: str) -> bool:
    return (
        db.query(User)
        .filter((User.email == email) | (User.username == username))
        .first()
        is not None
    )


# ==============================================================================
# AUTH0 INTEGRATION
# ==============================================================================

async def create_auth0_user(
    email: str, password: str, name: str, family_name: str
) -> dict:
    """
    Create user in Auth0.
    
    BIG TECH PATTERN:
    - Convert HTTP errors to AppError
    - Parse Auth0 error messages
    - User-friendly messages for common errors
    """
    signup_url = f"https://{auth0_domain}/dbconnections/signup"

    payload = {
        "client_id": auth0_client_id,
        "connection": "Username-Password-Authentication",
        "email": email,
        "password": password,
        "user_metadata": {"name": name, "family_name": family_name},
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(signup_url, json=payload)
            response.raise_for_status()

            auth0_user = response.json()
            logger.info("auth0_user_created", email=email)
            return auth0_user

        except httpx.HTTPStatusError as e:
            # Parse Auth0 error response
            try:
                error_data = e.response.json()
                error_message = (
                    error_data.get("description")
                    or error_data.get("error_description")
                    or error_data.get("message")
                    or str(e)
                )
                
                # Check for password validation errors
                if "rules" in error_data:
                    rules = error_data.get("rules", [])
                    error_message = f"Password requirements: {rules}"
                
            except:
                error_message = str(e)

            logger.error("auth0_signup_failed", email=email, error=error_message)

            raise AppError(
                code=ErrorCode.BAD_REQUEST if e.response.status_code < 500 else ErrorCode.INTERNAL_SERVER_ERROR,
                status_code=e.response.status_code,
                technical_message=f"Auth0 signup failed: {error_message}",
                user_message="Failed to create your account. Please check your information and try again.",
                is_operational=True,
                details={"email": email, "auth0_status": e.response.status_code},
            )

        except httpx.RequestError as e:
            logger.error("auth0_network_error", email=email, error=str(e))

            raise AppError(
                code=ErrorCode.SERVICE_UNAVAILABLE,
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                technical_message=f"Auth0 connection error: {str(e)}",
                user_message="Authentication service is temporarily unavailable",
                is_operational=True,
                details={"email": email},
            )


# ==============================================================================
# DATABASE OPERATIONS
# ==============================================================================

def create_family_record(db: Session, name: str) -> Family:
    """
    Create family record in database.
    
    BIG TECH PATTERN:
    - Simple database operation
    - Let SQLAlchemy errors propagate
    """
    new_family = Family(name=name)
    db.add(new_family)
    db.flush()

    logger.info("family_created", family_id=new_family.public_id)
    return new_family


def create_user_record(
    db: Session, username: str, email: str, name: str, family_id: str
) -> User:
    """
    Create user record in database.
    
    BIG TECH PATTERN:
    - Simple database operation
    - Let SQLAlchemy errors propagate
    """
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


# ==============================================================================
# PUBLIC API FUNCTIONS
# ==============================================================================

async def logout():
    return {"message": "Logout successful"}


async def signup(req, db: Session, idempotency_key):
    """
    User signup with family creation.
    
    BIG TECH PATTERN (Netflix/Google):
    1. Check idempotency
    2. Validate business rules
    3. Create database records first (easy to rollback)
    4. Create Auth0 user (harder to rollback)
    5. Send verification email (async, non-critical)
    6. Commit transaction
    7. Handle all specific errors with context
    """
    logger.info("signup_started", email=req.email)
    redis_client = await get_redis()

    # Check idempotency cache
    if idempotency_key:
        cached = await check_idempotency(idempotency_key, redis_client)
        if cached:
            logger.info("idempotency_cache_hit", email=req.email)
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
                details={"email": req.email},
            )

        # Create database records FIRST (easy to rollback)
        new_family = create_family_record(db, req.family_name)
        new_user = create_user_record(
            db=db,
            username=req.name,
            email=req.email,
            name=req.name,
            family_id=new_family.public_id,
        )
        db.flush()

        # Create Auth0 user (can raise AppError)
        try:
            auth0_user = await create_auth0_user(
                email=req.email,
                password=req.password,
                name=req.name,
                family_name=req.family_name,
            )
        except AppError:
            # Auth0 failed - rollback database
            db.rollback()
            raise

        # Send verification email (async, non-blocking)
        # Failure here should NOT fail the signup
        try:
            send_verification_email_task.delay(req.email, req.name)
        except Exception as e:
            # Email failure is not critical, just log it
            logger.warning("verification_email_failed", email=req.email, error=str(e))

        # Commit everything
        db.commit()

        response_data = {
            "message": "User created successfully. Please check your email to verify your account.",
            "user_id": new_user.public_id,
            "email": req.email,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "requires_verification": True,
        }

        # Store in idempotency cache
        if idempotency_key:
            await store_idempotency(idempotency_key, response_data, redis_client)

        logger.info("signup_completed", email=req.email)
        return response_data

    except AppError:
        # AppError already has context, just re-raise
        db.rollback()
        raise

    except IntegrityError as e:
        # Database constraint violation
        db.rollback()
        error_message = str(e.orig) if hasattr(e, "orig") else str(e)
        logger.error("integrity_error_signup", email=req.email, error=error_message)

        if "unique constraint" in error_message.lower():
            raise AppError(
                code=ErrorCode.CONFLICT,
                status_code=status.HTTP_409_CONFLICT,
                technical_message=f"Unique constraint violation: {error_message}",
                user_message="An account with this information already exists",
                is_operational=True,
                details={"email": req.email},
            )
        else:
            raise AppError(
                code=ErrorCode.INTERNAL_SERVER_ERROR,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                technical_message=f"Database integrity error: {error_message}",
                user_message="Unable to create account due to data validation error",
                is_operational=True,
                details={"email": req.email},
            )

    except SQLAlchemyError as e:
        # General database error
        db.rollback()
        logger.error("database_error_signup", email=req.email, error=str(e))

        raise AppError(
            code=ErrorCode.INTERNAL_SERVER_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            technical_message=f"Database error during signup: {str(e)}",
            user_message="Unable to create your account. Please try again.",
            is_operational=True,
            details={"email": req.email},
        )

    except ValueError as e:
        # Input validation error
        db.rollback()
        logger.error("validation_error_signup", email=req.email, error=str(e))

        raise AppError(
            code=ErrorCode.VALIDATION_ERROR,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            technical_message=f"Validation error: {str(e)}",
            user_message="Invalid input data. Please check your information.",
            is_operational=True,
            details={"email": req.email},
        )

    except Exception as e:
        # Unexpected error - let global handler catch it
        db.rollback()
        logger.error(
            "unexpected_error_signup",
            email=req.email,
            error=str(e),
            error_type=type(e).__name__,
        )
        raise AppError(
        code=ErrorCode.INTERNAL_SERVER_ERROR,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        technical_message=f"Unexpected error: {str(e)}",
        user_message="Something went wrong. Please try again later.",
        is_operational=False,
        details={"email": req.email},
    )