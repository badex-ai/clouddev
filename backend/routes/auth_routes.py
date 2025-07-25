from fastapi import APIRouter,Body, Request,Depends
from controllers.auth_controller import  signup, logout,sendVerificationEmail
from schemas.schemas import SignupRequest,EmailVerificationRequest


router = APIRouter()


@router.post("/signup")
async def signup_route(req: SignupRequest= Body(...)):
    return await signup(req)

@router.post("/emailVerification")
async def email_verification_route(req: EmailVerificationRequest= Body(...)):
    return await sendVerificationEmail(req)
