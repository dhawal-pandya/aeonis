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


def generate_chat_response(
    user_query: str, project_id: str, repo: TraceRepository, tools: list
):
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
        if not response.candidates:
            return "An unexpected error occurred: No candidates in response."

        part = (
            response.candidates[0].content.parts[0]
            if response.candidates[0].content.parts
            else None
        )
        if not part:
            return "An unexpected error occurred: No parts in response."

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
                    logger.error(
                        f"Error executing SQL query: {tool_args}", exc_info=True
                    )
                    tool_output_content = json.dumps(
                        {"error": f"Failed to execute query: {e}"}
                    )
            # git tools
            elif tool_name == "list_branches":
                tool_output_content = git_tools.list_branches(project_id, repo)
            elif tool_name == "get_commit_history":
                # if model doesnt provide a branch, use the default branch.
                if "branch" not in tool_args or not tool_args["branch"]:
                    default_branch = git_tools.get_default_branch(project_id, repo)
                    if default_branch:
                        tool_args["branch"] = default_branch
                    else:
                        tool_output_content = json.dumps(
                            {"error": "Could not determine the default branch."}
                        )

                if "branch" in tool_args:
                    tool_output_content = git_tools.get_commit_history(
                        project_id, repo, **tool_args
                    )

            elif tool_name == "get_commit_diff":
                tool_output_content = git_tools.get_commit_diff(
                    project_id, repo, **tool_args
                )
            elif tool_name == "read_file_at_commit":
                tool_output_content = git_tools.read_file_at_commit(
                    project_id, repo, **tool_args
                )
            elif tool_name == "analyze_code_with_semgrep":
                # if model doesnt provide a commit hash, use the latest one from the default branch.
                if "commit_hash" not in tool_args or not tool_args["commit_hash"]:
                    default_branch = git_tools.get_default_branch(project_id, repo)
                    if default_branch:
                        history = git_tools.get_commit_history(
                            project_id, repo, branch=default_branch, limit=1
                        )
                        if history and not isinstance(history, dict):
                            latest_commit_hash = history[0].get("hash")
                            if latest_commit_hash:
                                tool_args["commit_hash"] = latest_commit_hash
                            else:
                                tool_output_content = json.dumps(
                                    {
                                        "error": "Could not determine the latest commit hash."
                                    }
                                )
                        else:
                            tool_output_content = json.dumps(
                                {
                                    "error": "Could not retrieve commit history to find the latest commit."
                                }
                            )
                    else:
                        tool_output_content = json.dumps(
                            {
                                "error": "Could not determine the default branch for analysis."
                            }
                        )

                if "commit_hash" in tool_args and not tool_output_content:
                    tool_output_content = git_tools.analyze_code_with_semgrep(
                        project_id, repo, **tool_args
                    )
            else:
                tool_output_content = json.dumps(
                    {"error": f"Unknown tool: {tool_name}"}
                )

            # respond to model
            tool_output = protos.FunctionResponse(
                name=tool_name,
                response={"content": tool_output_content},
            )

            response = chat.send_message(protos.Part(function_response=tool_output))
        else:
            # if the part is not a function call, it should be text.
            # add a check for robustness.
            if hasattr(part, "text") and part.text:
                return part.text
            else:
                # if it's not text and not a function call, we don't know how to handle it.
                logger.error(f"Unhandled response part type: {type(part)}")
                return "I received a response I don't know how to handle. Please try again."
