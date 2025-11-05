#!/bin/sh
# Railway startup script for Meta Analysis Tool Backend
# Uses /bin/sh for compatibility with minimal Docker images
# Runs uvicorn with production settings

set -e  # Exit on any error

# Verify virtual environment is accessible
if [ ! -d "/opt/venv" ]; then
    echo "ERROR: Virtual environment not found at /opt/venv"
    exit 1
fi

# Ensure PATH includes virtual environment binaries
export PATH="/opt/venv/bin:$PATH"

# Verify uvicorn is available
if ! command -v uvicorn >/dev/null 2>&1; then
    echo "ERROR: uvicorn not found in PATH"
    exit 1
fi

# Set default PORT if not provided by Railway
PORT="${PORT:-8000}"

# Verify we're in the correct directory
if [ ! -d "/app/app" ]; then
    echo "ERROR: Application directory /app/app not found"
    exit 1
fi

# Export PYTHONPATH to ensure app module can be found
export PYTHONPATH="/app:${PYTHONPATH}"

# Log startup information
echo "Starting Meta Analysis Tool Backend API..."
echo "Working directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Uvicorn location: $(which uvicorn)"
echo "Port: ${PORT}"
echo "Python path: ${PYTHONPATH}"

# Run database migrations
echo "Running database migrations..."
if command -v alembic >/dev/null 2>&1; then
    alembic upgrade head
    if [ $? -eq 0 ]; then
        echo "✓ Database migrations completed successfully"
    else
        echo "WARNING: Database migrations failed, but continuing startup"
    fi
else
    echo "WARNING: alembic not found, skipping migrations"
fi

# Start uvicorn with production-optimized settings
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port "${PORT}" \
    --workers 2 \
    --loop uvloop \
    --log-level info \
    --no-access-log \
    --proxy-headers \
    --forwarded-allow-ips "*"
