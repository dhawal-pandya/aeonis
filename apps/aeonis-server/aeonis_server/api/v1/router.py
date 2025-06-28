from fastapi import APIRouter
from .endpoints import traces

api_router = APIRouter()
api_router.include_router(traces.router, prefix="/traces", tags=["traces"])
