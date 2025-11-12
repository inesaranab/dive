FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies and UV
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files and README (needed for build)
COPY pyproject.toml uv.lock README.md ./

# Install dependencies using UV
RUN uv sync --no-dev

# Copy application code
COPY app/ ./app/
COPY dataset/ ./dataset/
COPY scripts/ ./scripts/

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health')"

# Run the application with UV (use explicit shell)
CMD ["/bin/sh", "-c", "uv run uvicorn app.main:app --host 0.0.0.0 --port 8000"]

