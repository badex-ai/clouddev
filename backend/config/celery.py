import os
import sys
from celery import Celery
from dotenv import load_dotenv
from .env import get_config



load_dotenv()

print(os.getenv("CELERY_BROKER_URL"), "tis it te broker url ")
print(os.getenv("CELERY_RESULT_BACKEND"), "tis it te result backend")



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


if not result_backend or result_backend == "":
    sys.exit(1)



# Initialize Celery with explicit URLs
celery_app = Celery(
    "kabancelery",
    broker=config["celery_broker_url"],
    backend=config["celery_result_backend"],
)

print(f"[CELERY] Celery app initialized successfully")
print(f"[CELERY] Broker URL from app: {celery_app.conf.broker_url}")
print(f"[CELERY] Result backend from app: {celery_app.conf.result_backend}")

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Import tasks after Celery app is configured
from controllers import tasks