# Aeonis Project Onboarding Guide

This guide provides a complete walkthrough for onboarding a new project to the Aeonis observability platform.

## 1. Start the Aeonis Server

The Aeonis server is the central component that ingests and processes all trace data.

First, ensure all dependencies are installed and the database is initialized.

```bash
# Navigate to the server directory
cd apps/aeonis-server

# Install dependencies
.venv/bin/pip install -r requirements.txt

# Run the database initialization script
.venv/bin/python init_db_script.py
```

Now, start the server:

```bash
uvicorn aeonis_server.main:app --reload --port 8000
```

To verify the server is running, open a new terminal and run:

```bash
curl http://127.0.0.1:8000/ping
```

You should see a `{"message":"pong"}` response.

## 2. Create a New Project

Next, you need to create a project in Aeonis. This will generate an API key that your application will use to send data.

```bash
curl -X POST http://localhost:8000/v1/projects \
-H "Content-Type: application/json" \
-d '{
  "name": "My Awesome App",
  "git_repo_url": "https://github.com/your-username/my-awesome-app.git"
}'
```

This will return a JSON object containing your new project's details, including the crucial `api_key`.

**Save the `api_key` and the `id` from the response. You will need them in the next step.**

## 3. Instrument Your Go Application

Now, you will configure your Go application to send traces to the Aeonis server.

### Add the Aeonis Go SDK to your project:

```bash
go get github.com/aeonis/tracer-sdk/go
```

### Configure the Tracer

In your application's main entry point (e.g., `main.go`), initialize the Aeonis tracer.

```go
package main

import (
    "os"
    "github.com/aeonis/tracer-sdk/go"
)

func main() {
    // 1. Initialize the Aeonis Tracer
    // It's recommended to use environment variables for configuration.
    tracer, err := aeonis.NewTracer(
        "My Awesome App", // The name of your service
        os.Getenv("AEONIS_API_KEY"),
        aeonis.WithExporterURL("http://localhost:8000/v1/traces"),
        aeonis.WithCommitID(os.Getenv("AEONIS_COMMIT_ID")),
    )
    if err != nil {
        // Handle error
    }
    defer tracer.Shutdown()

    // ... your application code ...
}
```

### Set Environment Variables

Before running your application, you must set the following environment variables:

```bash
# The API key you saved from step 2
export AEONIS_API_KEY="your-api-key-goes-here"

# The current Git commit hash of your application
export AEONIS_COMMIT_ID=$(git rev-parse HEAD)
```

### Add Tracing to your Code

To trace a function, use the `tracer.Start()` method.

```go
import (
    "context"
    "net/http"
)

func handleOrder(w http.ResponseWriter, r *http.Request) {
    // Start a new span for this function
    ctx, span := tracer.Start(r.Context(), "handleOrder")
    defer span.End()

    // ... your function logic ...

    // You can add attributes to your span
    span.SetAttribute("http.method", "GET")

    // If an error occurs, you can record it
    if err != nil {
        span.SetError(err.Error(), "")
    }
}
```

## 4. Run Your Application and View Traces

Run your instrumented Go application. As it runs, it will send trace data to the Aeonis server.

You can then view your traces in the Aeonis UI or by querying the API:

```bash
# Use the project ID you saved from step 2
curl http://localhost:8000/v1/projects/{your-project-id}/traces
```

You have now successfully onboarded your application to Aeonis!
