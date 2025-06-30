# Aeonis: An AI-Powered DevSecOps Platform

Aeonis is an observability platform designed to provide deep, AI-powered insights into your applications. It combines distributed tracing with a conversational AI interface, allowing developers to not only visualize application flow but also ask complex questions about their system's behavior, security, and performance.

Our vision is to create a comprehensive DevSecOps tool that helps developers:
- **Identify Security Risks**: Proactively detect potential data leaks by asking questions like, *"Is this change logging sensitive data to a webhook?"*
- **Understand Code Impact**: Analyze the ripple effects of changes, asking *"Where would a new feature require the fewest changes?"*
- **Optimize Performance**: Compare performance characteristics across different versions or feature flags, asking *"How did the last commit affect database query times?"*

## Core Components

1.  **`aeonis-tracer`**: Language-specific SDKs that developers integrate into their applications to capture detailed operational data (spans).
2.  **`aeonis-server`**: The central server that ingests, stores, and serves trace data, and will eventually host the AI-powered analysis engine.
3.  **`aeonis-ui`**: A modern web frontend for visualizing and analyzing the collected traces.

## Getting Started

This project is a monorepo containing the `aeonis-server` and `aeonis-ui`. The following instructions will guide you through setting up the development environment.

### Prerequisites
- Python 3.10+
- Node.js 18+
- Go 1.20+
- PostgreSQL

### 1. Setup the Aeonis Server

The server is a FastAPI application responsible for ingesting and serving trace data.

```bash
# Navigate to the server directory
cd apps/aeonis-server

# Create and activate a Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up the database (run this once)
# This assumes you have PostgreSQL running and a database named 'aeonisdb'
init_db() 

# Run the server
uvicorn aeonis_server.main:app --host 0.0.0.0 --port 8000 --reload
```

The server will be running at `http://localhost:8000`.

### 2. Setup the Aeonis UI

The UI is a React application for visualizing traces.

```bash
# Navigate to the UI directory
cd apps/aeonis-ui

# Install dependencies
npm install

# Run the development server
npm run dev
```

The UI will be available at `http://localhost:5173`.

## Server API Endpoints

The `aeonis-server` exposes the following RESTful API for managing projects and traces.

### Projects API

- **`GET /v1/projects`**
  - **Description:** Retrieves a list of all projects.
  - **Success Response:** `200 OK` with a JSON array of project objects.

- **`POST /v1/projects`**
  - **Description:** Creates a new project.
  - **Query Parameter:** `name` (string, required) - The name of the new project.
  - **Success Response:** `200 OK` with the newly created project object, including its `id` and `api_key`.
  - **Example:** `curl -X POST "http://localhost:8000/v1/projects?name=MyNewApp"`

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
*This README reflects the project status as of Monday, June 30, 2025.*
