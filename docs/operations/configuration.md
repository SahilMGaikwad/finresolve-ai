# FinResolve AI — Configuration Reference

## Overview

All configuration parameters are centrally defined in [`apps/api/config.py`](file:///Users/sahilgaikwad/finresolve-ai/apps/api/config.py) and loaded via environment variables.

---

## Configuration Variables

| Variable | Type | Default | Production Requirement | Description |
| :--- | :--- | :--- | :--- | :--- |
| `APP_NAME` | `str` | `finresolve-ai` | Optional override | Application identifier for logging and metrics |
| `APP_ENV` | `str` | `development` | `production` | Environment mode (`development`, `staging`, `production`, `test`) |
| `APP_VERSION` | `str` | `0.1.0` | Injected by CI | Release version string |
| `LOG_LEVEL` | `str` | `INFO` | `INFO` / `WARN` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `DEBUG` | `bool` | `false` | **MUST BE FALSE** | Enables FastAPI interactive `/docs` and debug outputs |
| `API_HOST` | `str` | `0.0.0.0` | `0.0.0.0` | Network binding interface |
| `API_PORT` | `int` | `8000` | `8000` | Listening TCP port |
| `CORS_ORIGINS` | `str` | `http://localhost:3000` | Domain whitelist | Comma-separated list of allowed frontend origins |
| `TRUSTED_HOSTS` | `str` | `localhost,127.0.0.1` | Domain whitelist | Comma-separated allowed HTTP Host header values |
| `MAX_REQUEST_SIZE_BYTES` | `int` | `10485760` (10MB) | `10485760` | Maximum allowed request payload size in bytes |
| `AUTH_ENABLED` | `bool` | `false` | `true` | Enforces Bearer token authentication on protected routes |
| `AUTH_SECRET_KEY` | `str` | `dev-secret...` | **STRONG KEY (32+ chars)** | Secret key used for cryptographic token verification |
| `RATE_LIMIT_ENABLED` | `bool` | `true` | `true` | Enforces sliding-window rate limits |
| `RATE_LIMIT_REQUESTS_PER_MINUTE` | `int` | `120` | Scaled to tier | Maximum requests permitted per client per minute |
| `DATABASE_URL` | `str` | `postgresql://...` | **LIVE SECURE POSTGRES URL** | Connection string for persistent database storage |
| `POLICY_AUTO_RESOLVE_ENABLED` | `bool` | `false` | `false` (in prototype) | Flag for autonomous resolution gating |
