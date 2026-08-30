# FinResolve AI — Typed Investigator Tools

## 1. Tool Catalog

All investigator tools inherit from `BaseInvestigatorTool` with strict Pydantic parameter schemas:

| Tool Name | Access Type | Input Parameters | Output Description |
| :--- | :--- | :--- | :--- |
| `get_case_overview` | Read-Only | `case_id: str` | Summary counts of payments, settlements, fees, refunds, and ledger entries |
| `get_record_detail` | Read-Only | `record_type: str`, `record_id: str` | Complete dictionary of a specific record by ID |
| `get_evidence_items` | Read-Only | `case_id: str` | List of all verified evidence items from reconciliation rules |
| `get_evidence_subgraph`| Read-Only | `case_id: str` | Nodes and edges forming the case's Evidence Graph |
| `get_diagnostic_hypotheses`| Read-Only | `case_id: str` | Plausibility-ranked diagnostic root-cause hypotheses |
| `simulate_resolution_plan` | Simulation | `plan: ResolutionPlan` | Closed-loop sequential counterfactual simulation of plan steps |
| `evaluate_plan_policy` | Validation | `plan: ResolutionPlan` | Deterministic policy evaluation (`POL-001` to `POL-006`) |

---

## 2. Tool Security Policies

- **Zero Shell / Database / Network Execution**: The agent has no access to operating system commands, raw SQL, or live external payment gateways.
- **Resource Scope Isolation**: Every tool query is strictly bounded to the currently active case.
- **Audit Logging**: Every tool invocation records an entry in the investigation's `AgentTraceStep` sequence.
