import os
import json
import google.generativeai as genai
from google.generativeai import protos
from .prompts import SYSTEM_PROMPT
from ..db.repository import TraceRepository
from . import db_tools

# Configure the Gemini API key
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set.")
genai.configure(api_key=API_KEY)


def chat_with_db(user_query: str, project_id: str, repo: TraceRepository, tools: list):
    """
    Handles the full chat interaction, including tool calls and natural language responses.
    """
    # Initialize the generative model with tools.
    # A new model is initialized for each request to include the project_id
    # in the system instructions, ensuring the context is always current.
    system_instruction = f"{SYSTEM_PROMPT}\n\n**Current Project Context:** You are currently operating on `project_id`: `{project_id}`."

    model = genai.GenerativeModel(
        "gemini-2.5-flash",
        system_instruction=system_instruction,
        tools=tools,
    )

    chat = model.start_chat()

    # Send user query to the model
    response = chat.send_message(
        user_query, tool_config={"function_calling_config": "auto"}
    )

    first_part = response.candidates[0].content.parts[0]

    if hasattr(first_part, "function_call") and first_part.function_call:
        tool_call = first_part.function_call
        tool_name = tool_call.name
        tool_args = dict(tool_call.args)

        # Execute the requested tool
        tool_output_content = ""
        if tool_name == "get_traces_by_project_id":
            # The model will call this function without the project_id arg,
            # so we add it here from the request context.
            tool_args["project_id"] = project_id
            tool_output_content = db_tools.get_traces_by_project_id(repo, **tool_args)
        elif tool_name == "get_spans_by_trace_id":
            tool_output_content = db_tools.get_spans_by_trace_id(repo, **tool_args)
        elif tool_name == "execute_sql_query":
            tool_output_content = db_tools.execute_sql_query(repo, **tool_args)
        else:
            tool_output_content = json.dumps({"error": f"Unknown tool: {tool_name}"})

        # Create the tool output object for the model
        tool_output = protos.FunctionResponse(
            name=tool_name,
            response={"content": tool_output_content},
        )

        # Send the tool output back to the model to get a natural language response
        final_response = chat.send_message(tool_output)
        return final_response.text
    else:
        # The model decided no tool was needed and returned text directly.
        return first_part.text
