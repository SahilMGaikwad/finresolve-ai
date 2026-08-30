# FinResolve AI — Evidence Graph

## Overview

The `EvidenceGraph` is a lightweight, directed in-memory graph representing entities, financial transactions, and relational dependencies alongside mechanical support and conflict edges.

---

## Graph Topology

```
                  ┌────────────┐
                  │   Order    │
                  └─────▲──────┘
                        │ PAYS_FOR
                  ┌─────┴──────┐
        ┌─────────┤  Payment   ├─────────┐
        │         └─────▲──────┘         │
CHARGES │               │ SETTLES        │ REFUNDS
        ▼               │                ▼
  ┌───────────┐   ┌─────┴──────┐   ┌───────────┐
  │    Fee    │   │ Settlement │   │  Refund   │
  └─────┬─────┘   └─────┬──────┘   └─────┬─────┘
        │ CHARGES       │ POSTS_TO       │ POSTS_TO
        ▼               ▼                ▼
  ┌────────────────────────────────────────────┐
  │                LedgerEntry                 │
  └────────────────────────────────────────────┘
```

---

## Node Types (`GraphNodeType`)

- `CUSTOMER` / `MERCHANT`
- `ORDER`
- `PAYMENT`
- `SETTLEMENT`
- `REFUND`
- `FEE`
- `LEDGER_ENTRY`
- `PAYOUT`

---

## Edge Types (`GraphEdgeType`)

- `BELONGS_TO`: Entity ownership relationship.
- `PAYS_FOR`: Payment fulfilling an Order.
- `SETTLES`: Settlement transferring funds for a Payment.
- `REFUNDS`: Refund reversing a Payment.
- `CHARGES`: Fee deducted from a Payment or Settlement.
- `POSTS_TO`: Ledger entry recording a financial movement.
- `REFERENCES`: Foreign key linkage between records.
- `CONFLICTS_WITH`: Anomaly or contradiction identified between records or fields.
- `SUPPORTS`: Confirmatory relationship verifying financial balance.
