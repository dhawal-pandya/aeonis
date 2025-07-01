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
from aeonis_server.mcp import db_tools

# --- Mock LLM Service ---
# This is a mock of the llm_service to avoid making real API calls without a key.

def mock_generate_tool_call(user_query: str, project_id: uuid.UUID):
    """Simulates the LLM choosing a tool based on the query."""
    if "latest traces" in user_query:
        return {"name": "get_traces_by_project_id", "args": {"project_id": str(project_id)}}
    elif "spans for trace" in user_query:
        # In a real scenario, we'd parse the trace_id from the query
        # For this test, we'll just use a placeholder.
        return {"name": "get_spans_by_trace_id", "args": {"trace_id": "00000000-0000-0000-0000-000000000000"}}
    return {"name": "unknown_tool", "args": {}}

def mock_generate_response(user_query: str, tool_output: str) -> str:
    """Simulates the LLM generating a final response."""
    if not tool_output or tool_output == "[]":
        return "I couldn't find any data for your request."
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
    # In a real run, the second question would use a real trace_id from the first output.
    questions = [
        "Show me the latest traces",
        f"get me the spans for trace id 02d6e951-c3c6-4023-b571-3540b3606d74"
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
            if tool_name == "get_traces_by_project_id":
                tool_output = db_tools.get_traces_by_project_id(repo, project.id)
            elif tool_name == "get_spans_by_trace_id":
                # For the test, we extract the trace_id from the hardcoded query
                trace_id = user_query.split(" ")[-1]
                tool_output = db_tools.get_spans_by_trace_id(repo, trace_id)
            else:
                tool_output = f"Unknown tool: {tool_name}"
            print(f"   - Output: {tool_output[:300]}...")
        except Exception as e:
            print(f"   - Error executing tool: {e}")
            tool_output = "[]"

        # 3. Generate the final response (Mocked)
        print("\n🤖 Simulating LLM to generate final response...")
        final_response = mock_generate_response(user_query, tool_output)
        print(f"\n💬 Aeonis: {final_response}\n")
        print("---")

    db.close()

if __name__ == "__main__":
    asyncio.run(main())

