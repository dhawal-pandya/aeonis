from fastapi import APIRouter, Request, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid
from sqlalchemy.orm import Session
from ..db.database import get_db
from ..db.crud import PostgresTraceRepository
from ..db.repository import TraceRepository
from ..mcp import llm_service
from ..mcp.functions import ALL_TOOLS

router = APIRouter()


import logging

logger = logging.getLogger(__name__)

# pydantic models

class CreateProjectRequest(BaseModel):
    name: str
    git_repo_url: Optional[str] = None
    is_private: bool = False
    git_ssh_key: Optional[str] = None

# helper functions

def get_repository(db: Session = Depends(get_db)) -> TraceRepository:
    return PostgresTraceRepository(db)



# ai chat api


@router.post("/projects/{project_id}/chat", tags=["AI Chat"])
async def project_chat(
    project_id: uuid.UUID,
    request: Request,
    repo: TraceRepository = Depends(get_repository),
):
    """handles a chat message for a project."""
    logger.info(f"Received chat request for project_id: {project_id}")
    body = await request.json()
    user_query = body.get("message")
    if not user_query:
        logger.error("Chat request failed: No message in request body.")
        raise HTTPException(status_code=400, detail="Message is required.")

    # llm_service handles chat flow with all tools
    logger.info("Generating chat response from LLM service...")
    response_text = llm_service.generate_chat_response(
        user_query=user_query,
        project_id=str(project_id),
        repo=repo,
        tools=ALL_TOOLS,
    )
    logger.info("Successfully generated chat response.")
    return {"response": response_text}


# core project api


@router.get("/projects", tags=["Projects"])
async def get_all_projects(repo: TraceRepository = Depends(get_repository)):
    """retrieves all projects."""
    logger.info("Fetching all projects.")
    return repo.get_all_projects()


@router.get("/projects/{project_id}", tags=["Projects"])
async def get_project_by_id(
    project_id: uuid.UUID, repo: TraceRepository = Depends(get_repository)
):
    """retrieves a single project by its id."""
    logger.info(f"Fetching project with id: {project_id}")
    project = repo.get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    return project.to_dict(include_api_key=True)



@router.post("/projects", tags=["Projects"])
async def create_project(project_data: CreateProjectRequest, repo: TraceRepository = Depends(get_repository)):
    """creates a new project, returns it with api key."""
    logger.info(f"Creating new project with name: {project_data.name}")
    project = repo.create_project(
        name=project_data.name,
        git_repo_url=project_data.git_repo_url,
        is_private=project_data.is_private,
        git_ssh_key=project_data.git_ssh_key
    )
    logger.info(f"Successfully created project with ID: {project.id}")
    return project


@router.delete("/projects/{project_id}", tags=["Projects"])
async def delete_project(
    project_id: uuid.UUID, repo: TraceRepository = Depends(get_repository)
):
    """deletes a project and its associated data (spans)."""
    logger.info(f"Deleting project with ID: {project_id}")
    deleted_count = repo.delete_project(project_id)
    if not deleted_count:
        logger.error(f"Project with ID {project_id} not found for deletion.")
        raise HTTPException(status_code=404, detail="Project not found.")
    logger.info(f"Successfully deleted project with ID: {project_id}")
    return {"status": "deleted", "project_id": project_id}


# core traces api


@router.post("/traces", tags=["Traces"])
async def receive_traces(
    request: Request,
    x_aeonis_api_key: str = Header(None),
    repo: TraceRepository = Depends(get_repository),
):
    """receives and persists a batch of spans."""
    logger.info(f"Received trace request with API key: {x_aeonis_api_key}")
    try:
        logger.info("Received request to /traces endpoint.")
        if not x_aeonis_api_key:
            logger.error("Trace request failed: Missing X-Aeonis-API-Key header.")
            raise HTTPException(
                status_code=401, detail="X-Aeonis-API-Key header is required."
            )
        
        logger.info("Looking up project by API key...")
        project = repo.get_project_by_api_key(x_aeonis_api_key)
        if not project:
            logger.error("Trace request failed: Invalid API Key.")
            raise HTTPException(status_code=401, detail="Invalid API Key.")
        logger.info(f"Found project with ID: {project.id}")

        try:
            spans: List[Dict[str, Any]] = await request.json()
            logger.info(f"Received {len(spans)} spans in request body.")
        except Exception:
            logger.error("Trace request failed: Invalid JSON body.")
            raise HTTPException(status_code=400, detail="Invalid JSON body.")

        logger.info("Adding spans to the database...")
        repo.add_spans(spans, project.id)
        logger.info("Successfully added spans to the database.")
        return {"status": "received", "count": len(spans)}
    except Exception as e:
        logger.error("An unexpected error occurred in receive_traces", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/projects/{project_id}/traces", tags=["Traces"])
async def get_project_traces(
    project_id: uuid.UUID, repo: TraceRepository = Depends(get_repository)
):
    """retrieves all traces for a project, ordered by most recent."""
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
    """retrieves all spans for a trace id."""
    spans = repo.get_spans_by_trace_id(trace_id)
    if not spans:
        raise HTTPException(status_code=404, detail="Trace not found.")
    return spans


# for testing only


@router.post("/debug/clear-database", tags=["Debug"])
async def clear_database(repo: TraceRepository = Depends(get_repository)):
    """
    [dev only] deletes all data from database by dropping
    and recreating all tables.
    """
    repo.delete_all_data()
    return {"status": "database cleared"}
