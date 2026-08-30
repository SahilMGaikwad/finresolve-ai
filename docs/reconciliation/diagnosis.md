# FinResolve AI — Deterministic Diagnosis & Root-Cause Hypotheses

## Overview

The diagnosis engine mechanically derives structured `Discrepancy` objects and ranked `RootCauseHypothesis` candidate explanations.

Hypotheses are explicitly framed as **mechanically supported hypotheses**, not unsupported claims. Every hypothesis links directly to supporting and contradicting evidence IDs.

---

## Discrepancy Categories & Hypothesis Mapping

| Discrepancy Type | Evaluated Symptoms | Candidate Root Causes |
| :--- | :--- | :--- |
| `settlement_amount_mismatch` | Settlement net amount differs from payment gross less fees | `incorrect_settlement_calculation`, `fee_omitted`, `partial_settlement` |
| `missing_record` | Payment captured without settlement or fee | `record_missing_from_source`, `settlement_delay` |
| `duplicate_record` | Multiple records with identical identifiers | `duplicate_submission`, `duplicate_replay` |
| `fee_calculation_error` | Observed fee diverges from stated basis-point rate | `fee_rate_miscalculation`, `tax_classification_error` |
| `settlement_timing_anomaly` | Timing out of sequence or delay $> 7$ days | `settlement_delay`, `backdated_entry` |
| `status_sync_failure` | Failed payment with processed settlement | `cross_system_sync_failure`, `uncaptured_capture` |
| `partial_settlement` | Settlement gross $< 100\%$ of payment gross | `incomplete_settlement`, `split_batch` |
| `broken_reference` | Settlement references non-existent payment ID | `reference_id_error`, `orphaned_record` |

---

## Conflict Analysis & Compensating Entries

When multiple interpretations exist, the engine does not rush to premature conclusions:
- If a gross difference is observed between Payment and Settlement (e.g. ₹10,000 vs ₹9,700), the engine checks whether a recorded fee (₹300) exists. If ₹10,000 - ₹300 = ₹9,700, the apparent difference is recognized as reconciled by recorded fees.
- If a refund exists, the engine checks whether the difference in net funds matches the refund amount.
