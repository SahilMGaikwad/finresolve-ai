# FinResolve AI — Normalization

## Purpose

Normalization converts records from heterogeneous source systems
into a single canonical internal representation.

## What Gets Normalized

### 1. Field Names

Source systems use different field names for the same concept.
Mappings are defined per source system in `services/normalization/field_mappings.py`.

Example (Razorpay → canonical):
```
id          → payment_id
amount      → amount
created_at  → captured_at
notes       → metadata
```

Fields not in the mapping pass through unchanged.

### 2. Monetary Amounts

All amounts are normalised to integer minor currency units:

| Currency | Minor Unit | Example |
|----------|-----------|---------|
| INR | paise | ₹500.00 → 50000 |
| USD | cents | $10.50 → 1050 |
| EUR | cents | €25.00 → 2500 |

**No float arithmetic.** If a float is detected in a monetary amount
field, normalisation is refused with a `NormalizationError`.

### 3. Timestamps

All timestamps are normalised to UTC:

| Input | Output |
|-------|--------|
| `2026-01-15T16:00:00+05:30` | `2026-01-15T10:30:00+00:00` |
| `2026-01-15T10:30:00` (naive) | `2026-01-15T10:30:00+00:00` (assumed UTC) |
| `1768566600` (unix) | `2026-01-15T10:30:00+00:00` |

Naive timestamps (no timezone info) are assumed to be UTC.

### 4. Content Hash

A deterministic hash is computed from `(source_system, source_record_id, schema_version)`
for idempotent ingestion. The hash is SHA-256.

## Canonical Record

After normalisation, every record becomes a `CanonicalRecord`:

| Field | Description |
|-------|-------------|
| canonical_id | Internal UUID |
| record_type | Original record type |
| source_record | Full normalised record as dict |
| amount | Primary amount (Money) |
| merchant_id | Merchant identifier |
| timestamp | Primary timestamp (UTC) |
| reference_ids | Map of reference type → ID |
| provenance | Full ingestion provenance |
| content_hash | Idempotency hash |

## Version Scheme

- **Schema version**: Semantic versioning (1.0.0). Tracks changes to the
  data model schemas.
- **Normalization version**: Semantic versioning (1.0.0). Tracks changes
  to normalisation logic (field mappings, coercion rules).

Both versions are recorded in provenance metadata.

## Edge Cases

1. **Missing timestamp**: `NormalizationError` is raised.
2. **Missing amount**: `NormalizationError` is raised.
3. **Float amount**: `NormalizationError` is raised (never silently truncated).
4. **Unknown source system**: Empty mapping is used (passthrough).
5. **Naive datetime**: Assumed UTC (logged as warning in production).
