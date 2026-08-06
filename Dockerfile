# Use Python 3.11 slim image for fast build and small container footprint
FROM python:3.11-slim

# Prevent Python from writing .pyc files & enable unbuffered logging
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=7860 \
    HOST=0.0.0.0

WORKDIR /app

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency management
RUN pip install --no-cache-dir uv

# Copy project specification files
COPY pyproject.toml .
COPY README.md .

# Copy source code
COPY src/ ./src/
COPY main.py .

# Install Python dependencies using uv
RUN uv pip install --system --no-cache -e .

# Expose container port
EXPOSE 7860

# Command to run the application
CMD ["python", "main.py"]
