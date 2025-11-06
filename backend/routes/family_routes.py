from fastapi import APIRouter,Body, Depends
from controllers.family_controller import get_family, get_family_task_for_date
from sqlalchemy.orm import Session
from config.db import get_db
from typing import List
import logging
from schemas.schemas import (
 TaskResponse,  FamilyResponse, FamilyUsers, FamilyDetails
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/{family_id}", response_model=FamilyUsers)
async def get_family_route(
    family_id: str, 
    db: Session = Depends(get_db)
) -> FamilyUsers:
    logger.info(f"Fetching family details: {family_id}")
    return await get_family(family_id, db)


@router.get("/{family_id}/tasks", response_model=List[TaskResponse])
async def get_tasks_route(
    family_id: str, 
    date: str, 
    db: Session = Depends(get_db)
) -> List[TaskResponse]:
    logger.info(f"Fetching tasks for family: {family_id} on date: {date}")
    return await get_family_task_for_date(family_id, date, db)

