import os
import google.generativeai as genai
from .prompts import SYSTEM_PROMPT

# Configure the Gemini API key
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set.")
genai.configure(api_key=API_KEY)

# Initialize the generative model
model = genai.GenerativeModel(
    "gemini-1.5-flash-latest",
    system_instruction=SYSTEM_PROMPT,
)

def generate_tool_call(user_query: str, tools: list) -> dict:
    """Generates the tool call dictionary based on the user query."""
    response = model.generate_content(
        user_query,
        tools=tools,
    )
    tool_call = response.candidates[0].content.parts[0].function_call
    return {
        "name": tool_call.name,
        "args": dict(tool_call.args)
    }

def generate_response(user_query: str, tool_output: str) -> str:
    """Generates a natural language response based on the tool output."""
    # This is a simplified RAG prompt.
    # The model is given the original query and the data retrieved by the tool.
    # It uses this data as context to formulate the final answer.
    prompt = f"""
    User Query: {user_query}

    You have executed a tool and received the following data:
    ---
    {tool_output}
    ---

    Based on this data, please provide a natural language response to the user's query.
    """
    response = model.generate_content(prompt)
    return response.text