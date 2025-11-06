from fastapi import APIRouter, Body, Request,Depends, Header, status
from config.db import get_db
from sqlalchemy.orm import Session
from controllers.auth_controller import  signup, logout
from schemas.schemas import SignupRequest, EmailVerificationRequest,UserRequest,FamilyRequest,CreateMemberRequest, UserResponse, AuthenticatedUserProfile
from controllers.user_controller import get_user, create_family_member, deactivate_user,reactivate_user
from schemas.schemas import UserStatusRequest
import logging
from config.env import get_config



logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/me", response_model=AuthenticatedUserProfile)
async def get_user_route(
    req: UserRequest = Body(...), 
    db: Session = Depends(get_db)
) -> dict:
    logger.info(f"Fetching user details for: {req.user_email}")
    return await get_user(req, db)


@router.post("/new", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user_route(
    req: CreateMemberRequest = Body(...), 
    db: Session = Depends(get_db),
    idempotency_key: str = Header(None, alias="Idempotency-Key")
) -> UserResponse:
    logger.info(f"Creating new family member: {req.email}")
    return await create_family_member(req, db, idempotency_key)


@router.patch("/{user_id}/deactivate", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_family_member_route(
    user_id: str, 
    db: Session = Depends(get_db)
) -> None:
    logger.info(f"Deactivating user: {user_id}")
    deactivate_user(user_id, db)


@router.patch("/{user_id}/activate", status_code=status.HTTP_204_NO_CONTENT)
def reactivate_family_member_route(
    user_id: str, 
    db: Session = Depends(get_db)
) -> None:
    logger.info(f"Reactivating user: {user_id}")
    reactivate_user(user_id, db)
