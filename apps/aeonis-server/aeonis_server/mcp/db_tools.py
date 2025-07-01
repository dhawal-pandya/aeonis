import json
from typing import List
import uuid
from ..db.repository import TraceRepository

# This file contains the functions that the LLM can learn to use.
# Each function should have a clear purpose and type hints.


def get_traces_by_project_id(repo: TraceRepository, project_id: uuid.UUID) -> str:
    """Fetches the most recent traces for a given project ID."""
    traces = repo.get_traces_by_project_id(project_id)
    # We need to serialize the SQLAlchemy objects to a JSON string for the LLM
    return json.dumps([trace.to_dict() for trace in traces])


def get_spans_by_trace_id(repo: TraceRepository, trace_id: str) -> str:
    """Fetches all spans for a given trace ID."""
    spans = repo.get_spans_by_trace_id(trace_id)
    return json.dumps([span.to_dict() for span in spans])
