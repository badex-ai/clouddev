import os
from dotenv import load_dotenv
from fastapi import HTTPException, Depends
from datetime import datetime, time,timezone
from sqlalchemy.orm import joinedload,contains_eager
from schemas.schemas import FamilyUsers

from models.models import Family,User
from config.db import get_db
from schemas.schemas import (
    UserCreate, UserResponse, UserUpdate,
    TaskCreate, TaskResponse, GetTasks,
    TaskUpdate, ChecklistItem, DeleteTask,
    TaskStatus, UserRole
)
from models.models import Task
from sqlalchemy import and_ , or_ 



load_dotenv()


async def get_family(id, db):
    from sqlalchemy.orm import joinedload
    
    family = (
        db.query(Family)
        .options(joinedload(Family.users))
        .filter(Family.public_id == id)
        .first()
    )
    
    if not family:
        raise HTTPException(status_code=404, detail="Family not found")
    
    return family


async def get_family_task_for_date(family_id, date,db) -> list[TaskResponse]:

  

  
    parsed_date = datetime.fromisoformat(date).date()
    start_of_day = datetime.combine(parsed_date, time.min).replace(tzinfo=timezone.utc)
    end_of_day = datetime.combine(parsed_date, time.max).replace(tzinfo=timezone.utc)

    print(f"Start of day: {start_of_day}, End of day: {end_of_day}")
   
    try: 
        tasks = db.query(Task).filter(
            and_(
                Task.family_id == family_id,
                Task.is_deleted == False,
                or_(
                    # Tasks created on this date
                    and_(
                        Task.created_at >= start_of_day,
                        Task.created_at <= end_of_day
                    ),
                    # Overdue/upcoming tasks that are not completed
                    and_(
                        Task.due_date >= start_of_day,
                        Task.status != 'completed'
                    )
                )
            )
        ).order_by(Task.due_date.asc()).all()

        print(f"Retrieved tasks: {tasks}")
       
      
    
        return [TaskResponse.model_validate(task) for task in tasks]

    except Exception as e:
        print(f"Error retrieving tasks: {e}")
        raise HTTPException(status_code= 500,detail= "something went wrong")
 



# async def get_user_family(id, db)-> FamilyUsers:
#     # print(f"Family Object: ",req)
#     try:
#         family = db.query(Family).options(joinedload(Family.users)).filter(Family.id == id).first()
        
#         print(f"User Email: {family.users}")
    
#         if not family:
#             raise HTTPException(status_code=404, detail="family not found")
        
#         return FamilyUsers.model_validate(family)
#     except Exception as e:
#          raise HTTPException(status_code=500, detail=f"Error getting family: {str(e)}")
