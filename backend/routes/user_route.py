from fastapi import APIRouter, Body, Request,Depends
from config.db import get_db
from sqlalchemy.orm import Session
from controllers.auth_controller import  signup, logout,sendVerificationEmail
from schemas.schemas import SignupRequest, EmailVerificationRequest,UserRequest
from controllers.user_controller import get_user



router = APIRouter()

@router.post("/me")
async def get_user_route(req: UserRequest = Body(...)):
   print("Request received in get_user_route:", req)
   return await get_user(req)


