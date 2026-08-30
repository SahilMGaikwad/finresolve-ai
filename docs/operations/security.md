# FinResolve AI — Operational Security & Data Classification

## Overview

This guide establishes data classification tiers, security practices, and prohibited operations.

---

## 1. Data Classification

| Classification Level | Definition | FinResolve Examples | Handling Requirements |
| :--- | :--- | :--- | :--- |
| **PUBLIC** | Freely shareable documentation and release notes | Architecture docs, API reference | Public Git repository |
| **INTERNAL** | System logs, performance metrics, case metadata | `/metrics` output, match group IDs | Internal observability, authenticated access |
| **SENSITIVE** | Customer transaction records, payment identifiers, amounts | Observed Payment, Settlement, Fee records | Role-gated access, encrypted at rest/transit |
| **SECRET** | Credentials, private keys, database passwords, auth tokens | JWT Secret, DB credentials | Never committed, KMS/Secrets Manager only |

---

## 2. Prohibited Log Content

The logging system actively scrubs the following attributes:
- Passwords and secret keys
- Raw Bearer tokens and API keys
- Permanent Account Numbers (PAN), Aadhaar numbers, and CVV codes
- Private RSA/EC keys

---

## 3. Core Architectural Principle

> **AI MAY RECOMMEND. DETERMINISTIC CONTROLS MAY VALIDATE. POLICY ENGINE MAY AUTHORIZE. HUMANS MAY APPROVE HIGH-RISK ACTIONS. REAL FINANCIAL EXECUTION IS OUTSIDE THE CURRENT PROTOTYPE.**
