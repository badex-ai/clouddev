from fastapi import APIRouter,Body, Request,Depends
from controllers.task_controller import  get_tasks,update_checklist_item_state, update_task, delete_task, add_checklist_item,create_task
from schemas.schemas import TaskUpdate,TaskCreate, ChecklistItem, GetTasks, TaskRequest


router = APIRouter()


@router.get("/")
async def get_tasks(req: GetTasks= Body(...)):
    await get_tasks(req)


@router.post("/checklist")
async def add_checklist_item(req: ChecklistItem= Body(...)):
    await add_checklist_item(req)



# admin middleware here

@router.post("/")
async def create_task(req: TaskCreate= Body(...)):
    await create_task(req)

@router.post("/delete")
async def delete_task(req: TaskRequest= Body(...)):
    await delete_task(req)
