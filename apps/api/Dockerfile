# ============================================
# FinResolve AI — API Dockerfile
# ============================================
# Multi-stage build for the FastAPI backend.
# Phase 1: minimal image for development.
# ============================================

FROM python:3.11-slim AS base

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies (minimal)
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# ---- Dependencies stage ----
FROM base AS dependencies

COPY apps/api/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# ---- Application stage ----
FROM dependencies AS app

# Copy application code
COPY apps/ /app/apps/
COPY services/ /app/services/
COPY ml/ /app/ml/
COPY data/ /app/data/

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run with uvicorn
CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
