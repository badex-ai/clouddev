import os
from dotenv import load_dotenv
from fastapi import HTTPException, status
from datetime import datetime, time, timezone
from sqlalchemy.orm import joinedload, contains_eager
from sqlalchemy import and_, or_
from sqlalchemy.exc import SQLAlchemyError
from schemas.schemas import FamilyUsers
from models.models import Family, User, Task
from config.db import get_db
from schemas.schemas import (
    UserCreate, UserResponse, UserUpdate,
    TaskCreate, TaskResponse, GetTasks,
    TaskUpdate, ChecklistItem, DeleteTask,
    TaskStatus, UserRole
)
# from utils.error_handler import ErrorHandler
from structlog import get_logger

load_dotenv()

logger = get_logger()

# -> Family:
def get_family_by_id(db, family_id: str): 
    family = (
        db.query(Family)
        .options(joinedload(Family.users))
        .filter(Family.public_id == family_id)
        .first()
    )
    
    if not family:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Family not found"
        )
    
    return family


def parse_date_to_utc_range(date_str: str) -> tuple[datetime, datetime]:
    parsed_date = datetime.fromisoformat(date_str).date()
    start_of_day = datetime.combine(parsed_date, time.min).replace(tzinfo=timezone.utc)
    end_of_day = datetime.combine(parsed_date, time.max).replace(tzinfo=timezone.utc)
    return start_of_day, end_of_day


def query_tasks_for_date(db, family_id: str, start_of_day: datetime, end_of_day: datetime) -> list[Task]:
    return db.query(Task).filter(
        and_(
            Task.family_id == family_id,
            Task.is_deleted == False,
            or_(
                and_(
                    Task.created_at >= start_of_day,
                    Task.created_at <= end_of_day
                ),
                and_(
                    Task.due_date >= start_of_day,
                    Task.status != 'completed'
                )
            )
        )
    ).order_by(Task.due_date.asc()).all()


async def get_family(id: str, db):
    logger.info("get_family_started", family_id=id)
    
    try:
        family = get_family_by_id(db, id)
        logger.info("get_family_completed", family_id=id)
        return family
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        ErrorHandler.handle_sqlalchemy_error(e, {"family_id": id})
    except Exception as e:
        ErrorHandler.handle_generic_error(e, {"family_id": id})


async def get_family_task_for_date(family_id: str, date: str, db) -> list[TaskResponse]: 
    logger.info("get_family_task_for_date_started", family_id=family_id, date=date)
    
    
    start_of_day, end_of_day = parse_date_to_utc_range(date)
    
    logger.info(
        "date_range_parsed",
        start_of_day=start_of_day.isoformat(),
        end_of_day=end_of_day.isoformat()
    )
    
    tasks = query_tasks_for_date(db, family_id, start_of_day, end_of_day)

    if not tasks:
        logger.info("no_tasks_found", family_id=family_id, date=date)
        return []
    
    logger.info("get_family_task_for_date_completed", family_id=family_id, task_count=len(tasks))
    return [TaskResponse.model_validate(task) for task in tasks]
        

        
  


