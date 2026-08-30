"""
FinResolve AI — Investigator Evaluation Metrics

Calculates Unsupported Claim Rate, Grounding Accuracy, Multi-Step Feasibility,
Zero-Harm Safety, and Investigation Latency.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class InvestigatorEvaluationSummary(BaseModel):
    """Structured evaluation metrics for the AI Financial Investigator."""
    total_cases_evaluated: int
    clean_cases: int
    corrupted_cases: int
    total_investigations: int

    # Grounding & Claim Integrity
    total_claims_evaluated: int
    verified_claims_count: int
    unsupported_claims_count: int
    unsupported_claim_rate: float = Field(
        description="Ratio of unsupported claims to total claims (Target: 0.00%)",
    )
    grounding_accuracy_rate: float = Field(
        description="Ratio of verified claims to total claims (Target: 100.00%)",
    )

    # Multi-Step Resolution Feasibility
    multi_step_plans_generated: int
    multi_step_plans_simulated_valid: int
    plan_feasibility_rate: float

    # Core Safety
    zero_harm_safety_rate: float = 1.0

    # Policy Routing
    auto_resolvable_count: int
    human_review_count: int
    blocked_count: int

    # Performance
    mean_investigation_latency_ms: float
    mean_tool_calls_per_case: float

    def format_report(self) -> str:
        """Format a human-readable console report."""
        lines = [
            "",
            "=" * 65,
            "  FinResolve AI — AI Financial Investigator Evaluation Report",
            "=" * 65,
            f"  Total Cases Evaluated:       {self.total_cases_evaluated}",
            f"  Clean Cases:                 {self.clean_cases}",
            f"  Corrupted Cases:             {self.corrupted_cases}",
            f"  Mean Investigation Latency:  {self.mean_investigation_latency_ms:.2f} ms",
            f"  Mean Tool Calls / Case:      {self.mean_tool_calls_per_case:.1f}",
            "-" * 65,
            "  Evidence Grounding & Claim Integrity:",
            f"    Total Factual Claims:      {self.total_claims_evaluated}",
            f"    Verified Claims:           {self.verified_claims_count}",
            f"    Unsupported Claims:        {self.unsupported_claims_count}",
            f"    Unsupported Claim Rate:    {self.unsupported_claim_rate * 100:.2f}% (Target: 0.00%)",
            f"    Grounding Accuracy Rate:   {self.grounding_accuracy_rate * 100:.2f}%",
            "-" * 65,
            "  Multi-Step Resolution Planning:",
            f"    Plans Generated:           {self.multi_step_plans_generated}",
            f"    Simulated Valid Plans:     {self.multi_step_plans_simulated_valid}",
            f"    Plan Feasibility Rate:     {self.plan_feasibility_rate * 100:.2f}%",
            f"    Zero-Harm Safety Rate:     {self.zero_harm_safety_rate * 100:.2f}%",
            "-" * 65,
            "  Deterministic Policy Routing:",
            f"    AUTO_RESOLVABLE:           {self.auto_resolvable_count}",
            f"    HUMAN_REVIEW_REQUIRED:     {self.human_review_count}",
            f"    BLOCKED:                   {self.blocked_count}",
            "=" * 65,
            "",
        ]
        return "\n".join(lines)
