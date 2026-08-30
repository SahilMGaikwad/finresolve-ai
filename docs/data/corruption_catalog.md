# FinResolve AI — Corruption Catalog

## Overview

This catalog documents all corruption types that the synthetic data
generator can inject into observed records. Each corruption simulates
a real-world financial discrepancy.

Corruptions only modify the **observed** copy of case records.
The **ground truth** is never modified.

## Corruption Types

---

### 1. AMOUNT_MISMATCH

**What it simulates**: An incorrect settlement calculation where the settled
amount differs from what was expected based on the payment and fees.

**How it's injected**: The settlement `net_amount` is modified by 1%–15%
in either direction.

**How it should be detected**: Compare `payment.amount - total_fees` against
`settlement.net_amount`. The difference exceeds the acceptable tolerance.

**Difficulty levels**: Easy, Medium, Hard

**Example**:
```
Ground truth:  settlement.net_amount = 48,820 paise
Observed:      settlement.net_amount = 47,200 paise  (−1,620 paise, −3.3%)
```

---

### 2. MISSING_RECORD

**What it simulates**: A record that exists in one system but is missing
from another. Common in distributed payment systems where webhooks fail.

**How it's injected**: A settlement or fee record is removed from the
observed records list.

**How it should be detected**: A payment exists but has no corresponding
settlement, or a settlement exists but some expected fees are missing.

**Difficulty levels**: Medium, Hard

**Example**:
```
Ground truth:  2 fee records (platform_fee, gst)
Observed:      1 fee record (platform_fee) — GST fee is missing
```

---

### 3. DUPLICATE_RECORD

**What it simulates**: A payment or settlement processed twice due to
webhook replay, retry logic, or duplicate submission.

**How it's injected**: A payment or settlement record is deep-copied and
appended to the observed records list.

**How it should be detected**: Multiple records with the same ID or
matching amounts/timestamps within the same case.

**Difficulty levels**: Medium, Hard

**Example**:
```
Ground truth:  1 payment record
Observed:      2 identical payment records (same payment_id)
```

---

### 4. FEE_DISCREPANCY

**What it simulates**: A fee that was calculated incorrectly — wrong rate
applied, unexpected fee added, or fee amount doesn't match the rate.

**How it's injected**: A fee record's `amount` is modified by 10%–50%.

**How it should be detected**: Recompute the fee using the stated `rate_bps`
and `payment.amount`. The actual fee differs from the expected fee.

**Difficulty levels**: Easy, Medium, Hard

**Example**:
```
Ground truth:  fee.amount = 1,000 paise (200 bps on ₹50,000)
Observed:      fee.amount = 1,400 paise  (+40%)
```

---

### 5. TIMING_MISMATCH

**What it simulates**: A settlement that arrived much later or earlier
than expected, indicating a processing delay or backdated entry.

**How it's injected**: The settlement `settled_at` timestamp is shifted
by 3–30 days forward or backward.

**How it should be detected**: The gap between `payment.captured_at` and
`settlement.settled_at` exceeds the expected settlement window.

**Difficulty levels**: Medium, Hard

**Example**:
```
Ground truth:  settled_at = 2026-03-18 (3 days after payment)
Observed:      settled_at = 2026-04-10 (26 days after payment)
```

---

### 6. STATUS_INCONSISTENCY

**What it simulates**: A payment showing "failed" status while a settlement
record exists for it, indicating a status synchronisation failure between
systems.

**How it's injected**: The payment `status` is changed to "failed" while
the settlement record remains.

**How it should be detected**: A settlement exists for a payment whose
status indicates it should not have been settled.

**Difficulty levels**: Hard

**Example**:
```
Ground truth:  payment.status = "captured"
Observed:      payment.status = "failed" (but settlement exists!)
```

---

### 7. PARTIAL_SETTLEMENT

**What it simulates**: A settlement for less than the full payment amount,
without any refund to explain the shortfall.

**How it's injected**: The settlement `gross_amount` and `net_amount` are
reduced to 40%–80% of the original amounts.

**How it should be detected**: `settlement.gross_amount < payment.amount`
with no corresponding refund or adjustment.

**Difficulty levels**: Hard

**Example**:
```
Ground truth:  settlement.gross_amount = 50,000 paise
Observed:      settlement.gross_amount = 30,000 paise  (60%)
               No refund to explain the missing ₹200
```

---

### 8. INCORRECT_REFERENCE

**What it simulates**: A settlement that references a wrong payment_id,
simulating a cross-reference error between systems.

**How it's injected**: The settlement `payment_id` is replaced with a
randomly generated (non-existent) payment ID.

**How it should be detected**: The settlement's `payment_id` does not
match any known payment in the dataset.

**Difficulty levels**: Hard

**Example**:
```
Ground truth:  settlement.payment_id = "pay_abc123"
Observed:      settlement.payment_id = "pay_xyz999" (doesn't exist)
```

---

## Difficulty Levels

| Level | Available Corruptions | Corruption Count |
|-------|----------------------|-----------------|
| Easy | AMOUNT_MISMATCH, FEE_DISCREPANCY | 1 |
| Medium | + TIMING_MISMATCH, MISSING_RECORD, DUPLICATE_RECORD | 1–2 |
| Hard | + STATUS_INCONSISTENCY, PARTIAL_SETTLEMENT, INCORRECT_REFERENCE | 1–3 |
| Mixed | Weighted: 40% Easy, 35% Medium, 25% Hard | varies |

## Ground Truth Labels

Every corruption produces a `CorruptionLabel` with:

| Field | Description |
|-------|-------------|
| corruption_id | Unique identifier |
| case_id | Which case was corrupted |
| corruption_type | Which corruption was applied |
| target_record_type | Which record type was modified |
| target_record_id | Which specific record was modified |
| target_field | Which field was changed |
| original_value | Value before corruption |
| corrupted_value | Value after corruption |
| description | Human-readable explanation |
