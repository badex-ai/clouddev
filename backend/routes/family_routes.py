from fastapi import APIRouter,Body
from controllers.family_controller import get_family

router = APIRouter()

@router.get("/{id}")
def read_family(id: int):
    return {"family_id": id}
