from fastapi import FastAPI
from .phone_agent.router import router as phone_agent_router
from .vector_store.router import router as vector_store_router

app = FastAPI()
app.include_router(phone_agent_router)
app.include_router(vector_store_router)

