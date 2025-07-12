from fastapi import APIRouter
from sqlalchemy.orm import Session
from controllers.user_controller import get_user_by_id

router = APIRouter()

@router.get("/users/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    return user
