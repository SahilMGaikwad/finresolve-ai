# FinResolve AI — Deployment Guide

## Overview

FinResolve AI is designed for containerized deployment with FastAPI. This document describes deployment strategies across local, staging, and production environments.

---

## 1. Local Development Deployment

```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Copy and customize environment variables
cp .env.example .env

# 3. Run FastAPI development server
uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 2. Docker Container Deployment

```bash
# Build production Docker image
docker build -t finresolve-ai:latest -f apps/api/Dockerfile .

# Run container with resource limits and non-root execution
docker run -d \
  --name finresolve-api \
  --p 8000:8000 \
  --memory="1g" \
  --cpus="1.0" \
  --env-file .env \
  finresolve-ai:latest
```

---

## 3. Health & Readiness Verification

- **Liveness probe**: `GET /health` (returns 200 OK if process is running).
- **Readiness probe**: `GET /ready` (returns 200 OK when dependencies and configuration are verified).
- **Container health check**: Handled automatically via Docker `HEALTHCHECK`.

---

## 4. Production Rollback Strategy

1. Deploy new container image alongside existing replica.
2. Direct traffic to new replica only after `/ready` returns HTTP 200.
3. If errors spike (`http_errors_total` exceeds alert threshold), immediately switch ingress routing back to previous stable container tag.
