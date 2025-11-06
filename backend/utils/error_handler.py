
from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import os
import traceback

from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import httpx
import structlog
import logging

# Configure structlog for production-ready logging
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer() if os.getenv("ENVIRONMENT") == "production"
        else structlog.dev.ConsoleRenderer(colors=True)
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


class ErrorCode(str, Enum):
    """Error codes matching frontend ErrorCode enum"""
    # Network Errors
    NETWORK_ERROR = "NETWORK_ERROR"
    REQUEST_TIMEOUT = "REQUEST_TIMEOUT"
    
    # API Errors
    BAD_REQUEST = "BAD_REQUEST"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    RATE_LIMIT = "RATE_LIMIT"
    
    # Server Errors
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    
    # Client Errors
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


class ErrorMetadata:
    """
    Metadata for error tracking and debugging
    Matches frontend ErrorMetadata interface
    """
    
    def __init__(
        self,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.request_id = request_id
        self.user_id = user_id
        self.context = context or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            **({"requestId": self.request_id} if self.request_id else {}),
            **({"userId": self.user_id} if self.user_id else {}),
            **({"context": self.context} if self.context else {})
        }



class AppError(Exception):
    """
    Application error with three levels of detail:
    1. user_message: Shown to end users (customer-facing) - NEVER technical
    2. technical_message: For customer support/logs - What actually happened
    3. stack_trace + details: For developers debugging - Full context
    
    Matches frontend AppError class structure
    """
    
    def __init__(
        self,
        code: ErrorCode,
        status_code: int,
        technical_message: str,
        user_message: str,
        is_operational: bool = True,
        details: Optional[Dict[str, Any]] = None,
        metadata: Optional[ErrorMetadata] = None
    ):
        self.code = code
        self.status_code = status_code
        self.user_message = user_message  # Customer sees this ONLY
        self.technical_message = technical_message  # Support/logs see this
        self.is_operational = is_operational
        self.details = details or {}
        self.metadata = metadata or ErrorMetadata()
        self.stack_trace = traceback.format_exc()
        
        super().__init__(self.technical_message)
    
    def to_json_for_client(self) -> Dict[str, Any]:
        """
        Minimal response for client - ONLY user-friendly message
        Matches frontend expected response format
        """
        return {
            "code": self.code.value,
            "message": self.user_message,  # User-friendly ONLY
            "timestamp": self.metadata.timestamp,
            **({"details": self.details} if self.details else {})
        }
    
    def to_json_for_logging(self) -> Dict[str, Any]:
        """
        Full error details for logging/monitoring (CloudWatch/X-Ray)
        This is what developers see for debugging
        """
        return {
            "code": self.code.value,
            "status_code": self.status_code,
            "user_message": self.user_message,  # What customer saw
            "technical_message": self.technical_message,  # What really happened
            "is_operational": self.is_operational,
            "details": self.details,
            "metadata": self.metadata.to_dict(),
            "stack_trace": self.stack_trace if not self.is_operational else None,
            "environment": os.getenv("ENVIRONMENT", "development")
        }



