# FinResolve AI — AI Financial Investigator Architecture

## 1. Executive Overview

The **AI Financial Investigator** is an evidence-grounded reasoning layer designed to orchestrate investigation, synthesize symptoms, evaluate root-cause hypotheses, and propose multi-step resolution plans for unresolved financial discrepancies.

---

## 2. Core Safety Boundary

> **AI MAY INVESTIGATE. AI MAY REASON OVER VERIFIED EVIDENCE. AI MAY PROPOSE STRUCTURED ACTIONS.**
>
> **AI MUST NOT:**
> - Access ground truth, corruption labels, or expected outcomes.
> - Bypass deterministic reconciliation, evidence validation, counterfactual simulation, or policy engine.
> - Execute real financial actions, mutate financial state, issue payouts/refunds, or approve its own proposals.

```
AI INVESTIGATOR
     │
     ▼
STRUCTURED PROPOSAL (Multi-Step ResolutionPlan)
     │
     ▼
SCHEMA & CLAIM VALIDATION
     │
     ▼
COUNTERFACTUAL SIMULATION & LEDGER VERIFICATION
     │
     ▼
DETERMINISTIC POLICY ENGINE
     │
     ▼
AUTO-RESOLVE / HUMAN REVIEW / BLOCK
```

---

## 3. Subsystem Components

1. **State Machine (`services.investigator.state_machine`)**: Enforces explicit lifecycle states (`CREATED` $\to$ `INVESTIGATING` $\to$ `EVIDENCE_COLLECTED` $\to$ `DIAGNOSIS_SYNTHESIZED` $\to$ `PLANNING` $\to$ `SIMULATING` $\to$ `POLICY_REVIEW` $\to$ `CLAIM_VALIDATION` $\to$ `COMPLETED` / `HUMAN_REVIEW_REQUIRED` / `BLOCKED`), maximum step bounds, and short-lived execution memory.
2. **Typed Tools (`services.investigator.tools`)**: Controlled, read-only inspection tools and deterministic simulation tools.
3. **Multi-Step Planner (`services.investigator.planner`)**: Synthesizes sequential resolution actions to resolve compound discrepancies.
4. **Claim Validator (`services.investigator.validator`)**: Validates factual claims against observable records and the Evidence Graph.
5. **Provider Abstraction (`services.investigator.provider`)**: Abstract protocol supporting pluggable LLMs and an offline deterministic mock provider.
6. **Deterministic Fallback (`services.investigator.fallback`)**: Pure rule-based fallback when LLM providers are unavailable.
