import os
import sys
import time
from celery import Celery
from celery.signals import task_prerun, task_postrun, task_failure, task_retry
from dotenv import load_dotenv

if not os.getenv("DOCKER_CONTAINER"):
    load_dotenv()

from config.logging import setup_logging, get_logger
setup_logging(service_name="kaban-celery")
logger = get_logger("celery")


def create_celery_app():
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


celery_app = create_celery_app()

from controllers import tasks


def _init_celery_tracing(*args, **kwargs):
    from config.tracing import setup_celery_tracing

    print(f"[CELERY] Initializing tracing in worker process PID={os.getpid()}")
    setup_celery_tracing()


try:
    from celery.signals import worker_process_init

    worker_process_init.connect(_init_celery_tracing, weak=False)
    logger.info("celery_tracing_connected")
except ImportError as e:
    logger.error("celery_tracing_failed", error=str(e))


_task_start_times = {}


@task_prerun.connect
def task_started(task_id, task, args, kwargs, **kw):
    _task_start_times[task_id] = time.time()
    logger.info(
        "task_started",
        task_id=task_id,
        task_name=task.name,
    )


@task_postrun.connect
def task_completed(task_id, task, args, kwargs, retval, state, **kw):
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
    logger.warning(
        "task_retry",
        task_id=request.id,
        task_name=request.task,
        retry_count=request.retries,
        reason=str(reason),
    )