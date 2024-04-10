from fastapi import APIRouter, Depends

router = APIRouter(
    prefix="/phone_agent",
    tags=["phone_agent"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{id}")
def get_phone_agent(id: int):
    return {"agent": "Rick", "number": "111-111-1111", "id": id}

