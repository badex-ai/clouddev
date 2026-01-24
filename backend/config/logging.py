"""
Unified logging configuration for CloudWatch
- Development: Console output with colors (human-readable)
- Staging/Production: JSON output (CloudWatch-friendly)

Logs are written to stdout and picked up by CloudWatch Container Insights.
"""

import os
import logging
import structlog
from typing import Optional


ENVIRONMENT = os.getenv("ENVIRONMENT", "development")


def get_log_level() -> int:
    """Get log level based on environment"""
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    return getattr(logging, level, logging.INFO)


def setup_logging(service_name: str = "kaban-backend") -> structlog.BoundLogger:
    """
    Configure structlog for the application.

    Args:
        service_name: Name of the service (backend, celery, frontend)

    Returns:
        Configured structlog logger
    """
    # Shared processors for all environments
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    # Environment-specific renderer
    if ENVIRONMENT in ("staging", "production"):
        # JSON for CloudWatch - includes service metadata
        processors = shared_processors + [
            _add_service_info(service_name),
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Pretty console output for development
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(get_log_level()),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    return structlog.get_logger()


def _add_service_info(service_name: str):
    """Add service metadata to log entries for CloudWatch filtering"""
    def processor(logger, method_name, event_dict):
        event_dict["service"] = service_name
        event_dict["environment"] = ENVIRONMENT
        return event_dict
    return processor


def get_logger(name: Optional[str] = None) -> structlog.BoundLogger:
    """
    Get a logger instance, optionally bound to a specific module/component.

    Args:
        name: Optional name for the logger (e.g., module name)

    Returns:
        structlog logger instance
    """
    logger = structlog.get_logger()
    if name:
        logger = logger.bind(component=name)
    return logger


# What to log at each level:
#
# DEBUG (development only):
#   - Detailed variable values
#   - SQL queries
#   - Request/response bodies
#
# INFO (staging + production):
#   - Request received/completed (method, path, status, duration)
#   - User actions (login, signup, task created)
#   - Business events (family created, task assigned)
#   - Celery task started/completed
#
# WARNING:
#   - Slow requests (>2s)
#   - Retry attempts
#   - Deprecated feature usage
#
# ERROR:
#   - All exceptions (with user_message and technical_message)
#   - Failed external API calls
#   - Database errors
#   - Authentication failures
