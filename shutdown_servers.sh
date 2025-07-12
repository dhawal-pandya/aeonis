#!/bin/bash
# This script finds and kills processes listening on specified ports.

PORTS=(8000 8001 5173 3000 3001 8080)
PIDS_KILLED=false

echo "Shutting down servers..."

for PORT in "${PORTS[@]}"; do
  # Find the PID of the process listening on the port
  PID=$(lsof -t -i:$PORT)

  if [ -n "$PID" ]; then
    echo "Found process with PID $PID on port $PORT. Terminating..."
    # Kill the process
    kill -9 $PID
    PIDS_KILLED=true
  else
    echo "No process found on port $PORT."
  fi
done

if [ "$PIDS_KILLED" = true ]; then
  echo "Server shutdown process complete."
else
  echo "No running servers found on specified ports."
fi
