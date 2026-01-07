# Use the official Python runtime as a parent image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create data directory
RUN mkdir -p .data

# Health check
HEALTHCHECK --interval=5m --timeout=30s --start-period=30s --retries=2 \
    CMD curl -f http://localhost:8000/health || exit 1 || echo "Monitor running"

# Run the scheduler
CMD ["python3", "scheduler.py"]
