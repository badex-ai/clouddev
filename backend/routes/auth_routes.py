from fastapi import APIRouter
from controllers.auth_controller import  signup, logout,sendVerificationEmail
from schemas.schemas import SignupRequest, LogoutRequest,EmailVerificationRequest

router = APIRouter()


@router.post("/signup")
async def signup_route(req: SignupRequest):
    return await signup(req)

@router.post("/emailVerification")
async def email_verification_route(req: EmailVerificationRequest):
    return await sendVerificationEmail(req)

@router.post("/logout")
async def logout_route(req: LogoutRequest):
    return await logout(req)