# FinResolve AI — Investigation Flow & State Machine

## 1. Lifecycle State Progression

```
[CREATED]
    │
    ▼
[INVESTIGATING] ───────────────► Runs Case Overview & Evidence Tools
    │
    ▼
[EVIDENCE_COLLECTED] ──────────► Verifies Node/Edge Structure in Graph
    │
    ▼
[DIAGNOSIS_SYNTHESIZED] ───────► Extracts Plausibility-Ranked Hypotheses
    │
    ▼
[PLANNING] ────────────────────► Constructs Sequential ResolutionPlan
    │
    ▼
[SIMULATING] ──────────────────► Runs Closed-Loop Multi-Step Simulation
    │
    ▼
[POLICY_REVIEW] ───────────────► Evaluates Policy Risk & Monetary Thresholds
    │
    ▼
[CLAIM_VALIDATION] ────────────► Checks Factual Claims Against Evidence Graph
    │
    ├──────────────────────────┼──────────────────────────┐
    ▼                          ▼                          ▼
[COMPLETED]          [HUMAN_REVIEW_REQUIRED]          [BLOCKED]
```

---

## 2. Guard Rails & Circuit Breakers

- **Step Limit**: Maximum 8 lifecycle state transitions.
- **Tool Call Limit**: Maximum 12 tool executions per investigation.
- **Timeout**: Maximum 10.0 seconds per case.
- If any limit is breached, the agent immediately transitions to `HUMAN_REVIEW_REQUIRED` or `FAILED` without mutating financial state.
