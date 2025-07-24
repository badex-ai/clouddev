import os
from dotenv import load_dotenv
from fastapi import HTTPException, Depends
import httpx 
from sqlalchemy.orm import Session
from config.db import SessionLocal 
from backend.models.models import Task
from config.db import get_db
from schemas.schemas import (
    UserCreate, UserResponse, UserUpdate,
    TaskCreate, TaskResponse, GetTasks,
    TaskUpdate, ChecklistItem
)

load_dotenv()

db = SessionLocal()

async def create_task(request: TaskCreate) -> TaskResponse:

  
    try:
        new_task = Task(
            title=request.title,
            description=request.description,
            owner_id=request.owner_id
        )
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        return TaskResponse.from_orm(new_task)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating task: {str(e)}")
    finally :
        db.close()


async def get_tasks(req: GetTasks) -> list[TaskResponse]:
    try: 
        tasks = db.query(Task).filter(Task.date == req.date, Task.family == req.family).all()
        
        if not tasks:
            raise HTTPException(status_code=404, detail="No tasks found")
    
        return [TaskResponse.from_orm(task) for task in tasks]

    except Exception as e:
        raise HTTPException(status_code= 500, detail= "something went wrong")
    finally:
        db.close()

async def update_task(req: TaskUpdate)  -> TaskResponse:
    try: 
        task = db.query(Task).filter(Task.id == req.id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        task.title = req.title
        task.description = req.description
        task.Checklist = req.checklist
        db.commit()
        db.refresh(task)
        return TaskResponse.from_orm(task)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating task: {str(e)}")
    finally: 
        db.close
    

async def delete_task(task_id: int) -> None:
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        db.delete(task)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting task: {str(e)}")
    finally: 
        db.close
    
async def update_checklist_item_state(task_id: int, item_id: str) -> TaskResponse:
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task.update_checklist_item(item_id=item_id, completed=True)
        db.commit()
        db.refresh(task)
        return TaskResponse.from_orm(task)
    
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error marking item as completed: {str(e)}")
    finally: 
        db.close
    
# async def unmark_checklist_item_completed(task_id: int, item_id: str) -> TaskResponse:
#     try:
#         task = db.query(Task).filter(Task.id == task_id).first()
#         if not task:
#             raise HTTPException(status_code=404, detail="Task not found")
        
#         task.update_checklist_item(item_id=item_id, completed=False)
#         db.commit()
#         db.refresh(task)
#         return TaskResponse.from_orm(task)
    
#     except ValueError as ve:
#         raise HTTPException(status_code=400, detail=str(ve))
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=f"Error unmarking item as completed: {str(e)}")
#     finally:
#         db.close()
    

async def add_checklist_item(req:ChecklistItem) -> TaskResponse:
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task.add_checklist_item(item_id=req.id, title=req.title, completed=req.completed)
        db.commit()
        db.refresh(task)
        return TaskResponse.from_orm(task)
    
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error adding checklist item: {str(e)}")
    finally:
        db.close()

# async def delete_checklist_item(req: ChecklistItem) -> TaskResponse:


