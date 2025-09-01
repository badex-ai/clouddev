from fastapi import APIRouter,Body,params,Depends
from typing import List
from controllers.task_controller import  update_checklist_item_state, update_task, delete_task, add_checklist_item,create_task
from schemas.schemas import TaskUpdate, ChecklistItem, TaskRequest,TaskResponse,TaskCreate
from sqlalchemy.orm import Session
from config.db import get_db


router = APIRouter()

@router.post("/")
async def create_task_route(req: TaskCreate= Body(...),db: Session = Depends(get_db)):
    print("this is the request from the create task",req)
    return await create_task(req,db)





@router.post("/{taskId}")
async def add_checklist_item_route(taskId, req: ChecklistItem= Body(...), db: Session = Depends(get_db)):
    print (taskId,req.title )
    return await add_checklist_item(taskId,req,db)



# admin middleware here

@router.delete("/{task_id}")
async def delete_task_route(task_id,db: Session = Depends(get_db)):
    return await delete_task(task_id,db)




