from fastapi import APIRouter,Body, Request,Depends
from controllers.auth_controller import  signup, logout
from schemas.schemas import SignupRequest,EmailVerificationRequest
from config.db import get_db
from sqlalchemy.orm import Session



router = APIRouter()


@router.post("/signup")
async def signup_route(req: SignupRequest= Body(...), db: Session = Depends(get_db)):

    print(req, "ti is aut request" )
    return await signup(req,db)

# @router.post("/emailVerification")
# async def email_verification_route(req: EmailVerificationRequest= Body(...)):
#     return await sendVerificationEmail(req)