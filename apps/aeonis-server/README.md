# Aeonis Server

This document provides quick instructions on how to run and test the Aeonis server.

## How to Run

1.  **Install Dependencies**:
    Navigate to the `apps/aeonis-server/` directory and install the required Python packages:
    ```bash
    python3 -m pip install -r requirements.txt
    ```

2.  **Start the Server**:
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
