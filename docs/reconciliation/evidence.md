# FinResolve AI — Evidence Model

## Overview

In FinResolve AI, discrepancies are not abstract assertions. Every discrepancy is backed by first-class, structured **`Evidence`** objects pointing directly to source records, inspected fields, and observed vs expected values.

---

## Evidence Structure

Each `Evidence` record carries:

| Field | Type | Description |
| :--- | :--- | :--- |
| `evidence_id` | `UUID` | Unique evidence identifier |
| `evidence_type` | `EvidenceType` | Classification (`AMOUNT_DIFF`, `MISSING_LINK`, `TEMPORAL_ANOMALY`, `STATUS_CONFLICT`, `FEE_MISMATCH`, `DUPLICATE_ENTRY`, `LEDGER_IMBALANCE`, `REFERENCE_MISMATCH`) |
| `source_record_id` | `str` | Exact identifier of the record providing this evidence |
| `record_type` | `RecordType` | Source record type (`payment`, `settlement`, `fee`, etc.) |
| `field_name` | `str` | The specific attribute inspected (e.g. `net_amount`, `status`, `settled_at`) |
| `observed_value` | `Any` | Actual value observed in data |
| `expected_value` | `Any` | Mechanically calculated expected value |
| `rule_id` | `str` | Evaluating rule identifier |
| `severity` | `Severity` | `INFO`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `strength` | `float` | Confidence weight of the observation ($0.0 \dots 1.0$) |
| `explanation` | `str` | Human and machine-readable explanation |

---

## Severity Criteria

- **`CRITICAL`**: Fundamental accounting violations (e.g. ledger entries with both debit and credit $>0$, processed settlement for failed payment).
- **`HIGH`**: Direct financial net variances, missing settlement records, broken references.
- **`MEDIUM`**: Minor fee calculation differences, temporal delays beyond normal window.
- **`LOW` / `INFO`**: Expected adjustments or informational variances.
