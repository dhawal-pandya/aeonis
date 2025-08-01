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

        # initialize a list to hold all tool outputs for this turn
        tool_outputs = []

        for part in response.candidates[0].content.parts:
            if hasattr(part, "function_call") and part.function_call:
                tool_call = part.function_call
                tool_name = tool_call.name
                tool_args = dict(tool_call.args)

                logger.info(f"Tool Call: {tool_name} with args: {tool_args}")

                # tool dispatch
                tool_output_content = None  # default to none

                # database tools
                if tool_name == "execute_sql_query":
                    try:
                        if "params" not in tool_args:
                            tool_args["params"] = {}
                        tool_args["params"]["project_id"] = project_id
                        tool_args["params"] = dict(tool_args["params"])
                        logger.info(f"Executing SQL query: {tool_args}")
                        tool_output_content = db_tools.execute_sql_query(
                            repo, **tool_args
                        )
                    except Exception as e:
                        logger.error(f"Error executing SQL: {e}", exc_info=True)
                        tool_output_content = json.dumps({"error": str(e)})

                # git tools
                elif tool_name == "list_branches":
                    tool_output_content = git_tools.list_branches(project_id, repo)
                elif tool_name == "get_commit_history":
                    if "branch" not in tool_args or not tool_args["branch"]:
                        default_branch = git_tools.get_default_branch(
                            project_id, repo
                        )
                        if default_branch:
                            tool_args["branch"] = default_branch
                        else:
                            tool_output_content = json.dumps(
                                {"error": "Could not determine default branch."}
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
                elif tool_name == "list_files_at_commit":
                    tool_output_content = git_tools.list_files_at_commit(
                        project_id, repo, **tool_args
                    )
                elif tool_name == "get_commit_author":
                    tool_output_content = git_tools.get_commit_author(
                        project_id, repo, **tool_args
                    )
                elif tool_name == "analyze_code_with_semgrep":
                    tool_output_content = git_tools.analyze_code_with_semgrep(
                        project_id, repo, **tool_args
                    )
                else:
                    tool_output_content = json.dumps(
                        {"error": f"Unknown tool: {tool_name}"}
                    )

                # if a tool execution happened, append the output
                if tool_output_content is not None:
                    tool_outputs.append(
                        protos.Part(
                            function_response=protos.FunctionResponse(
                                name=tool_name,
                                response={"content": tool_output_content},
                            )
                        )
                    )

        # if there were tool calls, send their responses back to the model
        if tool_outputs:
            response = chat.send_message(tool_outputs)
        else:
            # if there were no function calls, it should be a text response
            final_response_part = response.candidates[0].content.parts[0]
            if hasattr(final_response_part, "text") and final_response_part.text:
                return final_response_part.text
            else:
                logger.error(
                    f"Unhandled response part type: {type(final_response_part)}"
                )
                return "I received a response I don't know how to handle. Please try again."
