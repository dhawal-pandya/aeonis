# Aeonis Pathway: A Developer's Guide

This document outlines the complete workflow of the Aeonis observability platform, from instrumenting an application with the Go SDK to analyzing traces and chatting with your data in the UI.

## 1. Instrumenting Your Application with the Aeonis Go SDK

The first step is to instrument your Go application to send trace data to the Aeonis server. We provide a Go SDK for this purpose.

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

You can run the services individually for more control or use the provided convenience scripts to start and stop everything at once.

### Method 1: Running Services Individually (Manual)

Run each command in a separate terminal window.

#### Step 1: Start the Aeonis Server (Backend)

```bash
cd apps/aeonis-server
source .venv/bin/activate
uvicorn aeonis_server.main:app --reload --port 8000
```

> **Troubleshooting:**
> *   **`uvicorn: command not found`**: Make sure you have activated the Python virtual environment with `source .venv/bin/activate`.
> *   **`Address already in use`**: Another process is using port 8000. Find it with `lsof -ti:8000` and stop it with `kill <PID>`.

#### Step 2: Start the Invoxa Test App (Go Service)

```bash
cd invoxa-test
go run main.go
```

> **Troubleshooting:**
> *   **`listen tcp :8081: bind: address already in use`**: Another process is using port 8081. Find it with `lsof -ti:8081` and stop it with `kill <PID>`.

#### Step 3: Start the Aeonis UI (Frontend)

```bash
cd apps/aeonis-ui
npm run dev
```

> **Troubleshooting:**
> *   **`address already in use`**: Another process is using port 5173. Find it with `lsof -ti:5173` and stop it with `kill <PID>`.

### Method 2: Using the Convenience Scripts

For a simpler experience, you can use the provided shell scripts in the project root to manage all services simultaneously.

*   **To start all services:**
    ```bash
    ./start_all.sh
    ```
*   **To stop all services:**
    ```bash
    ./shutdown_all.sh
    ```

---


## 5. End-to-End Demo Flow with `curl`

Here is a sequence of `curl` commands to simulate a common user flow in the `invoxa-test` application. Running these commands will generate meaningful, interconnected traces that you can explore in the Aeonis UI.

**Note:** You will need to capture the `ID` from the response of one command and use it in the subsequent commands.

### Step 1: Create a New Organization

This command creates a new organization. Note the `ID` in the JSON response.

```bash
curl -X POST http://localhost:8081/organizations \
-H "Content-Type: application/json" \
-d '{
  "name": "Innovate Inc.",
  "billing_email": "billing@innovate.com"
}'
```

**Response Example:**
```json
{"ID":1,"CreatedAt":"...","UpdatedAt":"...","DeletedAt":null,"name":"Innovate Inc.","billing_email":"billing@innovate.com","Users":null,"SubscriptionPlans":null,"Subscriptions":null,"Invoices":null}
```
> **Action:** Copy the `ID` (e.g., `1`) from the response. This is your `ORG_ID`.

### Step 2: Create a New User

Now, create a user associated with the organization you just created.

```bash
# Replace <ORG_ID> with the ID from Step 1
ORG_ID=1

curl -X POST http://localhost:8081/users \
-H "Content-Type: application/json" \
-d '{
  "username": "testuser",
  "email": "test@innovate.com",
  "password": "securepassword123",
  "organization_id": '$ORG_ID'
}'
```
**Response Example:**
```json
{"message":"User created successfully","user_id":1}
```
> **Action:** Copy the `user_id` (e.g., `1`). This is your `USER_ID`.

### Step 3: Create a Subscription Plan

The following commands require authentication. We'll pass the `caller_organization_id` and `caller_user_id` as query parameters to simulate an authenticated session.

```bash
# Replace <ORG_ID> with your Organization ID
ORG_ID=1
USER_ID=1

curl -X POST "http://localhost:8081/subscription_plans?caller_organization_id=$ORG_ID&caller_user_id=$USER_ID" \
-H "Content-Type: application/json" \
-d '{
    "name": "Pro Plan",
    "description": "The professional tier plan.",
    "price": 99.99,
    "currency": "USD",
    "interval": "monthly",
    "organization_id": '$ORG_ID'
}'
```
**Response Example:**
```json
{"message":"Subscription plan created successfully","plan_id":1}
```
> **Action:** Copy the `plan_id` (e.g., `1`). This is your `PLAN_ID`.

### Step 4: Subscribe the Organization to the Plan

This action will create a `Subscription` and the first `Invoice`.

```bash
# Replace with your IDs
ORG_ID=1
USER_ID=1
PLAN_ID=1

curl -X POST "http://localhost:8081/subscribe?caller_organization_id=$ORG_ID&caller_user_id=$USER_ID" \
-H "Content-Type: application/json" \
-d '{
    "organization_id": '$ORG_ID',
    "subscription_plan_id": '$PLAN_ID',
    "user_id": '$USER_ID'
}'
```
**Response Example:**
```json
{"message":"Subscription and initial invoice created successfully","subscription_id":1,"invoice_id":1}
```
> **Action:** Copy the `invoice_id` (e.g., `1`). This is your `INVOICE_ID`.

### Step 5: Pay the Invoice

Finally, simulate paying the invoice that was just created.

```bash
# Replace with your IDs
ORG_ID=1
USER_ID=1
INVOICE_ID=1

curl -X POST "http://localhost:8081/pay_invoice?caller_organization_id=$ORG_ID&caller_user_id=$USER_ID" \
-H "Content-Type: application/json" \
-d '{
    "invoice_id": '$INVOICE_ID',
    "user_id": '$USER_ID',
    "amount": 99.99,
    "currency": "USD",
    "transaction_id": "txn_123abc456def",
    "payment_method": "credit_card"
}'
```

### Step 6: View Traces

After running these commands, go to the **Aeonis UI** at `http://localhost:5173`. Enter your project ID and click **Fetch Traces**. You will see new traces corresponding to each `curl` command you executed. Click on them to see the detailed waterfall view and use the AI Chat to ask questions about them.

```
