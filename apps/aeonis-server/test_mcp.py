import os
import sys
import uuid
import asyncio
import json
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the path to allow relative imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from aeonis_server.db.database import engine
from aeonis_server.db.crud import PostgresTraceRepository
from aeonis_server.mcp import db_tools, git_tools

# --- Mock LLM Service ---
# This is a mock of the llm_service to avoid making real API calls without a key.

def mock_generate_tool_call(user_query: str, project_id: uuid.UUID):
    """Simulates the LLM choosing a tool based on the query."""
    if "latest traces" in user_query:
        return {"name": "execute_sql_query", "args": {"query": f"SELECT * FROM spans WHERE project_id = '{project_id}' AND parent_span_id IS NULL LIMIT 10;"}}
    elif "spans for trace" in user_query:
        trace_id = user_query.split(" ")[-1]
        return {"name": "execute_sql_query", "args": {"query": f"SELECT * FROM spans WHERE trace_id = '{trace_id}';"}}
    elif "list all branches" in user_query:
        return {"name": "list_branches", "args": {}}
    elif "commit history" in user_query:
        # a bit of a hack to get the branch name
        branch = user_query.split("for the ")[-1].split(" branch")[0]
        return {"name": "get_commit_history", "args": {"branch": branch}}
    elif "diff for the last commit" in user_query:
        # This is a multi-step process, we first get the commit history and then the diff
        # For the test, we'll just get the latest commit from the main branch
        history = git_tools.get_commit_history("main", limit=1)
        last_commit_hash = history[0]['hash']
        return {"name": "get_commit_diff", "args": {"commit_hash": last_commit_hash}}
    elif "read the README.md" in user_query:
        history = git_tools.get_commit_history("main", limit=1)
        last_commit_hash = history[0]['hash']
        return {"name": "read_file_at_commit", "args": {"file_path": "README.md", "commit_hash": last_commit_hash}}
    return {"name": "unknown_tool", "args": {}}

def mock_generate_response(user_query: str, tool_output: str) -> str:
    """Simulates the LLM generating a final response."""
    if not tool_output or tool_output == "[]":
        return "I couldn't find any data for your request."
    # pretty print json
    try:
        parsed_json = json.loads(tool_output)
        tool_output = json.dumps(parsed_json, indent=2)
    except (json.JSONDecodeError, TypeError):
        pass # not a json string
    return f"Based on your request, I found the following information: {tool_output}"

# --- Main Test Runner ---

async def main():
    """Main function to run the CLI chat test."""
    print("Aeonis MCP CLI Tester (Mocked)")
    print("------------------------------")

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    repo = PostgresTraceRepository(db)

    projects = repo.get_all_projects()
    if not projects:
        print("No projects found. Please create a project first.")
        db.close()
        return

    project = projects[0]
    print(f"\nChatting with project: {project.name} (ID: {project.id})\n")

    # --- Test Questions ---
    questions = [
        "Show me the latest traces",
        "get me the spans for trace id 02d6e951-c3c6-4023-b571-3540b3606d74",
        "list all branches",
        "show me the commit history for the main branch",
        "show me the diff for the last commit",
        "read the README.md file at the last commit"
    ]

    for user_query in questions:
        print(f"> {user_query}")

        # 1. Generate the tool call (Mocked)
        print("\n🤖 Simulating LLM call to determine tool...")
        tool_call = mock_generate_tool_call(user_query, project.id)
        print(f"   - Tool: {tool_call.get('name')}")
        print(f"   - Args: {tool_call.get('args')}")

        # 2. Execute the tool
        tool_name = tool_call.get("name")
        tool_args = tool_call.get("args")
        tool_output = ""

        print("\n⚙️ Executing tool...")
        try:
            if tool_name == "execute_sql_query":
                tool_output = db_tools.execute_sql_query(repo, **tool_args)
            elif tool_name == "list_branches":
                tool_output = json.dumps(git_tools.list_branches())
            elif tool_name == "get_commit_history":
                tool_output = json.dumps(git_tools.get_commit_history(**tool_args))
            elif tool_name == "get_commit_diff":
                tool_output = json.dumps(git_tools.get_commit_diff(**tool_args))
            elif tool_name == "read_file_at_commit":
                tool_output = json.dumps(git_tools.read_file_at_commit(**tool_args))
            else:
                tool_output = f"Unknown tool: {tool_name}"
            print(f"   - Output: {tool_output[:500]}...")
        except Exception as e:
            print(f"   - Error executing tool: {e}")
            tool_output = "[]"

        # 3. Generate the final response (Mocked)
        print("\n��� Simulating LLM to generate final response...")
        final_response = mock_generate_response(user_query, tool_output)
        print(f"\n💬 Aeonis: {final_response}\n")
        print("---")

    db.close()

if __name__ == "__main__":
    asyncio.run(main())

