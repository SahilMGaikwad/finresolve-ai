# FinResolve AI — Record Matching Engine

## Overview

The matching engine groups observed financial records (`Payment`, `Order`, `Settlement`, `Fee`, `Refund`, `LedgerEntry`, `Payout`) into cohesive transaction lifecycles (`MatchGroup`).

Matching operates strictly **without an LLM**, using multi-signal scoring with explainable weights.

---

## Matching Signals & Scoring

Matching between a primary record (e.g. `Payment`) and a candidate record evaluates 5 distinct signals:

| Signal Name | Configured Weight | Description | Scoring Logic |
| :--- | :--- | :--- | :--- |
| `reference_matching` | 0.40 | Explicit foreign key or reverse ID reference | 1.0 (exact match), -1.0 (contradictory reference), 0.0 (no reference) |
| `amount_compatibility` | 0.25 | Integer minor unit compatibility | 1.0 (exact), 0.85–0.90 (valid fee/refund proportion), 0.0 (mismatch) |
| `timestamp_proximity` | 0.15 | Temporal sequence and window closeness | 1.0 (≤1 day), 0.8 (≤7 days), linear decay (8–30 days), 0.0 (>30 days) |
| `currency_match` | 0.10 | ISO currency code equivalence | 1.0 (identical), 0.0 (mismatch or absent) |
| `merchant_match` | 0.10 | Merchant account identity | 1.0 (identical), 0.5 (neutral/absent), 0.0 (mismatch) |

### Aggregate Score Formula
$$\text{Score} = \sum_{i=1}^{5} \text{raw\_score}_i \times \text{weight}_i$$

---

## Matching States

| State | Score Threshold / Condition | Meaning |
| :--- | :--- | :--- |
| `MATCHED` | $\text{Score} \ge 0.70$ | High-confidence deterministic association |
| `PROBABLE_MATCH` | $0.50 \le \text{Score} < 0.70$ | Plausible link; flagged for variance inspection |
| `AMBIGUOUS` | $|\text{Score}_1 - \text{Score}_2| \le 0.05$ | Multiple close candidate records competing for a 1:1 relationship |
| `UNMATCHED` | $\text{Score} < 0.50$ | Record could not be associated with any group |
| `CONFLICT` | Contradictory references | Record has strong signals but explicit contradictory foreign key |

---

## Relationship Multiplicity

The engine supports:
- **1:1**: Payment $\leftrightarrow$ Order
- **1:1 / 1:N**: Payment $\leftrightarrow$ Settlement (split settlements)
- **1:N**: Payment $\leftrightarrow$ Fees (platform fee, GST, intermediary charges)
- **1:N**: Payment $\leftrightarrow$ Refunds (partial and full refunds)
- **1:N**: Financial events $\leftrightarrow$ Ledger Entries (credits, debits, reversals)
- **N:1**: Settlements $\leftrightarrow$ Payout
