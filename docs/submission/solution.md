# Solution Overview — FinResolve AI

## 1. Architectural Philosophy
FinResolve AI enforces strict separation of responsibilities:
```
AI MAY INVESTIGATE.
DETERMINISTIC CONTROLS MAY VALIDATE.
POLICY MAY AUTHORIZE.
HUMANS MAY APPROVE HIGH-RISK ACTIONS.
REAL FINANCIAL EXECUTION IS OUT OF SCOPE.
```

---

## 2. The 7-Stage Closed-Loop Pipeline

1. **Ingestion & Normalization**: Canonical schemas with integer minor units (paise) and immutable provenance.
2. **Deterministic Matching**: Multi-signal matching (1:1, 1:N split, N:1 batch).
3. **Evidence Collection & Graph**: Directed graph connecting payments, settlements, fees, and ledger entries.
4. **Mechanical Root-Cause Diagnosis**: Bayesian plausibility scoring across ranked hypotheses.
5. **AI Financial Investigator**: State-machine-driven investigation producing verified factual claims.
6. **Counterfactual Simulation**: Deep-clone state testing and zero-sum ledger conservation verification.
7. **Deterministic Policy Gating & Audit**: Threshold-based routing and SHA-256 cryptographic audit logging.
