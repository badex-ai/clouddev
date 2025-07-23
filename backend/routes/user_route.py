from fastapi import APIRouter, Body, Request,Depends
from config.db import get_db
from sqlalchemy.orm import Session
from controllers.auth_controller import  signup, logout,sendVerificationEmail
from schemas.schemas import SignupRequest, LogoutRequest,EmailVerificationRequest,UserRequest
from controllers.user_controller import get_user



router = APIRouter()

@router.post("/me")
async def get_user_route(req: UserRequest = Body(...), db: Session = Depends(get_db)):
   print("Request received in get_user_route:", req)
   return await get_user(req,db)


