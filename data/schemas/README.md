# Data — Schemas

This directory contains Pydantic and JSON schemas for all financial record types
used by FinResolve AI.

## Planned Schemas (Phase 2+)

- `payment.py` — Payment record schema
- `order.py` — Order record schema
- `settlement.py` — Settlement record schema
- `refund.py` — Refund record schema
- `fee.py` — Fee/charge record schema
- `ledger_entry.py` — Ledger entry schema
- `payout.py` — Payout record schema
- `canonical.py` — Canonical normalized record schema
- `evidence.py` — Evidence record schema
- `hypothesis.py` — Hypothesis/diagnosis schema
- `resolution.py` — Resolution candidate schema
- `audit.py` — Audit log entry schema

All monetary amounts will be represented as integers in minor currency units (paise for INR).
