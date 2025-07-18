import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv
load_dotenv()

from .api.router import router as api_router
from .db.database import init_db


app = FastAPI(title="Aeonis Ingestion Server", version="0.1.0")

# Set up CORS
if os.getenv("DEV_MODE", "false").lower() == "true":
    # In development, allow all origins for convenience.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # In production, restrict to specific origins.
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"http://localhost:\d+", # Adjust for your production frontend URL
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(api_router, prefix="/v1")


@app.get("/")
def read_root():
    return {"message": "Aeonis Ingestion Server is running."}


@app.get("/ping")
def ping():
    return {"message": "pong"}
