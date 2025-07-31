# Developer's Guide

## 1. Instrumenting Your Application with the Aeonis Go SDK

The first step is to instrument your Go application to send trace data to the Aeonis server. Use Go SDK for this purpose.

### 1.1. How the SDK Works

The SDK is located in `packages/tracer-sdk/go`. Its key components are:

-   **`tracer.go`**: The main entry point for creating spans. The `Tracer` object is responsible for starting and managing spans.
-   **`span.go`**: Defines the `Span` struct, which represents a single unit of work (e.g., an HTTP request, a database query).
-   **`exporter.go`**: Contains logic for sending spans to a backend. The `HTTPExporter` sends spans to the Aeonis server over HTTP.
-   **`contrib/gorm.go`**: Provides a GORM plugin to automatically instrument database queries.

### 1.2. Example Usage: The `invoxa-test` Application

The `invoxa-test` application is a real-world example of how to use the Aeonis Go SDK. Here's how it's set up:

**File: `invoxa-test/main.go`**

1.  **Initialization**: A `Tracer` is initialized with an `HTTPExporter` that points to the Aeonis server's `/v1/traces` endpoint. A PII sanitizer is also configured to prevent sensitive data from being sent in traces.

    ```go
    exporter := sdktracer.NewHTTPExporter("http://localhost:8000/v1/traces", "YOUR_API_KEY")
    sanitizer := sdktracer.NewPIISanitizer()
    handlers.Tracer = sdktracer.NewTracerWithExporter("invoxa-test", exporter, sanitizer)
    ```

2.  **Gin Middleware**: A Gin middleware is used to automatically create a "root" span for every incoming HTTP request. This span captures essential information like the HTTP method, URL, and status code.

    ```go
    r.Use(func(c *gin.Context) {
        ctx, span := handlers.Tracer.StartSpan(c.Request.Context(), c.Request.URL.Path)
        defer span.End()
        // ... set attributes ...
        c.Request = c.Request.WithContext(ctx)
        c.Next()
    })
    ```

3.  **Custom Spans**: For more detailed insights, you can create custom "child" spans for specific business logic.

    **File: `invoxa-test/handlers/billing_handlers.go`**

    ```go
    func Subscribe(c *gin.Context) {
        _, span := Tracer.StartSpan(c.Request.Context(), "Subscribe")
        defer span.End()
        // ...
    }
    ```

4.  **Automatic Function Tracing**: The `TraceFunc` utility can automatically wrap a function call in a span, capturing its arguments and return values.

    **File: `invoxa-test/handlers/billing_handlers.go`**

    ```go
    out := Tracer.TraceFunc(c.Request.Context(), validateSubscriptionRequest, c, req)
    ```

5.  **Database Instrumentation**: The GORM plugin automatically creates spans for all database queries.

    **File: `invoxa-test/database/database.go`**

    ```go
    if err := db.Use(&contrib.GormTracer{}); err != nil {
        log.Fatalf("Failed to use gorm tracer: %v", err)
    }
    ```

## 2. The Aeonis Server: Ingesting and Processing Traces

The `aeonis-server` is a FastAPI application responsible for receiving, storing, and serving trace data.

### 2.1. API Endpoints

The server exposes a REST API for managing projects and traces.

-   **`POST /v1/traces`**: The endpoint where the Go SDK sends trace data.
-   **`GET /v1/projects/{project_id}/traces`**: Retrieves all traces for a project.
-   **`GET /v1/traces/{trace_id}`**: Retrieves all spans for a specific trace.
-   **`POST /v1/projects/{project_id}/chat`**: The AI chat endpoint.

### 2.2. Data Storage

Trace data is stored in a PostgreSQL database using SQLAlchemy. The database schema is defined in `aeonis_server/db/models.py` with two main tables: `projects` and `spans`.

### 2.3. The Mission Control Platform (MCP)

The MCP is the AI-powered component of the Aeonis server. It uses the Gemini Pro model to provide a natural language interface for querying trace data.

-   **`llm_service.py`**: Orchestrates the chat interaction, including calling tools.
-   **`db_tools.py`**: Defines the functions (tools) that the AI model can use to query the database, such as `get_traces_by_project_id` and `execute_sql_query`.

## 3. The Aeonis UI: Visualizing and Chatting with Your Data

