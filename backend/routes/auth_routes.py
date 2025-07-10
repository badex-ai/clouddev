from fastapi import APIRouter
from controllers.auth_controller import login, signup, logout

router = APIRouter()
@router.post("/login",login)
@router.post("/signup", signup)
@router.post("/logout", logout)