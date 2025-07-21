import os
import json
import logging
import google.generativeai as genai
from google.generativeai import protos
from .prompts import SYSTEM_PROMPT
from ..db.repository import TraceRepository
from . import db_tools, git_tools

# configure logging
logger = logging.getLogger(__name__)

# configure gemini api key
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set.")
genai.configure(api_key=API_KEY)


def chat_with_db(user_query: str, project_id: str, repo: TraceRepository, tools: list):
    """handles chat interaction with tool calls and responses."""
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

    while True:
        part = response.candidates[0].content.parts[0]

        if hasattr(part, "function_call") and part.function_call:
            tool_call = part.function_call
            tool_name = tool_call.name
            tool_args = dict(tool_call.args)

            # tool dispatch
            tool_output_content = ""
            # database tools
            if tool_name == "execute_sql_query":
                try:
                    # force project_id into params for security
                    if "params" not in tool_args:
                        tool_args["params"] = {}
                    tool_args["params"]["project_id"] = project_id

                    # convert mapcomposite to dict before passing to tool
                    tool_args["params"] = dict(tool_args["params"])

                    logger.info(f"Executing SQL query from tool call: {tool_args}")
                    tool_output_content = db_tools.execute_sql_query(repo, **tool_args)
                except Exception as e:
                    logger.error(f"Error executing SQL query: {tool_args}", exc_info=True)
                    tool_output_content = json.dumps({"error": f"Failed to execute query: {e}"})
            # git tools
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

            # respond to model
            tool_output = protos.FunctionResponse(
                name=tool_name,
                response={"content": tool_output_content},
            )

            response = chat.send_message(
                protos.Part(function_response=tool_output)
            )
        else:
            # if no tool call, return direct text response
            return response.text

