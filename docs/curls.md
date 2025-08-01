## Step 1: Start the Aeonis Server (Backend)

This command starts the Python-based backend server. It's crucial to run it from the correct directory to ensure all modules are found.

Here is a sequence of `curl` commands to simulate a common user flow in the `invoxa-test` application. Running these commands will generate meaningful, interconnected traces that you can explore in the Aeonis UI.

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


**Note:** You will need to capture the `ID` from the response of one command and use it in the subsequent commands.

## Step 2: Onboard New Project


```bash
curl -X POST http://localhost:8000/v1/projects \
-H "Content-Type: application/json" \
-d '{
  "name": "Invoxa Test Project",
  "git_repo_url": "https://github.com/dhawal-pandya/Invoxa"
}'
```

**Response Example:**
```json
{
    "api_key": "eD_FJfw-A_6yCyih8HTaJChPFJroKcx2U2r3ghMumXA",
    "name": "Invoxa Test Project",
    "is_private": false,
    "git_repo_url": "https://github.com/dhawal-pandya/invoxa-test.git",
    "id": "47dfe55d-6c00-40d8-b03d-51123acfdd8a",
    "git_ssh_key": null
}
```
> **Action:** Create a new project in Aeonis. **Save the `id` and `api_key` from the response.**


## Step 3: Start the Invoxa Test App (Go Service)

### Set Environment Variables

Before running your application, you must set the following environment variables:

```bash
# The API key you saved from step 2
export AEONIS_API_KEY="your-api-key-goes-here"
export AEONIS_API_KEY="eD_FJfw-A_6yCyih8HTaJChPFJroKcx2U2r3ghMumXA"

# The current Git commit hash of your application
export AEONIS_COMMIT_ID=$(git rev-parse HEAD)
```

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

## Step 4: Create a New organisation

Now, create a new organization

```bash
curl -X POST http://localhost:8081/organizations \
    -H "Content-Type: application/json" \
    -d '{
      "name": "My Awesome Company",
      "billing_email": "billing@example.com"
    }'
```
**Response Example:**
```json
{
    "ID": 1,
    "CreatedAt": "2025-07-31T20:08:47.291785+05:30",
    "UpdatedAt": "2025-07-31T20:08:47.291785+05:30",
    "DeletedAt": null,
    "Name": "My Awesome Company",
    "BillingEmail": "billing@example.com",
    "Users": null,
    "Subscriptions": null,
    "SubscriptionPlans": null,
    "Invoices": null
} 
```

## Step 5: Create a New User

Now, create a user associated with the organization you just created.

```bash
curl -X POST http://localhost:8081/users \
-H "Content-Type: application/json" \
-d '{
  "username": "testuser",
  "email": "test@innovate.com",
  "password": "securepassword123",
  "organization_id": '1'
}'
```
**Response Example:**
```json
{"message":"User created successfully","user_id":1}
```
> **Action:** Copy the `user_id` (e.g., `1`). This is your `USER_ID`.

## Step 6: Create a Subscription Plan

The following commands require authentication. We'll pass the `caller_organization_id` and `caller_user_id` as query parameters to simulate an authenticated session.

```bash

curl -X POST "http://localhost:8081/subscription_plans?caller_organization_id=1&caller_user_id=1" \
-H "Content-Type: application/json" \
-d '{
    "name": "Pro Plan",
    "description": "The professional tier plan.",
    "price": 99.99,
    "currency": "USD",
    "interval": "monthly",
    "organization_id": '1'
}'
```
**Response Example:**
```json
{"message":"Subscription plan created successfully","plan_id":1}
```
> **Action:** Copy the `plan_id` (e.g., `1`). This is your `PLAN_ID`.

## Step 7: Subscribe the Organization to the Plan

This action will create a `Subscription` and the first `Invoice`.

```bash
curl -X POST "http://localhost:8081/subscribe?caller_organization_id=1&caller_user_id=1" \
-H "Content-Type: application/json" \
-d '{
    "organization_id": '1',
    "subscription_plan_id": '1',
    "user_id": '1'
}'
```
**Response Example:**
```json
{"message":"Subscription and initial invoice created successfully","subscription_id":1,"invoice_id":1}
```
> **Action:** Copy the `invoice_id` (e.g., `1`). This is your `INVOICE_ID`.

## Step 8: Pay the Invoice

Finally, simulate paying the invoice that was just created.

```bash
curl -X POST "http://localhost:8081/pay_invoice?caller_organization_id=1&caller_user_id=1" \
-H "Content-Type: application/json" \
-d '{
    "invoice_id": '1',
    "user_id": '1',
    "amount": 99.99,
    "currency": "USD",
    "transaction_id": "txn_123abc456def",
    "payment_method": "credit_card"
}'
```

## Step 9: View Traces

After running these commands, go to the **Aeonis UI** at `http://localhost:5173`. Enter your project ID and click **Fetch Traces**. You will see new traces corresponding to each `curl` command you executed. Click on them to see the detailed waterfall view and use the AI Chat to ask questions about them.

```bash
curl -X POST -H "Content-Type: application/json" -d '{
    "message": "Investigate thoroughly the slowest trace of this project?"
}' http://127.0.0.1:8000/v1/projects/47dfe55d-6c00-40d8-b03d-51123acfdd8a/chat
```

```bash
curl -X POST -H "Content-Type: application/json" -d '{
    "message": "I am seeing high latency in the `create_organization` endpoint. Can you analyze the code at commit e43127c676f43f191e1f9cccb3a568e21b46681c and tell me what might be causing it?"
}' http://127.0.0.1:8000/v1/projects/47dfe55d-6c00-40d8-b03d-51123acfdd8a/chat
```