from fastapi import FastAPI, Request, HTTPException
from typing import List
import json

app = FastAPI()

# This is a temporary in-memory representation of our trace schema for validation.
# In the future, this could be more robust, perhaps by fetching the schema definition.
REQUIRED_SPAN_KEYS = {
    "trace_id",
    "span_id",
    "name",
    "start_time",
    "end_time",
}

@app.post("/v1/traces")
async def receive_traces(request: Request):
    """
    Receives a batch of spans, validates them, and prints them to the console.
    """
    try:
        spans = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON body.")

    if not isinstance(spans, list):
        raise HTTPException(status_code=400, detail="Request body must be a JSON array of spans.")

    print(f"--- Received batch of {len(spans)} spans ---")
    for i, span in enumerate(spans):
        if not isinstance(span, dict):
            print(f"  - Span {i+1} is not a valid object, skipping.")
            continue

        missing_keys = REQUIRED_SPAN_KEYS - set(span.keys())
        if missing_keys:
            print(f"  - Span {i+1} is missing required keys: {missing_keys}, skipping.")
            continue

        print(f"  - Span {i+1}:")
        print(f"    TraceID: {span.get('trace_id')}")
        print(f"    SpanID:  {span.get('span_id')}")
        print(f"    Name:    {span.get('name')}")
    print("--- End of batch ---")

    return {"status": "received", "count": len(spans)}

@app.get("/")
def read_root():
    return {"message": "Aeonis Ingestion Server is running."}
