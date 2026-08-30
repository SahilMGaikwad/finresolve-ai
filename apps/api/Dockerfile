# =========================================================================
# FinResolve AI — Hardened Multi-Stage Production Container
# =========================================================================

# ---- Stage 1: Build Dependencies ----
FROM python:3.13-slim AS builder

WORKDIR /build

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY apps/api/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ---- Stage 2: Runtime Image ----
FROM python:3.13-slim AS runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/finresolve/.local/bin:${PATH}"

# Install curl for container health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create dedicated non-root user and group
RUN groupadd -g 10001 finresolve && \
    useradd -u 10001 -g finresolve -s /bin/bash -m finresolve

# Copy installed Python packages from builder stage
COPY --from=builder --chown=finresolve:finresolve /root/.local /home/finresolve/.local

# Copy application source code
COPY --chown=finresolve:finresolve apps /app/apps
COPY --chown=finresolve:finresolve data /app/data
COPY --chown=finresolve:finresolve services /app/services

# Switch to non-root user
USER finresolve

# Expose API port
EXPOSE 8000

# Health check instruction
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production command with non-debug settings
CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--no-access-log"]
