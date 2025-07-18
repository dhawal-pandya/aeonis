#!/bin/bash
# This script starts all the necessary services for the Aeonis demo.

echo "🚀 Starting all Aeonis services..."

# 1. Start Aeonis Server (FastAPI)
echo "   - Starting Aeonis Server..."
(cd apps/aeonis-server && source .venv/bin/activate && uvicorn aeonis_server.main:app --port 8000 &)
sleep 5 # Give the server a moment to start up

# 2. Start Invoxa Test App (Go)
echo "   - Starting Invoxa Test App..."
(cd invoxa-test && go run main.go &)
sleep 2

# 3. Start Aeonis UI (Vite)
echo "   - Starting Aeonis UI..."
(cd apps/aeonis-ui && npm run dev &)
sleep 5

echo "✅ All services are starting in the background."
echo "   - Aeonis Server should be on http://localhost:8000"
echo "   - Invoxa Test App should be on http://localhost:8081"
echo "   - Aeonis UI should be on http://localhost:5173"
echo "Run ./shutdown_all.sh to stop all services."
