# FinResolve AI — Data Model

## Overview

This document describes the data model used throughout FinResolve AI.
All schemas are defined as Pydantic v2 models in `data/schemas/`.

## Entity Relationship Diagram

```
┌──────────┐     1:1      ┌──────────┐
│  Order   │◄────────────│ Payment  │
│          │              │          │
│ order_id │              │payment_id│
│ amount   │              │order_id  │──────┐
│ status   │              │amount    │      │
└──────────┘              │status    │      │
                          │method    │      │
                          └────┬─────┘      │
                               │            │
                    ┌──────────┼────────────┼──────────┐
                    │          │            │           │
               1:1  │     1:N  │       0:1  │      1:N  │
                    ▼          ▼            ▼           ▼
             ┌──────────┐ ┌────────┐ ┌──────────┐ ┌─────────────┐
             │Settlement│ │  Fee   │ │  Refund  │ │Ledger Entry │
             │          │ │        │ │          │ │             │
             │settle_id │ │fee_id  │ │refund_id │ │entry_id     │
             │payment_id│ │pay_id  │ │payment_id│ │reference_id │
             │gross_amt │ │settle_id│ │amount    │ │debit/credit │
             │fee_amt   │ │amount  │ │status    │ │balance_after│
             │net_amt   │ │rate_bps│ │          │ │entry_type   │
             └────┬─────┘ └────────┘ └──────────┘ └─────────────┘
                  │
                  │ N:1
                  ▼
             ┌──────────┐
             │  Payout  │
             │          │
             │payout_id │
             │settle_ids│
             │amount    │
             │status    │
             └──────────┘
```

## Record Types

### Payment (`data/schemas/payment.py`)
A single payment transaction by a customer.

| Field | Type | Description |
|-------|------|-------------|
| payment_id | str | Source system payment identifier |
| order_id | str | Associated order |
| merchant_id | str | Receiving merchant |
| amount | Money | Payment amount (minor units) |
| status | PaymentStatus | captured, failed, refunded, etc. |
| method | PaymentMethod | card, upi, netbanking, etc. |
| captured_at | datetime | When captured (UTC) |
| metadata | dict[str, str] | **Untrusted** arbitrary metadata |

### Order (`data/schemas/order.py`)
A merchant order.

| Field | Type | Description |
|-------|------|-------------|
| order_id | str | Source system order identifier |
| merchant_id | str | Merchant who created the order |
| amount | Money | Total order amount |
| status | OrderStatus | created, paid, fulfilled, etc. |
| items_count | int (≥1) | Number of items |
| ordered_at | datetime | When placed (UTC) |

### Settlement (`data/schemas/settlement.py`)
Transfer from gateway to merchant after fee deduction.

| Field | Type | Description |
|-------|------|-------------|
| settlement_id | str | Settlement identifier |
| payment_id | str | Associated payment |
| merchant_id | str | Receiving merchant |
| gross_amount | Money | Total before fees |
| fee_amount | Money | Total fees deducted |
| net_amount | Money | Amount settled (gross - fees) |
| status | SettlementStatus | pending, processed, failed |
| settled_at | datetime | When processed (UTC) |
| utr | str | Unique Transaction Reference |

**Invariant**: `net_amount = gross_amount - fee_amount`

### Refund (`data/schemas/refund.py`)
Full or partial refund of a payment.

| Field | Type | Description |
|-------|------|-------------|
| refund_id | str | Refund identifier |
| payment_id | str | Payment being refunded |
| amount | Money | Refund amount (≤ payment amount) |
| reason | str | Refund reason |
| status | RefundStatus | initiated, processed, failed |
| initiated_at | datetime | When initiated (UTC) |
| processed_at | datetime? | When processed (None if pending) |

### Fee (`data/schemas/fee.py`)
A fee charged on a transaction.

| Field | Type | Description |
|-------|------|-------------|
| fee_id | str | Fee identifier |
| payment_id | str | Payment this fee is charged on |
| settlement_id | str | Settlement this fee deducted from |
| fee_type | FeeType | platform_fee, gst, etc. |
| amount | Money | Fee amount |
| rate_bps | int (≥0) | Fee rate in basis points |
| applied_at | datetime | When applied (UTC) |

**Note**: `rate_bps` is in basis points (1 bps = 0.01%). 200 bps = 2.00%.

### Ledger Entry (`data/schemas/ledger_entry.py`)
A line in a merchant's financial ledger.

| Field | Type | Description |
|-------|------|-------------|
| entry_id | str | Entry identifier |
| reference_id | str | ID of the causing record |
| reference_type | RecordType | Type of the causing record |
| merchant_id | str | Merchant's ledger |
| debit | Money | Money going out |
| credit | Money | Money coming in |
| balance_after | Money | Balance after this entry |
| entry_type | LedgerEntryType | credit, debit, reversal, adjustment |
| posted_at | datetime | When posted (UTC) |

### Payout (`data/schemas/payout.py`)
Batch transfer from gateway to merchant's bank.

| Field | Type | Description |
|-------|------|-------------|
| payout_id | str | Payout identifier |
| merchant_id | str | Receiving merchant |
| amount | Money | Total payout |
| settlement_ids | list[str] | Settlements included |
| status | PayoutStatus | pending, processed, etc. |
| initiated_at | datetime | When initiated (UTC) |
| completed_at | datetime? | When completed |
| utr | str | Unique Transaction Reference |

## Money Value Object

All monetary amounts use the `Money` type: an integer in minor currency units.

- **No floats anywhere** in the financial data path
- 1 INR = 100 paise → `Money(amount_minor=50000, currency=Currency.INR)` = ₹500.00
- Fee rates in basis points: `payment.multiply_bps(200)` = 2% of payment
- Currency mismatch raises `ValueError`

## Assumptions

1. Each case has exactly one payment and one order.
2. Each payment has at most one full settlement (partial settlements are a corruption type).
3. Fee rates are expressed in basis points (integer) to avoid float arithmetic.
4. All timestamps are normalized to UTC.
5. All amounts are in paise (for INR) — never rupees as floats.