async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global FastAPI exception handler that catches all unhandled exceptions
    and converts them to proper AppError responses
    """
    # If it's already an AppError, use it directly
    if isinstance(exc, AppError):
        logger.error(
            "application_error",
            **exc.to_json_for_logging()
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_json_for_client()
        )
    
    # Handle FastAPI HTTPException
    if isinstance(exc, HTTPException):
        app_error = AppError(
            code=ErrorCode.BAD_REQUEST if exc.status_code < 500 else ErrorCode.INTERNAL_SERVER_ERROR,
            status_code=exc.status_code,
            technical_message=str(exc.detail),
            user_message=exc.detail if exc.status_code < 500 else "An error occurred processing your request",
            is_operational=True,
            metadata=ErrorMetadata(
                request_id=request.headers.get("X-Request-ID"),
                context={"path": request.url.path, "method": request.method}
            )
        )
        logger.error("http_exception", **app_error.to_json_for_logging())
        return JSONResponse(
            status_code=app_error.status_code,
            content=app_error.to_json_for_client()
        )
    
    # Handle SQLAlchemy IntegrityError
    if isinstance(exc, IntegrityError):
        error_message = str(exc.orig) if hasattr(exc, 'orig') else str(exc)
        
        if "unique constraint" in error_message.lower():
            user_msg = "A record with this information already exists"
            tech_msg = f"Unique constraint violation: {error_message}"
        elif "foreign key constraint" in error_message.lower():
            user_msg = "Invalid reference to related data"
            tech_msg = f"Foreign key constraint violation: {error_message}"
        else:
            user_msg = "Database constraint violation"
            tech_msg = f"Database integrity error: {error_message}"
        
        app_error = AppError(
            code=ErrorCode.CONFLICT,
            status_code=status.HTTP_409_CONFLICT,
            technical_message=tech_msg,
            user_message=user_msg,
            is_operational=True,
            metadata=ErrorMetadata(
                request_id=request.headers.get("X-Request-ID"),
                context={"path": request.url.path}
            )
        )
        logger.error("integrity_error", **app_error.to_json_for_logging())
        return JSONResponse(
            status_code=app_error.status_code,
            content=app_error.to_json_for_client()
        )
    
    # Handle SQLAlchemy errors
    if isinstance(exc, SQLAlchemyError):
        app_error = AppError(
            code=ErrorCode.INTERNAL_SERVER_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            technical_message=f"Database error: {str(exc)}",
            user_message="A database error occurred",
            is_operational=True,
            metadata=ErrorMetadata(
                request_id=request.headers.get("X-Request-ID"),
                context={"path": request.url.path}
            )
        )
        logger.error("sqlalchemy_error", **app_error.to_json_for_logging())
        return JSONResponse(
            status_code=app_error.status_code,
            content=app_error.to_json_for_client()
        )
    
    # Handle Auth0/HTTP errors
    if isinstance(exc, httpx.HTTPStatusError):
        try:
            error_data = exc.response.json()
            error_message = (
                error_data.get('description') or 
                error_data.get('error_description') or 
                error_data.get('message') or 
                'Authentication service error'
            )
        except:
            error_message = exc.response.text or 'Unknown authentication error'
        
        app_error = AppError(
            code=ErrorCode.UNAUTHORIZED if exc.response.status_code == 401 else ErrorCode.BAD_REQUEST,
            status_code=exc.response.status_code,
            technical_message=f"Auth0 error: {error_message}",
            user_message="Authentication failed. Please try again.",
            is_operational=True,
            metadata=ErrorMetadata(
                request_id=request.headers.get("X-Request-ID"),
                context={"auth0_status": exc.response.status_code}
            )
        )
        logger.error("auth0_error", **app_error.to_json_for_logging())
        return JSONResponse(
            status_code=app_error.status_code,
            content=app_error.to_json_for_client()
        )
    
    # Handle network errors
    if isinstance(exc, httpx.RequestError):
        app_error = AppError(
            code=ErrorCode.SERVICE_UNAVAILABLE,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            technical_message=f"Network error: {str(exc)}",
            user_message="External service is temporarily unavailable",
            is_operational=True,
            metadata=ErrorMetadata(
                request_id=request.headers.get("X-Request-ID"),
                context={"error_type": type(exc).__name__}
            )
        )
        logger.error("network_error", **app_error.to_json_for_logging())
        return JSONResponse(
            status_code=app_error.status_code,
            content=app_error.to_json_for_client()
        )
    
    # Handle all other unexpected errors
    app_error = AppError(
        code=ErrorCode.INTERNAL_SERVER_ERROR,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        technical_message=f"Unexpected error: {type(exc).__name__}: {str(exc)}",
        user_message="An unexpected error occurred",
        is_operational=False,
        metadata=ErrorMetadata(
            request_id=request.headers.get("X-Request-ID"),
            context={"path": request.url.path, "error_type": type(exc).__name__}
        )
    )
    logger.error("unexpected_error", **app_error.to_json_for_logging())
    return JSONResponse(
        status_code=app_error.status_code,
        content=app_error.to_json_for_client()
    )



