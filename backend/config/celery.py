import os
import sys
import time
from celery import Celery
from celery.signals import task_prerun, task_postrun, task_failure, task_retry
from dotenv import load_dotenv

# Only load .env file when running locally (not in Docker)
if not os.getenv("DOCKER_CONTAINER"):
    load_dotenv()

# Setup logging for Celery
from config.logging import setup_logging, get_logger
setup_logging(service_name="kaban-celery")
logger = get_logger("celery")


def create_celery_app():
    """
    Factory function that creates and configures Celery app.
    Called when the module is imported, but config is loaded fresh.
    """
    from .env import get_config
    
    print("[CELERY] Initializing Celery configuration...")
    
    try:
        config = get_config()
        print("[CELERY] Config retrieved successfully")
    except Exception as e:
        print(f"[CELERY] ERROR in get_config(): {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    broker_url = config.get("celery_broker_url")
    result_backend = config.get("celery_result_backend")
    
    # Validate before creating app
    if not broker_url:
        print("[CELERY] ERROR: broker_url is empty!")
        sys.exit(1)
    
    if not result_backend:
        print("[CELERY] ERROR: result_backend is empty!")
        sys.exit(1)
    
    logger.info(
        "celery_config",
        broker=broker_url.split('@')[-1] if '@' in broker_url else broker_url,
        backend=result_backend.split('@')[-1] if '@' in result_backend else result_backend,
    )
    
    # Create app with validated URLs
    app = Celery(
        "kabancelery",
        broker=broker_url,
        backend=result_backend,
    )
    
    app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
    )
    
    return app


# Create the app
celery_app = create_celery_app()

# Import tasks AFTER app is created
from controllers import tasks


# ============================================================================
# CELERY WORKER TRACING INITIALIZATION
# ============================================================================
# IMPORTANT: For prefork workers (Celery default), OpenTelemetry MUST be
# initialized in each worker process using the worker_process_init signal.
# This is required because:
# 1. BatchSpanProcessor uses threading
# 2. Child processes inherit parent memory but not thread state
# 3. Each process needs its own tracer provider instance
# ============================================================================

def _init_celery_tracing(*args, **kwargs):
    """
    Initialize OpenTelemetry tracing in each Celery worker process.
    Called by worker_process_init signal for each worker process.

    This ensures proper tracing in prefork worker pool model.
    """
    from config.tracing import setup_celery_tracing

    print(f"[CELERY] Initializing tracing in worker process PID={os.getpid()}")
    setup_celery_tracing()


# Connect the initialization function to worker_process_init signal
# weak=False ensures the function isn't garbage collected
try:
    from celery.signals import worker_process_init

    worker_process_init.connect(_init_celery_tracing, weak=False)
    logger.info("celery_tracing_connected")
except ImportError as e:
    logger.error("celery_tracing_failed", error=str(e))


# ============================================================================
# CELERY TASK LIFECYCLE LOGGING
# ============================================================================
# Log task events for CloudWatch monitoring
# ============================================================================

# Store task start times for duration calculation
_task_start_times = {}


@task_prerun.connect
def task_started(task_id, task, args, kwargs, **kw):
    """Log when a task starts"""
    _task_start_times[task_id] = time.time()
    logger.info(
        "task_started",
        task_id=task_id,
        task_name=task.name,
    )


@task_postrun.connect
def task_completed(task_id, task, args, kwargs, retval, state, **kw):
    """Log when a task completes successfully"""
    start_time = _task_start_times.pop(task_id, None)
    duration_ms = round((time.time() - start_time) * 1000, 2) if start_time else None

    logger.info(
        "task_completed",
        task_id=task_id,
        task_name=task.name,
        state=state,
        duration_ms=duration_ms,
    )


@task_failure.connect
def task_failed(task_id, exception, args, kwargs, traceback, einfo, **kw):
    """Log when a task fails"""
    start_time = _task_start_times.pop(task_id, None)
    duration_ms = round((time.time() - start_time) * 1000, 2) if start_time else None

    logger.error(
        "task_failed",
        task_id=task_id,
        error=str(exception),
        error_type=type(exception).__name__,
        duration_ms=duration_ms,
    )


@task_retry.connect
def task_retrying(request, reason, einfo, **kw):
    """Log when a task is being retried"""
    logger.warning(
        "task_retry",
        task_id=request.id,
        task_name=request.task,
        retry_count=request.retries,
        reason=str(reason),
    )