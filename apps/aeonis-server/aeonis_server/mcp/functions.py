from google.generativeai.types import FunctionDeclaration, Tool

# --- Database Tool Declarations ---
EXECUTE_SQL_QUERY = FunctionDeclaration(
    name="execute_sql_query",
    description="Executes a read-only SQL query (SELECT) against the database.",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The SELECT SQL query to execute.",
            },
        },
        "required": ["query"],
    },
)

# --- Git Tool Declarations ---
LIST_BRANCHES = FunctionDeclaration(
    name="list_branches",
    description="Lists all branches in the Git repository.",
)

GET_COMMIT_HISTORY = FunctionDeclaration(
    name="get_commit_history",
    description="Returns the commit history for a given branch.",
    parameters={
        "type": "object",
        "properties": {
            "branch": {"type": "string", "description": "The branch name to get history for."},
            "limit": {"type": "integer", "description": "The maximum number of commits to return.", "default": 10},
        },
        "required": ["branch"],
    },
)

GET_COMMIT_DIFF = FunctionDeclaration(
    name="get_commit_diff",
    description="Returns the diff for a specific commit hash.",
    parameters={
        "type": "object",
        "properties": {
            "commit_hash": {"type": "string", "description": "The commit hash to get the diff for."},
        },
        "required": ["commit_hash"],
    },
)

READ_FILE_AT_COMMIT = FunctionDeclaration(
    name="read_file_at_commit",
    description="Reads the content of a file at a specific commit hash.",
    parameters={
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "The path to the file."},
            "commit_hash": {"type": "string", "description": "The commit hash to read the file from."},
        },
        "required": ["file_path", "commit_hash"],
    },
)


# --- Tool Definitions ---
DB_TOOLS = Tool(
    function_declarations=[
        EXECUTE_SQL_QUERY,
    ]
)

GIT_TOOLS = Tool(
    function_declarations=[
        LIST_BRANCHES,
        GET_COMMIT_HISTORY,
        GET_COMMIT_DIFF,
        READ_FILE_AT_COMMIT,
    ]
)

# --- Combined Tool List ---
ALL_TOOLS = [DB_TOOLS, GIT_TOOLS]
