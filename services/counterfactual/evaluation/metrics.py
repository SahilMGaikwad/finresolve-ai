"""
FinResolve AI — Counterfactual Evaluation Metrics

Computes Case Resolution Rate, Proposal Feasibility, Policy Gating Accuracy,
Zero-Harm Safety Rate, and simulation performance metrics.
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class CounterfactualEvaluationSummary(BaseModel):
    """Structured evaluation report for counterfactual simulation & policy decisions."""
    total_cases_evaluated: int
    clean_cases: int
    corrupted_cases: int
    resolved_cases_count: int
    case_resolution_rate: float = Field(
        description="Proportion of corrupted cases where at least 1 valid resolution was simulated",
    )
    total_proposals_generated: int
    simulated_valid_proposals: int
    
    # Core Safety Ratio
    zero_harm_safety_rate: float = Field(
        description="Percentage of imbalanced or unverified proposals blocked (must be 100%)",
    )

    # Policy Routing Counts
    auto_resolvable_count: int
    human_review_count: int
    blocked_count: int
    no_safe_action_count: int

    # Performance
    mean_latency_ms: float

    def format_report(self) -> str:
        """Format a human-readable console report."""
        lines = [
            "",
            "=" * 65,
            "  FinResolve AI — Counterfactual Simulation & Policy Evaluation",
            "=" * 65,
            f"  Total Cases Evaluated:       {self.total_cases_evaluated}",
            f"  Clean Cases:                 {self.clean_cases}",
            f"  Corrupted Cases:             {self.corrupted_cases}",
            f"  Mean Simulation Latency:     {self.mean_latency_ms:.2f} ms",
            "-" * 65,
            "  Case Resolution Performance:",
            f"    Corrupted Cases Resolved:  {self.resolved_cases_count} / {self.corrupted_cases}",
            f"    Case Resolution Rate:      {self.case_resolution_rate * 100:.2f}%",
            f"    Zero-Harm Safety Rate:     {self.zero_harm_safety_rate * 100:.2f}%",
            "-" * 65,
            "  Proposal Simulation Breakdown:",
            f"    Proposals Generated:       {self.total_proposals_generated}",
            f"    Simulated Valid Proposals: {self.simulated_valid_proposals}",
            f"    Simulated Blocked Actions: {self.blocked_count}",
            "-" * 65,
            "  Deterministic Policy Decisions:",
            f"    AUTO_RESOLVABLE:           {self.auto_resolvable_count}",
            f"    HUMAN_REVIEW:              {self.human_review_count}",
            f"    BLOCKED:                   {self.blocked_count}",
            f"    NO_SAFE_ACTION:            {self.no_safe_action_count}",
            "=" * 65,
            "",
        ]
        return "\n".join(lines)
