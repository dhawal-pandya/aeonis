import json
from typing import List
import uuid
from ..db.repository import TraceRepository

# this file contains functions for the llm to use.
# each function needs a clear purpose and type hints.


def execute_sql_query(repo: TraceRepository, query: str, params: dict = None) -> str:
    """
    executes a read-only sql query with parameters.
    only select statements are allowed.
    """
    if not query.strip().upper().startswith("SELECT"):
        raise ValueError("Only SELECT statements are allowed for security reasons.")

    # convert mapcomposite object to a regular dict
    if params:
        params = dict(params)

    try:
        result = repo.execute_sql(query, params)
        # convert list of rowmapping objects to list of dicts
        result_dicts = [dict(row) for row in result]
        return json.dumps(result_dicts)
    except Exception as e:
        return json.dumps({"error": str(e)})
