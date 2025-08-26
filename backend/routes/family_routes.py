from fastapi import APIRouter,Body, Depends
from controllers.family_controller import get_family, get_family_tasks_for_date
from sqlalchemy.orm import Session
from config.db import get_db
import logging
from schemas.schemas import (
    UserCreate, UserResponse, UserUpdate,
    TaskCreate, TaskResponse, GetTasks,
    TaskUpdate, ChecklistItem, DeleteTask,
    TaskStatus, UserRole
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/{family_id}")
async def get_family_route(family_id, db: Session = Depends(get_db)):
 
    return await get_family(family_id, db)


@router.get("/{family_id}/tasks")
async def get_tasks_route(family_id, date, db: Session = Depends(get_db)):

    return await get_family_tasks_for_date(family_id, date, db)


