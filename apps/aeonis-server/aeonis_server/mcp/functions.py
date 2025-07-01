from google.generativeai.types import FunctionDeclaration, Tool

# Define the tools that the LLM can use
GET_TRACES_BY_PROJECT_ID = FunctionDeclaration(
    name="get_traces_by_project_id",
    description="Fetches the most recent traces for a given project ID.",
    parameters={
        "type": "object",
        "properties": {
            "project_id": {"type": "string", "description": "The UUID of the project."},
        },
        "required": ["project_id"],
    },
)

GET_SPANS_BY_TRACE_ID = FunctionDeclaration(
    name="get_spans_by_trace_id",
    description="Fetches all spans for a given trace ID.",
    parameters={
        "type": "object",
        "properties": {
            "trace_id": {"type": "string", "description": "The ID of the trace."},
        },
        "required": ["trace_id"],
    },
)

# Create a Tool object from the function declarations
DB_TOOLS = Tool(
    function_declarations=[
        GET_TRACES_BY_PROJECT_ID,
        GET_SPANS_BY_TRACE_ID,
    ]
)
