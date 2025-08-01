import json
import uuid
import datetime
import decimal
from ..db.repository import TraceRepository

# this file contains functions for the llm to use.
# each function needs a clear purpose and type hints.


class CustomJsonEncoder(json.JSONEncoder):
    """custom json encoder to handle uuid and datetime objects."""

    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            # if the obj is uuid, we return the uuid as a string
            return str(obj)
        if isinstance(obj, datetime.datetime):
            # if the obj is datetime, we return the datetime as a string
            return obj.isoformat()
        if isinstance(obj, decimal.Decimal):
            # if the obj is decimal, we return the decimal as a float
            return float(obj)
        return super().default(obj)


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
        return json.dumps(result_dicts, cls=CustomJsonEncoder)
    except Exception as e:
        return json.dumps({"error": str(e)})
