from fastapi import APIRouter,Body, Depends
from controllers.family_controller import get_family
from sqlalchemy.orm import Session
from config.db import get_db
import logging
from controllers.user_controller import delete_user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/{id}")
async def get_family_route(id, db: Session = Depends(get_db)):
 
    return await get_family(id, db)

@router.delete("/{id}")
async def delete_family_member(id, db: Session = Depends(get_db)):
     return await delete_user(id,db)

