import os
from dotenv import load_dotenv
from fastapi import HTTPException, Depends
from datetime import datetime, time,timezone
from sqlalchemy.orm import joinedload
from schemas.schemas import FamilyUsers

from models.models import Family
from config.db import get_db

load_dotenv()


async def get_family(id , db) :
    print('this is the request',id)

    family= db.query(Family).options(joinedload(Family.users)).filter(Family.id == id).first() 

    if not family:  
        raise HTTPException(status_code=404, detail="Family not found")
    
    return family



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
