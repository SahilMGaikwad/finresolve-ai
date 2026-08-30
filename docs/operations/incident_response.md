# FinResolve AI — Incident Response Plan

## Overview

This runbook outlines incident response procedures for FinResolve AI financial operations and security events.

---

## 1. Severity Classification

- **SEV-1 (Critical)**: Active security breach, potential unauthorized financial modification, or total reconciliation service outage.
- **SEV-2 (High)**: Spike in reconciliation rule failures, database connection errors, or rate limit throttling on ingestion.
- **SEV-3 (Medium)**: Transient latency spikes or non-critical background metric export failures.

---

## 2. Response Steps

1. **Identification**: Alert triggered via `/metrics` monitor or customer report.
2. **Containment**:
   - For suspected data tampering or exploit: immediately set `POLICY_AUTO_RESOLVE_ENABLED=false` and isolate API instance.
   - For ingestion overload: scale rate limits via environment variable or API gateway.
3. **Investigation**:
   - Inspect append-only audit trail via `AuditLogger.get_events()`.
   - Run cryptographic integrity check: `AuditLogger.verify_integrity()`.
   - Review structured JSON logs using `request_id`.
4. **Remediation**:
   - Rollback to previous container image tag if bug was introduced in deployment.
   - Resubmit failed cases through idempotency layer.
5. **Post-Mortem**: Document root cause, impact, timeline, and preventive actions within 48 hours.
