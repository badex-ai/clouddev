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





@router.post("/checklist")
async def add_checklist_item_route(req: ChecklistItem= Body(...), db: Session = Depends(get_db)):
    return await add_checklist_item(req)



# admin middleware here

@router.post("/delete")
async def delete_task_route(req: TaskRequest= Body(...)):
    return await delete_task(req)




