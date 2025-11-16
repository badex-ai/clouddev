import os
from celery import Celery
from dotenv import load_dotenv
from config.env import get_config

load_dotenv()
config = get_config()

celery_app = Celery(
    "tasks",
    broker=config["celery_broker_url"],
    backend=config["celery_result_backend"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
