from fastapi import APIRouter
from controllers.auth_controller import login, signup, logout
from schemas.schemas import LoginRequest, SignupRequest, LogoutRequest

router = APIRouter()
@router.post("/login")
async def login_route(req: LoginRequest):
    return login(req)


@router.post("/signup")
async def signup_route(req: SignupRequest):
    return signup(req)

@router.post("/logout")
async def logout_route(req: LogoutRequest):
    return logout(req)