"""
FinResolve AI — Counterfactual Resolution Engine Package
"""

from services.counterfactual.approval import (
    ApprovalRecord,
    ApprovalStatus,
    ApprovalWorkflowManager,
)
from services.counterfactual.generator import CandidateActionGenerator
from services.counterfactual.ledger_verifier import (
    compute_financial_delta,
    verify_ledger_double_entry,
)
from services.counterfactual.proposal import ResolutionOrchestrator
from services.counterfactual.simulator import CounterfactualSimulator
from services.counterfactual.state import (
    apply_action_to_state,
    create_counterfactual_state,
)

__all__ = [
    "ApprovalRecord",
    "ApprovalStatus",
    "ApprovalWorkflowManager",
    "CandidateActionGenerator",
    "CounterfactualSimulator",
    "ResolutionOrchestrator",
    "apply_action_to_state",
    "compute_financial_delta",
    "create_counterfactual_state",
    "verify_ledger_double_entry",
]
