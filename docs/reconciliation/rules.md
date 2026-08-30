# FinResolve AI — Deterministic Reconciliation Rules

## Overview

Reconciliation rules evaluate matched record groups to determine mathematical and lifecycle correctness. All monetary calculations operate in **exact integer minor units** (paise) — **zero floating-point math**.

---

## Implemented Rule Suite

### 1. `RULE-AMT-001` — Amount Reconciliation Rule
- **Category**: `amount`
- **Logic**:
  $$\text{expected\_net} = \text{payment\_gross} - \sum \text{fees}$$
  $$\text{diff} = \sum \text{observed\_settlement\_net} - \text{expected\_net}$$
- **Verification**:
  - Validates that observed settlements equal expected net after fee deductions.
  - Verifies that total refunds do not exceed initial payment gross.
- **Severity on Failure**: `HIGH` or `CRITICAL`.

---

### 2. `RULE-FEE-001` — Fee Analysis & Verification Rule
- **Category**: `fee`
- **Logic**:
  $$\text{expected\_platform\_fee} = \left\lfloor \frac{\text{payment\_gross} \times \text{rate\_bps} + 5000}{10000} \right\rfloor$$
  $$\text{expected\_gst} = \left\lfloor \frac{\text{platform\_fee} \times \text{gst\_rate\_bps} + 5000}{10000} \right\rfloor$$
- **Verification**:
  - Distinguishes platform fees from GST tax components.
  - Recomputes expected fee amounts using basis points and compares with observed fee records.
- **Severity on Failure**: `MEDIUM`.

---

### 3. `RULE-TIME-001` — Temporal Consistency Rule
- **Category**: `temporal`
- **Logic**:
  $$\text{order\_time} \le \text{payment\_time} \le \text{settlement\_time}$$
  $$\text{payment\_time} \le \text{refund\_time}$$
  $$\text{settlement\_time} - \text{payment\_time} \le \text{max\_delay\_days} \quad (7\text{ days})$$
- **Verification**:
  - Flags settlements or refunds dated prior to payment capture.
  - Detects excessive settlement delays exceeding standard banking windows.
- **Severity on Failure**: `MEDIUM` to `HIGH`.

---

### 4. `RULE-STAT-001` — Status Consistency Rule
- **Category**: `status`
- **Logic**:
  - Failed payment must not have a processed settlement.
  - Processed refund requires payment status to be `REFUNDED` or `PARTIALLY_REFUNDED`.
  - Cancelled order must not possess a captured unrefunded payment.
- **Severity on Failure**: `HIGH` to `CRITICAL`.

---

### 5. `RULE-LEDG-001` — Ledger Double-Entry Rule
- **Category**: `ledger`
- **Logic**:
  - For every ledger entry: exactly one of `debit` or `credit` must be $> 0$.
  - Verified ledger postings exist for matched payments, settlements, and refunds.
- **Severity on Failure**: `HIGH` to `CRITICAL`.
