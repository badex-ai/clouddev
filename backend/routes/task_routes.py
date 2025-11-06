from fastapi import APIRouter,Body,Depends, status
from typing import List
from controllers.task_controller import  update_checklist_item_state, update_task, delete_task, add_checklist_item,create_task, delete_checklist_item
from schemas.schemas import TaskUpdate, ChecklistItem,TaskResponse,TaskCreate
from sqlalchemy.orm import Session
from config.db import get_db
import logging


logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task_route(
    req: TaskCreate = Body(...), 
    db: Session = Depends(get_db)
) -> TaskResponse:
    logger.info(f"Creating task for family: {req.family_id}")
    return await create_task(req, db)


@router.delete("/{task_id}/checklist/{checklist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_checklist_item_route(
    task_id: str, 
    checklist_id: str, 
    db: Session = Depends(get_db)
) -> None:
    logger.info(f"Deleting checklist item: {checklist_id} from task: {task_id}")
    return await delete_checklist_item(task_id, checklist_id, db)


@router.post("/{task_id}/checklist", response_model=ChecklistItem, status_code=status.HTTP_201_CREATED)
async def add_checklist_item_route(
    task_id: str, 
    req: ChecklistItem = Body(...), 
    db: Session = Depends(get_db)
) -> ChecklistItem:
    logger.info(f"Adding checklist item to task: {task_id}")
    return await add_checklist_item(task_id, req, db)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_route(
    task_id: str, 
    db: Session = Depends(get_db)
) -> None:
    logger.info(f"Deleting task: {task_id}")
    return await delete_task(task_id, db)





