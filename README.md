# Aeonis: An AI-Powered Observability Platform

Aeonis is an observability platform designed to provide deep, AI-powered insights into your applications. It combines distributed tracing with a conversational AI interface, allowing developers to not only visualize application flow but also ask complex questions about their system's behavior, security, and performance.

## Guiding Principles

-   **Developer Experience is Paramount**: Simple, idiomatic, and low-friction.
-   **Specification-Driven and Modular**: Language-agnostic, decoupled, and scalable.
-   **Performance is a Non-Negotiable Feature**: Asynchronous, efficient, and low-overhead.
-   **Security and Privacy by Design**: Secure defaults, PII-aware, and data integrity.
-   **Pragmatic, Not Dogmatic**: Practical, justified, and the right tool for the job.

## High-Level Architecture

The Aeonis platform consists of three main components:

1.  **Tracer SDKs (`/packages/tracer-sdk`)**: Language-specific libraries that developers integrate into their applications. They capture operational data (spans) and export it to the Aeonis Server.
2.  **Aeonis Server (`/apps/aeonis-server`)**: The central backend that ingests, stores, and serves trace data. It exposes a REST API for data collection and querying, and it integrates with Google Gemini to provide an AI-powered chat for analysis.
3.  **Aeonis UI (`/apps/aeonis-ui`)**: A modern React-based web frontend for visualizing traces and interacting with the AI chat interface.

## Getting Started

This project is a monorepo containing the `aeonis-server` and `aeonis-ui`. The following instructions will guide you through setting up the development environment.

### Prerequisites
- Python 3.10+
- Node.js 18+
- Go 1.20+
- PostgreSQL

## Local Development Setup

This project is a monorepo containing the server and UI. The following instructions will guide you through setting up the full local development environment.

### Step 1: Set up the Aeonis Server

The server is the core of the platform. It must be running for the UI to function.

**For detailed instructions, refer to the server's README:**
[`/apps/aeonis-server/README.md`](./apps/aeonis-server/README.md)

**Quick Setup:**

1.  **Setup PostgreSQL:** Create a database named `aeonisdb`.
    ```sql
    -- In psql
    CREATE DATABASE aeonisdb;
    ```
2.  **Configure Environment:** Create an `.env` file in `/apps/aeonis-server/` with your `GEMINI_API_KEY` and `DATABASE_URL`.
3.  **Install & Run:**
    ```bash
    # Navigate to the server directory
    cd apps/aeonis-server

    # Create and activate a Python virtual environment
    python3 -m venv .venv
    source .venv/bin/activate

    # Install dependencies
    pip install -r requirements.txt

    # Initialize the database schema (run once)
    python3 init_db_script.py

    # Run the server
    uvicorn aeonis_server.main:app --host 127.0.0.1 --port 8000
    ```

### Step 2: Set up the Aeonis UI

The UI is the web interface for interacting with the platform.

**For detailed instructions, refer to the UI's README:**
[`/apps/aeonis-ui/README.md`](./apps/aeonis-ui/README.md)

**Quick Setup:**

1.  **Navigate to the UI directory:**
    ```bash
    cd apps/aeonis-ui
    ```
2.  **Install dependencies:**
    ```bash
    npm install
    ```
3.  **Run the development server:**
    ```bash
    npm run dev
    ```

### Step 3: Use the Application

-   The **Aeonis Server** will be running at `http://127.0.0.1:8000`.
-   The **Aeonis UI** will be available at `http://localhost:5173`.

Open the UI in your browser to start exploring. You will need a Project ID to fetch traces and use the chat. You can create a project and get an API key by calling the server's API.

### Projects API

**Example: Create a Project**
```bash
curl -X POST "http://localhost:8000/v1/projects?name=MyTestProject"
```
This will return a new project with an `id` and `api_key`. Use the `id` in the UI.

- **`GET /v1/projects`**
  - **Description:** Retrieves a list of all projects.
  - **Success Response:** `200 OK` with a JSON array of project objects.


- **`DELETE /v1/projects/{project_id}`**
  - **Description:** Deletes a project and all of its associated traces.
  - **Success Response:** `200 OK` with a confirmation message.

### Traces API

- **`POST /v1/traces`**
  - **Description:** Ingests a batch of spans for a project.
  - **Header:** `X-Aeonis-API-Key` (string, required) - The API key for the project.
  - **Body:** A JSON array of span objects.
  - **Success Response:** `200 OK` with a status message.

- **`GET /v1/projects/{project_id}/traces`**
  - **Description:** Retrieves all traces for a specific project, ordered by most recent.
  - **Success Response:** `200 OK` with a JSON array of span objects.

- **`GET /v1/traces/{trace_id}`**
  - **Description:** Retrieves all spans for a specific trace ID.
  - **Success Response:** `200 OK` with a JSON array of span objects.

### Debug API

- **`POST /v1/debug/clear-database`**
  - **Description:** [FOR DEVELOPMENT ONLY] Deletes all data from the database by dropping and recreating all tables.
  - **Success Response:** `200 OK` with a confirmation message.


---
*This README reflects the project status as of Wednesday, July 9, 2025.*