from fastapi import APIRouter, Body, Request,Depends
from config.db import get_db
from sqlalchemy.orm import Session
from controllers.auth_controller import  signup, logout,sendVerificationEmail
from schemas.schemas import SignupRequest, EmailVerificationRequest,UserRequest,FamilyRequest,CreateMemberRequest
from controllers.user_controller import get_user, create_family_member,delete_user
from schemas.schemas import UserStatusRequest



router = APIRouter()

@router.post("/me")
async def get_user_route(req: UserRequest = Body(...), db: Session = Depends(get_db)):
   print("this the request because the request reached here", req)
   return await get_user(req,db)

@router.post("/new")
async def create_user_route(req: CreateMemberRequest  = Body(...), db: Session = Depends(get_db)):
   return await create_family_member(req,db)



@router.patch("/{id}/deactivate")
async def delete_family_member(id, db: Session = Depends(get_db)):
     return  delete_user(id,db)

# @router.patch("/{id}")
# async def change_family_member_status_route(id, db: Session = Depends(get_db)):
#      return await change_family_member_status(id, db)