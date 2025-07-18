#!/bin/bash
# This script shuts down all services started by start_all.sh.

echo "🛑 Shutting down all Aeonis services..."

# Find and kill processes by the command they are running
# This is more robust than storing PIDs.
pkill -f "uvicorn aeonis_server.main:app"
pkill -f "go run main.go"
pkill -f "vite"

# Force kill any remaining Go processes on port 8081 as a fallback
lsof -ti:8081 | xargs kill -9

echo "✅ All services stopped."
