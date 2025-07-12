from fastapi import APIRouter
from controllers.auth_controller import login, signup, logout
from schemas.schemas import LoginRequest, SignupRequest, LogoutRequest

router = APIRouter()
@router.post("/login")
async def login_route(login_request: LoginRequest):
    return login(login_request)


@router.post("/signup")
async def signup_route(signup_request: SignupRequest):
    return signup(signup_request)

@router.post("/logout")
async def logout_route(logout_request: LogoutRequest):
    return logout(logout_request)