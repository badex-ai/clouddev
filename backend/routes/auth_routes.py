from fastapi import APIRouter,Body, Request,Depends, status, Header
from controllers.auth_controller import  signup, logout
from schemas.schemas import SignupRequest, UserResponse, SignupResponse
from config.db import get_db
from sqlalchemy.orm import Session
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
async def signup_route(
    req: SignupRequest = Body(...), 
    idempotency_key: str = Header(None, alias="Idempotency-Key"),
    db: Session = Depends(get_db)
) -> SignupResponse:
    logger.info(f"Processing signup for: {req.email}")
    return await signup(req,  db, idempotency_key)
