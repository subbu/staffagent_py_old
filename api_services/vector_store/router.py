from fastapi import APIRouter, Depends

router = APIRouter(
    prefix="/vector_store",
    tags=["vector_store"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
def query_vectors():
    return [{"username": "Rick"}, {"username": "Morty"}]