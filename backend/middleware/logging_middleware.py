"""
Request logging middleware for FastAPI.
Logs meaningful request/response information to CloudWatch.

What gets logged:
- INFO: All requests (method, path, status, duration, user_id if available)
- WARNING: Slow requests (>2 seconds)
- Skips: Health checks, static files
"""

import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from config.logging import get_logger

logger = get_logger("request")

# Paths to skip logging (noisy/unimportant)
SKIP_PATHS = {"/health", "/favicon.ico", "/robots.txt"}

# Slow request threshold in seconds
SLOW_REQUEST_THRESHOLD = 2.0


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log HTTP requests with timing and context"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip health checks and static files
        if request.url.path in SKIP_PATHS:
            return await call_next(request)

        # Generate request ID for tracing
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])

        # Extract user info if available (from Auth0 token)
        user_id = None
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            # We don't decode the token here, just note that auth is present
            user_id = "authenticated"

        # Start timing
        start_time = time.perf_counter()

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration_ms = (time.perf_counter() - start_time) * 1000
        duration_s = duration_ms / 1000

        # Build log context
        log_context = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2),
            "client_ip": _get_client_ip(request),
        }

        # Add user_id if present
        if user_id:
            log_context["user_authenticated"] = True

        # Add query params for non-GET requests (useful for debugging)
        if request.method != "GET" and request.query_params:
            log_context["query_params"] = str(request.query_params)

        # Log based on status and duration
        if response.status_code >= 500:
            logger.error("request_failed", **log_context)
        elif response.status_code >= 400:
            logger.warning("request_client_error", **log_context)
        elif duration_s > SLOW_REQUEST_THRESHOLD:
            logger.warning("request_slow", **log_context)
        else:
            logger.info("request_completed", **log_context)

        # Add request ID to response headers for client-side correlation
        response.headers["X-Request-ID"] = request_id

        return response


def _get_client_ip(request: Request) -> str:
    """Extract client IP, handling proxies/load balancers"""
    # Check X-Forwarded-For header (set by ALB/proxy)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # First IP is the original client
        return forwarded_for.split(",")[0].strip()

    # Fallback to direct client IP
    if request.client:
        return request.client.host

    return "unknown"
