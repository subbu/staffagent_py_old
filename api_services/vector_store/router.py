from fastapi import APIRouter, Depends

router = APIRouter()

@router.get("/vector_store")
def query_vectors():
    return [{"username": "Rick"}, {"username": "Morty"}]