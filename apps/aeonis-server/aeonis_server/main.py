from fastapi import FastAPI
from .api.v1.router import api_router

app = FastAPI(
    title="Aeonis Ingestion Server",
    version="0.1.0"
)

app.include_router(api_router, prefix="/v1")

@app.get("/")
def read_root():
    return {"message": "Aeonis Ingestion Server is running."}
