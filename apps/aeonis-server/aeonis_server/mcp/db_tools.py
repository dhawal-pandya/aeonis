import json
from typing import List
import uuid
from ..db.repository import TraceRepository

# This file contains the functions that the LLM can learn to use.
# Each function should have a clear purpose and type hints.


def execute_sql_query(repo: TraceRepository, query: str) -> str:
    """
    Executes a read-only SQL query against the database and returns the result.
    Only SELECT statements are allowed.
    """
    if not query.strip().upper().startswith("SELECT"):
        raise ValueError("Only SELECT statements are allowed for security reasons.")

    try:
        result = repo.execute_sql(query)
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})
