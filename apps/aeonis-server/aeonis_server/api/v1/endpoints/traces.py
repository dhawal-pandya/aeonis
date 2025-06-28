from fastapi import APIRouter, Request, HTTPException
from typing import List
import json
import pprint

router = APIRouter()

REQUIRED_SPAN_KEYS = {
    "trace_id",
    "span_id",
    "name",
    "start_time",
    "end_time",
}

@router.post("/")
async def receive_traces(request: Request):
    """
    Receives a batch of spans, validates them, and prints their full content.
    """
    try:
        spans = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON body.")

    if not isinstance(spans, list):
        raise HTTPException(status_code=400, detail="Request body must be a JSON array of spans.")

    print(f"--- Received batch of {len(spans)} spans ---")
    for i, span in enumerate(spans):
        print(f"--- Span {i+1} ---")
        if not isinstance(span, dict):
            print("  - Invalid span format: not a dictionary.")
            continue

        missing_keys = REQUIRED_SPAN_KEYS - set(span.keys())
        if missing_keys:
            print(f"  - Invalid span: missing required keys: {missing_keys}")
            continue
        
        pprint.pprint(span)

    print("--- End of batch ---")

    return {"status": "received", "count": len(spans)}
