import json
from typing import List
import uuid
from ..db.repository import TraceRepository

# This file contains the functions that the LLM can learn to use.
# Each function should have a clear purpose and type hints.


def execute_sql_query(repo: TraceRepository, query: str, params: dict = None) -> str:
    """
    Executes a read-only SQL query against the database with parameters and returns the result.
    Only SELECT statements are allowed.
    """
    if not query.strip().upper().startswith("SELECT"):
        raise ValueError("Only SELECT statements are allowed for security reasons.")

    # Convert the MapComposite object to a regular dict
    if params:
        params = dict(params)

    try:
        result = repo.execute_sql(query, params)
        # Convert the list of RowMapping objects to a list of dicts
        result_dicts = [dict(row) for row in result]
        return json.dumps(result_dicts)
    except Exception as e:
        return json.dumps({"error": str(e)})
