"""
Celery worker entry point.
This file imports the celery app and all tasks, then starts the worker.
"""
from config.celery import celery_app

# Import all task modules to register them with Celery
import controllers.tasks  # This registers the tasks

# This is just for starting the worker
if __name__ == '__main__':
    celery_app.start()