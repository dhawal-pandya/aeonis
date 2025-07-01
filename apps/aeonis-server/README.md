# Aeonis Server

This document provides quick instructions on how to run and test the Aeonis server.

## How to Run

1.  **Prerequisites**:
    Ensure you have a `GEMINI_API_KEY` set as an environment variable. This is required for the AI Chat functionality.

2.  **Install Dependencies**:
    Navigate to the `apps/aeonis-server/` directory and install the required Python packages:
    ```bash
    python3 -m pip install -r requirements.txt
    ```

3.  **Start the Server**:
    From the `apps/aeonis-server/` directory, run the server using Uvicorn:
    ```bash
    python3 -m uvicorn aeonis_server.main:app --host 0.0.0.0 --port 8000 --log-config uvicorn_log_config.json &
    ```
    This will start the server in the background on `http://localhost:8000`.

## How to Test (Ping API)

Once the server is running, you can test the `/ping` API endpoint:

```bash
curl http://localhost:8000/ping
```

Expected output:
```
{"message":"pong"}
```

## AI Chat API

The `aeonis-server` now includes an AI-powered chat endpoint for project-specific queries.

- **`POST /v1/projects/{project_id}/chat`**
  - **Description:** Sends a user message to the AI agent for a specific project and receives a response.
  - **Body:** `{"message": "Your question here"}`
  - **Success Response:** `200 OK` with a JSON object containing the AI's response.
  - **Example:** `curl -X POST -H "Content-Type: application/json" -d '{"message": "Show me the latest traces"}' http://localhost:8000/v1/projects/YOUR_PROJECT_ID/chat`
