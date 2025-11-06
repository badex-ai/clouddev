import os
from dotenv import load_dotenv
from fastapi import HTTPException, status
import httpx 
from datetime import datetime, time, timezone
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError
from config.db import SessionLocal 
from models.models import Task
from config.db import get_db
from config.env import get_config
from schemas.schemas import (
    UserCreate, UserResponse, UserUpdate,
    TaskCreate, TaskResponse,
    TaskUpdate, ChecklistItem, DeleteTask,
    TaskStatus, UserRole
)
from utils.error_handler import AppError, ErrorCode
from structlog import get_logger

load_dotenv()

logger = get_logger()
config = get_config()

auth0_domain = config["auth0_domain"]
auth0_client_id = config["auth0_client_id"]
auth0_m2m_client_id = config["auth0_m2m_client_id"]
auth0_m2m_client_secret = config["auth0_m2m_client_secret"]


def get_task_by_id(db, task_id: str) -> Task:
    task = db.query(Task).filter(Task.public_id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task


def create_task_record(db, req: TaskCreate) -> Task:
    new_task = Task(
        title=req.title,
        description=req.description,
        creator_id=req.creator_id,
        status=TaskStatus.initialised.value,
        assignee_id=req.assignee_id,
        family_id=req.family_id,
        due_date=req.due_date
    )
    db.add(new_task)
    db.flush()
    logger.info("task_created", task_id=new_task.public_id)
    return new_task


def update_task_fields(task: Task, req: TaskUpdate) -> Task:
    if req.title is not None:
        task.title = req.title
    if req.description is not None:
        task.description = req.description
    if req.checklist is not None:
        task.Checklist = req.checklist
    return task


def mark_task_deleted(task: Task) -> Task:
    task.is_deleted = True
    return task


async def create_task(req: TaskCreate, db) -> TaskResponse:
    logger.info("create_task_started", title=req.title)
    
    try:
        new_task = create_task_record(db, req)
        db.commit()
        
        logger.info("create_task_completed", task_id=new_task.public_id)
        return TaskResponse.model_validate(new_task)
    except Exception:
        db.rollback()
        raise    



async def update_task(req: TaskUpdate, db) -> TaskResponse:
    logger.info("update_task_started", task_id=req.id)
    
    try:
        task = get_task_by_id(db, req.id)
        task = update_task_fields(task, req)
        db.flush()
        db.commit()
        
        logger.info("update_task_completed", task_id=req.id)
        return TaskResponse.model_validate(task)
        
    except Exception:
        db.rollback()
        raise


async def delete_task(task_id: str, db) -> None:
    logger.info("delete_task_started", task_id=task_id)
    
    try:
        task = get_task_by_id(db, task_id)
        task = mark_task_deleted(task)
        db.flush()
        db.commit()
        
        logger.info("delete_task_completed", task_id=task_id)
        
    except Exception:
        db.rollback()
        raise


async def update_checklist_item_state(task_id: str, item_id: str, db):
    logger.info("update_checklist_item_started", task_id=task_id, item_id=item_id)
    
    try:
        task = get_task_by_id(db, task_id)
        task.update_checklist_item(item_id=item_id, completed=True)
        db.flush()
        db.commit()
        
        logger.info("update_checklist_item_completed", task_id=task_id, item_id=item_id)
        return TaskResponse.model_validate(task)
        
    except ValueError as e:
        # Business logic error - needs specific handling
        db.rollback()
        raise AppError(
            code=ErrorCode.BAD_REQUEST,
            status_code=status.HTTP_400_BAD_REQUEST,
            technical_message=f"Checklist item validation failed: {str(e)}",
            user_message=str(e),  # ValueError already has user-friendly message
            is_operational=True,
            details={"task_id": task_id, "item_id": item_id}
        )
    except Exception:
        db.rollback()
        raise


# async def unmark_checklist_item_completed(task_id: str, item_id: str, db) -> TaskResponse:
#     logger.info("unmark_checklist_item_started", task_id=task_id, item_id=item_id)
    
#     try:
#         task = get_task_by_id(db, task_id)
#         task.update_checklist_item(item_id=item_id, completed=False)
#         db.flush()
#         db.commit()
        
#         logger.info("unmark_checklist_item_completed", task_id=task_id, item_id=item_id)
#         return TaskResponse.model_validate(task)
        
#     except ValueError as e:
#         logger.error("checklist_item_validation_error", task_id=task_id, item_id=item_id, error=str(e))
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=str(e)
#         )
#     except HTTPException:
#         raise
#     except SQLAlchemyError as e:
#         db.rollback()
#         ErrorHandler.handle_sqlalchemy_error(e, {"task_id": task_id, "item_id": item_id})
#     except Exception as e:
#         db.rollback()
#         ErrorHandler.handle_generic_error(e, {"task_id": task_id, "item_id": item_id})


async def add_checklist_item(task_id: str, req: ChecklistItem, db) -> TaskResponse:
    logger.info("add_checklist_item_started", task_id=task_id, item_title=req.title)
    
    try:
        task = get_task_by_id(db, task_id)
        task.add_checklist_item(item_id=req.id, title=req.title, completed=req.completed)
        db.flush()
        db.commit()
        
        logger.info("add_checklist_item_completed", task_id=task_id, item_id=req.id)
        return TaskResponse.model_validate(task)
        
    except ValueError as e:
        db.rollback()
        raise AppError(
            code=ErrorCode.BAD_REQUEST,
            status_code=status.HTTP_400_BAD_REQUEST,
            technical_message=f"Checklist item validation failed: {str(e)}",
            user_message=str(e),
            is_operational=True,
            details={"task_id": task_id}
        )
    except Exception:
        db.rollback()
        raise


async def delete_checklist_item(task_id: str, checklist_id: str, db):
    logger.info("delete_checklist_item_started", task_id=task_id, checklist_id=checklist_id)
    
    try:
        task = get_task_by_id(db, task_id)
        task.remove_checklist_item(checklist_id)
        db.flush()
        db.commit()
        
        logger.info("delete_checklist_item_completed", task_id=task_id, checklist_id=checklist_id)
        return TaskResponse.model_validate(task)
        
    except ValueError as e:
        db.rollback()
        raise AppError(
            code=ErrorCode.BAD_REQUEST,
            status_code=status.HTTP_400_BAD_REQUEST,
            technical_message=f"Checklist item validation failed: {str(e)}",
            user_message=str(e),
            is_operational=True,
            details={"task_id": task_id, "checklist_id": checklist_id}
        )
    except Exception:
        db.rollback()
        raise