The `aeonis-ui` is a React application that provides a user-friendly interface for exploring traces and interacting with the AI chat.

### 3.1. Trace Visualization

-   **Trace List**: The UI fetches and displays a list of the most recent traces for a selected project.
-   **Waterfall View**: When a trace is selected, the UI renders a detailed waterfall view of all the spans in that trace. The `TraceDetailView.jsx` and `SpanBar.jsx` components are responsible for this.

### 3.2. AI Chat

The `Chatbox.jsx` component provides a chat interface where you can ask questions about your trace data in natural language. The UI sends your questions to the `aeonis-server`'s chat endpoint and displays the AI's response.

## 4. Running the Application

Run each command in a separate terminal window.

#### Step 1: Start the Aeonis Server (Backend)

This command starts the Python-based backend server. It's crucial to run it from the correct directory to ensure all modules are found.

**Command Breakdown:**

For a clean test run, remove the log files from previous sessions.

```bash
# In the project root directory
rm -f apps/aeonis-server/uvicorn.log
rm -f invoxa-test/invoxa.log
```

---

```bash
cd apps/aeonis-server

source .venv/bin/activate

uvicorn aeonis_server.main:app --reload --port 8000 --log-config uvicorn_log_config.json
```

*   **`cd apps/aeonis-server`**: This is a critical first step. It changes your terminal's current directory to the root of the `aeonis-server` application. Running the server from here ensures that Python can correctly locate the `aeonis_server` module.
*   **`source .venv/bin/activate`**: This command activates the project's dedicated Python virtual environment. This is important because it makes sure you are using the correct versions of all dependencies (like FastAPI, Uvicorn, etc.) and places the `uvicorn` executable in your `PATH`.
*   **`uvicorn aeonis_server.main:app ...`**: This is the core command that runs the server.
    *   `uvicorn`: The name of the high-performance ASGI server we use to run our FastAPI application.
    *   `aeonis_server.main:app`: This tells Uvicorn where to find the application instance. It means: "Within the `aeonis_server` package, look in the `main.py` file for a variable named `app`."
    *   `--reload`: This is a development-friendly flag. It tells Uvicorn to automatically restart the server whenever it detects a change in the source code.
    *   `--port 8000`: This specifies that the server should listen for incoming requests on port 8000.

> **Troubleshooting:**
> *   **`uvicorn: command not found`**: This means the `uvicorn` executable is not in your shell's `PATH`. **Solution:** You have likely forgotten to activate the virtual environment. Run `source .venv/bin/activate` and try again.
> *   **`Address already in use`**: This error means another program is already using port 8000. **Solution:** Find the conflicting process with `lsof -ti:8000` and stop it with `kill <PID>`, where `<PID>` is the number returned by the first command.
> *   **Server returns `Internal Server Error`**: If the server starts but API calls fail with a 500 error, it indicates a bug in the application code. **Solution:** Check the terminal window where the server is running. FastAPI will print a detailed traceback of the error. If you are running the server in the background, check the contents of the `apps/aeonis-server/uvicorn.log` file to find the traceback. This was key to debugging the `MALFORMED_FUNCTION_CALL` error.

* **Verification**

```bash
curl http://127.0.0.1:8000/ping
```

**Expected Output:** `{"message":"pong"}`

* **Run this to clear Aeonis DB**
```bash
curl -X POST http://localhost:8000/v1/debug/clear-database
```


#### Step 2: Start the Invoxa Test App (Go Service)

```bash
cd invoxa-test
go run main.go
```

> **Troubleshooting:**
> *   **`listen tcp :8081: bind: address already in use`**: Another process is using port 8081. Find it with `lsof -ti:8081` and stop it with `kill <PID>`.


* **Verification**

```bash
curl http://127.0.0.1:8081/ping
```

**Expected Output:** `{"message":"pong"}`

* **Run this to clear Invoxa DBs**
```bash
curl -X POST http://localhost:8081/admin/clear_db
```


#### Step 3: Start the Aeonis UI (Frontend)

```bash
cd apps/aeonis-ui
npm run dev
```

> **Troubleshooting:**
> *   **`address already in use`**: Another process is using port 5173. Find it with `lsof -ti:5173` and stop it with `kill <PID>`.


<br>
