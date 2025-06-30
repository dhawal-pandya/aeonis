from fastapi import APIRouter, Request, HTTPException, Depends, Header
from typing import List, Dict, Any
import uuid
from sqlalchemy.orm import Session
from ..db.database import get_db
from ..db.crud import PostgresTraceRepository
from ..db.repository import TraceRepository

# from ..mcp.agent import mcp_agent

router = APIRouter()


def get_repository(db: Session = Depends(get_db)) -> TraceRepository:
    return PostgresTraceRepository(db)


# # --- AI Chat API ---


# @router.post("/chat", tags=["AI Chat"])
# async def chat_with_agent(message: str):
#     """Receives a user message and returns the agent's response."""
#     try:
#         response = mcp_agent.chat(message)
#         return {"response": response}
#     except Exception as e:
#         import logging

#         logging.exception("Error during chat interaction")
#         raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")


# --- Core Project API ---


@router.get("/projects", tags=["Projects"])
async def get_all_projects(repo: TraceRepository = Depends(get_repository)):
    """Retrieves all projects."""
    return repo.get_all_projects()


@router.post("/projects", tags=["Projects"])
async def create_project(name: str, repo: TraceRepository = Depends(get_repository)):
    """Creates a new project and returns it, including the API key."""
    return repo.create_project(name)


@router.delete("/projects/{project_id}", tags=["Projects"])
async def delete_project(
    project_id: uuid.UUID, repo: TraceRepository = Depends(get_repository)
):
    """Deletes a project and all of its associated data (spans)."""
    deleted_count = repo.delete_project(project_id)
    if not deleted_count:
        raise HTTPException(status_code=404, detail="Project not found.")
    return {"status": "deleted", "project_id": project_id}


# --- Core Traces API ---


@router.post("/traces", tags=["Traces"])
async def receive_traces(
    request: Request,
    x_aeonis_api_key: str = Header(None),
    repo: TraceRepository = Depends(get_repository),
):
    """Receives and persists a batch of spans."""
    if not x_aeonis_api_key:
        raise HTTPException(
            status_code=401, detail="X-Aeonis-API-Key header is required."
        )
    project = repo.get_project_by_api_key(x_aeonis_api_key)
    if not project:
        raise HTTPException(status_code=401, detail="Invalid API Key.")

    try:
        spans: List[Dict[str, Any]] = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body.")

    repo.add_spans(spans, project.id)
    return {"status": "received", "count": len(spans)}


@router.get("/projects/{project_id}/traces", tags=["Traces"])
async def get_project_traces(
    project_id: uuid.UUID, repo: TraceRepository = Depends(get_repository)
):
    """Retrieves all traces for a given project, ordered by most recent."""
    try:
        return repo.get_traces_by_project_id(project_id)
    except Exception as e:
        import logging

        logging.exception("Error getting project traces")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/traces/{trace_id}", tags=["Traces"])
async def get_trace_by_id(
    trace_id: str, repo: TraceRepository = Depends(get_repository)
):
    """Retrieves all spans for a given trace ID."""
    spans = repo.get_spans_by_trace_id(trace_id)
    if not spans:
        raise HTTPException(status_code=404, detail="Trace not found.")
    return spans


# --- Debug API ---


@router.post("/debug/clear-database", tags=["Debug"])
async def clear_database(repo: TraceRepository = Depends(get_repository)):
    """
    [FOR DEVELOPMENT ONLY] Deletes all data from the database by dropping
    and recreating all tables.
    """
    repo.delete_all_data()
    return {"status": "database cleared"}
