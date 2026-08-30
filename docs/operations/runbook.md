# FinResolve AI — Operational Runbook

## Overview

Step-by-step procedures for standard operations, health checks, troubleshooting, and secret scanning.

---

## 1. Routine Verification Commands

```bash
# Run complete test suite (unit, property, adversarial, security)
source .venv/bin/activate
pytest -v

# Run automated secret scan across repository
python scripts/scan_secrets.py

# Run benchmark evaluation on 1,000 cases
python -m services.reconciliation.evaluate --cases 1000 --seed 42

# Run performance smoke test
python scripts/performance_smoke_test.py
```

---

## 2. Troubleshooting & Diagnostics

### Issue: Health Check Returns 503 / Not Ready
1. Inspect `/ready` response body to identify the failing subsystem.
2. Check environment configuration (`APP_ENV`, `DATABASE_URL`).
3. Check structured logs for startup exception stack traces.

### Issue: High 429 Rate Limit Errors
1. Check `/metrics` counter `http_errors_total`.
2. Inspect if a specific client or IP is exhausting the sliding-window budget.
3. Temporarily adjust `RATE_LIMIT_REQUESTS_PER_MINUTE` if legitimate traffic volume increased.

### Issue: Suspected Audit Tampering
1. Invoke `AuditLogger.verify_integrity()`.
2. If `False`, identify the first `prev_event_hash` mismatch in the chain.
3. Isolate the affected instance and notify security lead.
