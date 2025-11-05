#!/bin/bash
# Railway startup script
# Ensures proper working directory and PYTHONPATH for the application

# Set the working directory to the backend folder
cd /app || cd "$(dirname "$0")" || exit 1

# Export PYTHONPATH to ensure app module can be found
export PYTHONPATH="${PYTHONPATH}:/app"

# Start uvicorn with the FastAPI app
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
