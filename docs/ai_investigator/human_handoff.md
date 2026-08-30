# FinResolve AI — Human Review & Escalation Package

## 1. Handoff Package Structure

When automated resolution cannot safely resolve a case, the system constructs a structured [`HumanReviewPackage`](file:///Users/sahilgaikwad/finresolve-ai/data/schemas/investigation.py):

```python
class HumanReviewPackage(BaseModel):
    case_id: str
    discrepancies_summary: list[str]
    verified_evidence_summary: list[str]
    failed_simulations_summary: list[str]
    key_ambiguities: list[str]
    recommended_analyst_actions: list[str]
    priority: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
```

---

## 2. Information Handed to Financial Analysts

- **Verified Observable Facts**: Summary of all deterministic rules and evidence items.
- **Diagnostic Hypotheses**: Ranked plausible root causes with explanations.
- **Failed Simulation Logs**: Specific reasons why candidate resolutions failed closed-loop simulation.
- **Actionable Next Steps**: Clear operational recommendations for human reviewers.
