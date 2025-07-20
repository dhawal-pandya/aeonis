import os
import json
import google.generativeai as genai
from google.generativeai import protos
from .prompts import SYSTEM_PROMPT
from ..db.repository import TraceRepository
from . import db_tools, git_tools

# Configure the Gemini API key
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set.")
genai.configure(api_key=API_KEY)


def chat_with_db(user_query: str, project_id: str, repo: TraceRepository, tools: list):
    """
    Handles the full chat interaction, including tool calls and natural language responses.
    """
    system_instruction = f"{SYSTEM_PROMPT}\n\n**Current Project Context:** You are currently operating on `project_id`: `{project_id}`."

    model = genai.GenerativeModel(
        "gemini-1.5-flash",
        system_instruction=system_instruction,
        tools=tools,
    )

    chat = model.start_chat()

    response = chat.send_message(
        user_query, tool_config={"function_calling_config": "auto"}
    )

    first_part = response.candidates[0].content.parts[0]

    if hasattr(first_part, "function_call") and first_part.function_call:
        tool_call = first_part.function_call
        tool_name = tool_call.name
        tool_args = dict(tool_call.args)

        # --- Tool Dispatch ---
        tool_output_content = ""
        # Database Tools
        if tool_name == "execute_sql_query":
            tool_output_content = db_tools.execute_sql_query(repo, **tool_args)
        # Git Tools
        elif tool_name == "list_branches":
            tool_output_content = git_tools.list_branches(project_id, repo)
        elif tool_name == "get_commit_history":
            tool_output_content = git_tools.get_commit_history(project_id, repo, **tool_args)
        elif tool_name == "get_commit_diff":
            tool_output_content = git_tools.get_commit_diff(project_id, repo, **tool_args)
        elif tool_name == "read_file_at_commit":
            tool_output_content = git_tools.read_file_at_commit(project_id, repo, **tool_args)
        else:
            tool_output_content = json.dumps({"error": f"Unknown tool: {tool_name}"})

        # --- Respond to Model ---
        tool_output = protos.FunctionResponse(
            name=tool_name,
            response={"content": tool_output_content},
        )

        final_response = chat.send_message(tool_output)
        return final_response.text
    else:
        # If no tool call, return the direct text response
        return first_part.text
