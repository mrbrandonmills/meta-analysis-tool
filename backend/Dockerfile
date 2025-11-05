# Backend Dockerfile
# NOTE: This assumes Railway root directory is set to "backend"
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements (use production requirements for faster builds)
COPY requirements.production.txt ./requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app ./app

# Expose port
EXPOSE 8000

# Run the application
# Use shell form to allow $PORT environment variable expansion
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
