from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.v1.router import api_router
from .db.database import init_db

app = FastAPI(
    title="Aeonis Ingestion Server",
    version="0.1.0"
)

# Set up CORS
origins = [
    "http://localhost",
    "http://localhost:5173", # Default Vite dev server port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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
