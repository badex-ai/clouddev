from fastapi import APIRouter,Body
from typing import List
from controllers.task_controller import  get_tasks,update_checklist_item_state, update_task, delete_task, add_checklist_item,create_task
from schemas.schemas import TaskUpdate,TaskCreate, ChecklistItem, GetTasks, TaskRequest,TaskResponse


router = APIRouter()


@router.post("/date")
async def get_tasks_route(req :GetTasks = Body(...)):
    print(req)
    return await get_tasks(req)


@router.post("/checklist")
async def add_checklist_item_route(req: ChecklistItem= Body(...)):
    return await add_checklist_item(req)



# admin middleware here

@router.post("/delete")
async def delete_task_route(req: TaskRequest= Body(...)):
    return await delete_task(req)

# @router.post("/")
# async def create_task(req: TaskCreate= Body(...)):
#     await create_task(req)


