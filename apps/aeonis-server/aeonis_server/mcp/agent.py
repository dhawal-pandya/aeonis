# from google.adk.agents import Agent
# from toolbox_core import ToolboxSyncClient
# import os

# # The URL of the standalone Toolbox Server.
# TOOLBOX_SERVER_URL = os.getenv("TOOLBOX_SERVER_URL", "http://localhost:5000")

# # This client connects to the standalone Toolbox Server to access the tools.
# toolbox = ToolboxSyncClient(url=TOOLBOX_SERVER_URL)

# # Load the toolset from the running Toolbox Server.
# tools = toolbox.load_toolset("aeonis_toolset")

# # Define the root agent
# mcp_agent = Agent(
#     name="AeonisCopilot",
#     model="gemini-2.5-flash-latest",
#     description="An agent that can answer questions about projects, traces, and spans in the Aeonis database.",
#     instruction=(
#         "You are a helpful assistant for the Aeonis observability platform. "
#         "Your goal is to help developers understand the data stored in the system. "
#         "Use the available tools to answer questions about projects, traces, and spans. "
#         "Be concise and clear in your answers. Do not hallucinate or make up information."
#     ),
#     tools=tools,
# )
