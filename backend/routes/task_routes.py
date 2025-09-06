from fastapi import APIRouter,Body,Depends
from typing import List
from controllers.task_controller import  update_checklist_item_state, update_task, delete_task, add_checklist_item,create_task, delete_checklist_item
from schemas.schemas import TaskUpdate, ChecklistItem, TaskRequest,TaskResponse,TaskCreate
from sqlalchemy.orm import Session
from config.db import get_db


router = APIRouter()

@router.post("/")
async def create_task_route(req: TaskCreate= Body(...),db: Session = Depends(get_db)):
    print("this is the request from the create task",req)
    return await create_task(req,db)




@router.delete("/{taskId}/checklist/{checklistId}")
async def delete_checlist_item_router(taskId,checklistId, db: Session= Depends(get_db)):
    print('this is it ',taskId )
    print('this is checklist', checklistId)
    return await delete_checklist_item(taskId,checklistId,db)

@router.post("/{taskId}/checklist")
async def add_checklist_item_route(taskId, req: ChecklistItem= Body(...), db: Session = Depends(get_db)):
    return await add_checklist_item(taskId,req,db)

# admin middleware here

@router.delete("/{task_id}")
async def delete_task_route(task_id,db: Session = Depends(get_db)):
    return await delete_task(task_id,db)





