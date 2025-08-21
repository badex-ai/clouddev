from fastapi import APIRouter, Body, Request,Depends
from config.db import get_db
from sqlalchemy.orm import Session
from controllers.auth_controller import  signup, logout,sendVerificationEmail
from schemas.schemas import SignupRequest, EmailVerificationRequest,UserRequest,FamilyRequest,CreateMemberRequest
from controllers.user_controller import get_user, get_user_family, create_family_member



router = APIRouter()

@router.post("/me")
async def get_user_route(req: UserRequest = Body(...), db: Session = Depends(get_db)):
   print("this the request because the request reached here", req)
   return await get_user(req,db)

@router.post("/new")
async def create_user_route(req: CreateMemberRequest  = Body(...), db: Session = Depends(get_db)):
   return await create_family_member(req,db)


@router.post("/family")
async def get_user_family_route(req: FamilyRequest = Body(...),db: Session = Depends(get_db)):
   return await get_user_family(req,db)


