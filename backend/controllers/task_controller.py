import os
from dotenv import load_dotenv
from fastapi import HTTPException, Depends
import httpx 
from datetime import datetime, time,timezone
from sqlalchemy import and_  
from config.db import SessionLocal 
from models.models import Task
from config.db import get_db
from config.env import get_config
from schemas.schemas import (
    UserCreate, UserResponse, UserUpdate,
    TaskCreate, TaskResponse,
    TaskUpdate, ChecklistItem, DeleteTask,
    TaskStatus, UserRole
)
import logging
import traceback
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

config = get_config()

auth0_domain = config["auth0_domain"]
auth0_client_id = config["auth0_client_id"]
auth0_m2m_client_id = config["auth0_m2m_client_id"]
auth0_m2m_client_secret = config["auth0_m2m_client_secret"]  # SECRET

db = SessionLocal()

async def create_task(req: TaskCreate,db) -> TaskResponse:
    print('this is the request',req)
    print('this is the request',TaskStatus.initialised.value)
 
  
    try:
        new_task = Task(
            title=req.title,
            description=req.description,
            creator_id=req.creator_id,
            status= TaskStatus.initialised.value,
            assignee_id= req.assignee_id,
            family_id= req.family_id,
            due_date= req.due_date
        )
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        print()
        return TaskResponse.model_validate(new_task)
    except Exception as e:
        db.rollback()
        print('this is the error',e)
        raise HTTPException(status_code=500, detail=f"Error creating task: {str(e)}")
    



async def update_task(req: TaskUpdate,db)  -> TaskResponse:
    try: 
        task = db.query(Task).filter(Task.public_id == req.id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        task.title = req.title
        task.description = req.description
        task.Checklist = req.checklist
        db.commit()
        db.refresh(task)
        return TaskResponse.model_validate(task)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating task: {str(e)}")
  
    


async def delete_task(task_id,db) -> None:
    try:
        task = db.query(Task).filter(Task.public_id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task.is_deleted = True
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting task: {str(e)}")
    

# -> TaskResponse
async def update_checklist_item_state(task_id: int, item_id: str) :
    print(task_id, item_id)
    try:
        task = db.query(Task).filter(Task.public_id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task.update_checklist_item(item_id=item_id, completed=True)
        db.commit()
        db.refresh(task)
        return TaskResponse.model_validate(task)
    
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error marking item as completed: {str(e)}")
    
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
    

async def add_checklist_item(task_id,req:ChecklistItem, db) -> TaskResponse:
    
    try:
        task = db.query(Task).filter(Task.public_id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task.add_checklist_item(item_id=req.id, title=req.title, completed=req.completed)
        db.commit()
        db.refresh(task)
        return TaskResponse.model_validate(task)
    
    except ValueError as ve:

        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        db.rollback()
        print("Error adding checklist item:", e)
        raise HTTPException(status_code=500, detail=f"Error adding checklist item: {str(e)}")

async def delete_checklist_item(task_id,checklistId, db):
    print(task_id)
    try:
        task = db.query(Task).filter(Task.public_id == task_id).first()

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        me =task.remove_checklist_item(checklistId)
        
        db.commit()
        db.refresh(task)
        return TaskResponse.model_validate(task)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        print("Error adding checklist item:", e)
        raise HTTPException(status_code=500, detail=f"Error adding checklist item: {str(e)}")



