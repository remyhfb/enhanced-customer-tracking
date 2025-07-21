FROM python:3.11-slim

# Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

# Copy requirements and install Python dependencies with minimal cache
COPY requirements.txt .
RUN pip install --no-cache-dir --no-deps -r requirements.txt \
    && pip cache purge

# Copy application code
COPY src/ ./src/

# Expose port
EXPOSE 5000

# Set environment variables for minimal memory usage
ENV FLASK_APP=src/main.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Run with minimal Gunicorn configuration for 600MB limit
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "1", "--timeout", "60", "--max-requests", "50", "--preload", "--worker-class", "sync", "src.main:app"]

