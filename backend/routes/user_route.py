from fastapi import APIRouter, Body, Request,Depends
from config.db import get_db
from sqlalchemy.orm import Session
from controllers.auth_controller import  signup, logout,sendVerificationEmail
from schemas.schemas import SignupRequest, EmailVerificationRequest,UserRequest,FamilyRequest
from controllers.user_controller import get_user, get_user_family



router = APIRouter()

@router.post("/me")
async def get_user_route(req: UserRequest = Body(...)):
   print("this the request because the request reached here", req)
   return await get_user(req)


@router.post("/family")
async def get_user_family_route(req: FamilyRequest = Body(...)):
   return await get_user_family(req)


