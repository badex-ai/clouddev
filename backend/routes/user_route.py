from fastapi import APIRouter, Body, Request,Depends
from config.db import get_db
from sqlalchemy.orm import Session
from controllers.auth_controller import  signup, logout
from schemas.schemas import SignupRequest, EmailVerificationRequest,UserRequest,FamilyRequest,CreateMemberRequest
from controllers.user_controller import get_user, create_family_member, deactivate_user,reactivate_user
from schemas.schemas import UserStatusRequest
import logging
from config.env import get_config



router = APIRouter()

@router.post("/me")
async def get_user_route(req: UserRequest = Body(...), db: Session = Depends(get_db)):
   return await get_user(req,db)

@router.post("/new")
async def create_user_route(req: CreateMemberRequest  = Body(...), db: Session = Depends(get_db)):
   return await create_family_member(req,db)



@router.patch("/{id}/deactivate")
async def deactivate_family_member(id, db: Session = Depends(get_db)):
     return  deactivate_user(id,db)

# @router.delete("/{id}")
# async def delete_user(id, db: Session = Depends(get_db)):
#      return await delete_user(id,db)

@router.patch("/{id}/activate")
async def reactivate_family_member(id, db: Session = Depends(get_db)):
     return  reactivate_user(id,db)