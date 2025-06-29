from fastapi import APIRouter, Request, HTTPException, Depends, Header
from typing import List, Dict, Any
import uuid
from sqlalchemy.orm import Session
from aeonis_server.db.database import get_db
from aeonis_server.db.crud import PostgresTraceRepository
from aeonis_server.db.repository import TraceRepository

router = APIRouter()

def get_repository(db: Session = Depends(get_db)) -> TraceRepository:
    return PostgresTraceRepository(db)

@router.post("/")
async def receive_traces(
    request: Request,
    x_aeonis_api_key: str = Header(None),
    repo: TraceRepository = Depends(get_repository)
):
    """
    Receives a batch of spans, validates them against an API key,
    and persists them to the database.
    """
    if not x_aeonis_api_key:
        raise HTTPException(status_code=401, detail="X-Aeonis-API-Key header is required.")

    project = repo.get_project_by_api_key(x_aeonis_api_key)
    if not project:
        raise HTTPException(status_code=401, detail="Invalid API Key.")

    try:
        spans: List[Dict[str, Any]] = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body.")

    if not isinstance(spans, list):
        raise HTTPException(status_code=400, detail="Request body must be a JSON array of spans.")

    # Log the received spans for debugging
    import json
    print(json.dumps(spans, indent=2))

    # Here you might add more robust validation against the trace-schema.json
    
    repo.add_spans(spans, project.id)

    return {"status": "received", "count": len(spans), "project_id": str(project.id)}

@router.get("/projects/{project_id}/traces")
async def get_project_traces(
    project_id: uuid.UUID,
    repo: TraceRepository = Depends(get_repository)
):
    """
    Retrieves the most recent traces for a given project ID.
    """
    traces = repo.get_traces_by_project_id(project_id)
    return traces

@router.delete("/projects/{project_id}")
async def delete_project_traces(
    project_id: uuid.UUID,
    repo: TraceRepository = Depends(get_repository)
):
    """
    Deletes all traces for a given project ID.
    """
    num_deleted = repo.delete_traces_by_project_id(project_id)
    return {"status": "deleted", "deleted_count": num_deleted}

@router.get("/{trace_id}")
async def get_trace_by_id(
    trace_id: str,
    repo: TraceRepository = Depends(get_repository)
):
    """
    Retrieves all spans for a given trace ID.
    """
    spans = repo.get_spans_by_trace_id(trace_id)
    if not spans:
        raise HTTPException(status_code=404, detail="Trace not found.")
    return spans
