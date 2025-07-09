# Aeonis Server

The Aeonis Server is the central backend for the Aeonis observability platform. It's a FastAPI application responsible for ingesting trace data, managing projects, and providing an AI-powered chat interface for data analysis.

## Getting Started

These instructions will guide you through setting up and running the server on your local machine for development and testing purposes.

### 1. Prerequisites

-   **Python 3.10+**
-   **PostgreSQL:** The server uses a PostgreSQL database. Make sure you have it installed and running.
-   **Google Gemini API Key:** The AI chat functionality is powered by Google Gemini. You will need an API key.

### 2. Database Setup

The server requires a PostgreSQL database named `aeonisdb`.

1.  **Start the PostgreSQL service.**

2.  **Create the database:**
    Open `psql` and run the following command to create the database.

    ```sql
    CREATE DATABASE aeonisdb;
    ```

### 3. Environment Setup

The server requires a `.env` file for configuration.

1.  **Create the file:**
    In the `apps/aeonis-server/` directory, create a file named `.env`.

2.  **Add environment variables:**
    Add the following key-value pairs to the `.env` file.

    ```env
    # Get your API key from Google AI Studio: https://aistudio.google.com/app/apikey
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY"

    # This is the default connection string. Change it if your PostgreSQL setup is different.
    DATABASE_URL="postgresql://localhost/aeonisdb"
    ```

    Replace `"YOUR_GEMINI_API_KEY"` with your actual key.

### 4. Installation

1.  **Navigate to the server directory:**
    ```bash
    cd apps/aeonis-server
    ```

2.  **Create a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### 5. Initialize the Database Schema

Run the initialization script to create the necessary tables in your database.

```bash
python3 init_db_script.py
```

You should see the output `Database initialized successfully.`

### 6. Running the Server

You can now start the server using Uvicorn.

```bash
uvicorn aeonis_server.main:app --host 127.0.0.1 --port 8000
```

The server will be running at `http://127.0.0.1:8000`.

## API Verification

You can verify that the server is running correctly by sending a `GET` request to the `/ping` endpoint.

```bash
curl http://127.0.0.1:8000/ping
```

You should receive the following response:

```json
{"message":"pong"}
```