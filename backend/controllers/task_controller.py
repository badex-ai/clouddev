import os
from dotenv import load_dotenv
from fastapi import HTTPException, Depends
import httpx 
from datetime import datetime, time,timezone
from sqlalchemy import and_  
from config.db import SessionLocal 
from models.models import Task
from config.db import get_db
from schemas.schemas import (
    UserCreate, UserResponse, UserUpdate,
    TaskCreate, TaskResponse, GetTasks,
    TaskUpdate, ChecklistItem, DeleteTask
)

load_dotenv()

db = SessionLocal()

async def create_task(req: TaskCreate) -> TaskResponse:

  
    try:
        new_task = Task(
            title=req.title,
            description=req.description,
            creator_id=req.creator_id,
            status= req.status,
            assignee_id= req.assignee_id,
            due_date= req.due_date
        )
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        return TaskResponse.model_validate(new_task)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating task: {str(e)}")
    finally :
        db.close()


async def get_tasks(req: GetTasks) -> list[TaskResponse]:

    print(req)
    start_of_day = datetime.combine(req.date, time.min).replace(tzinfo=timezone.utc)
    end_of_day = datetime.combine(req.date, time.max).replace(tzinfo=timezone.utc)
    print(start_of_day)
    print(end_of_day)
    try: 
        tasks = db.query(Task).filter( and_(
            Task.created_at >= start_of_day,
            Task.created_at <= end_of_day,
            Task.family_id == req.family_id
        )).all()
        print(tasks)
      
    
        return [TaskResponse.model_validate(task) for task in tasks]

    except Exception as e:
        raise HTTPException(status_code= 500, detail= "something went wrong")
    finally:
        db.close()
    # return []

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
    

async def delete_task(req: DeleteTask ) -> None:
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
        return TaskResponse.model_validate(task)(task)
    
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error adding checklist item: {str(e)}")
    finally:
        db.close()

# async def delete_checklist_item(req: ChecklistItem) -> TaskResponse:



