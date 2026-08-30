# FinResolve AI — Monitoring & Observability Guide

## Overview

FinResolve AI exposes application metrics via `GET /metrics` and structured JSON logs with correlation IDs.

---

## 1. Key Application Metrics

| Metric Name | Type | Description | Alert Threshold |
| :--- | :--- | :--- | :--- |
| `health_checks_total` | Counter | Total liveness probe requests | Anomaly if zero over 5 mins |
| `readiness_checks_total` | Counter | Total readiness probe requests | Anomaly if zero over 5 mins |
| `http_requests_total` | Counter | Total HTTP requests handled | Spike or drop anomaly |
| `http_errors_total` | Counter | HTTP 4xx and 5xx errors by status code | Alert if 5xx error rate $> 1\%$ |
| `reconciliation_cases_total` | Counter | Total cases reconciled | Throughput tracking |
| `discrepancies_detected_total` | Counter | Total discrepancies identified | Discrepancy rate spike |
| `http_request_duration_seconds` | Histogram | Request latency (p50, p95, mean) | Alert if p95 $> 500\text{ ms}$ |

---

## 2. Structured JSON Logging

All logs are emitted to `stdout` in structured JSON format with sensitive credential scrubbing:

```json
{
  "timestamp": "2026-08-30T12:00:00.000000+00:00",
  "level": "INFO",
  "logger": "finresolve.reconciliation.engine",
  "service": "finresolve-ai",
  "message": "Reconciliation concluded with status RECONCILED",
  "request_id": "req_8f7b2c91a0",
  "case_id": "CASE-000042"
}
```

---

## 3. Alerts & Recommended SLOs

- **Availability SLO**: 99.9% successful responses on `/health` and `/ready`.
- **Latency SLO**: 95% of deterministic reconciliation requests complete in $< 100\text{ ms}$.
- **Error Budget**: Trigger incident if 500 error count exceeds 10 per minute.
