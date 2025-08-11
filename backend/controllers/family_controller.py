import os
from dotenv import load_dotenv
from fastapi import HTTPException, Depends
from datetime import datetime, time,timezone
from sqlalchemy import and_  
from config.db import SessionLocal 
from models.models import Task
from config.db import get_db

load_dotenv()

db = SessionLocal()

async def get_family(req: ) -> TaskResponse:
    print('this is the request',req)
    print('this is the request',TaskStatus.initialised.value)
 
  
    # try:
    #     new_task = Task(
    #         title=req.title,
    #         description=req.description,
    #         creator_id=req.creator_id,
    #         status= TaskStatus.initialised.value,
    #         assignee_id= req.assignee_id,
    #         family_id= req.family_id,
    #         due_date= req.due_date
    #     )
    #     db.add(new_task)
    #     db.commit()
    #     db.refresh(new_task)
    #     return TaskResponse.model_validate(new_task)
    # except Exception as e:
    #     db.rollback()
    #     print('this is the error',e)
    #     raise HTTPException(status_code=500, detail=f"Error creating task: {str(e)}")
    # finally :
    #     db.close()
