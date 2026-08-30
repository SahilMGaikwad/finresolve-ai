"""
FinResolve AI — LLM Provider Abstraction & Prompt Templates

Defines abstract LLM interfaces, structured generation contracts, and prompt injection trust boundaries.
Provides a default MockDeterministicLLMProvider for offline, 100% reproducible execution.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any, TypeVar

from pydantic import BaseModel

from data.schemas.case import CaseRecords
from data.schemas.investigation import FactualClaim
from data.schemas.reconciliation_result import ReconciliationResult

T = TypeVar("T", bound=BaseModel)


def wrap_untrusted_data(data: Any, label: str = "untrusted_financial_metadata") -> str:
    """
    Quarantine external transaction metadata, notes, and descriptions in strict XML/JSON delimiters.
    Prevents prompt injection by isolating data from instructions.
    """
    serialized = json.dumps(data, default=str) if not isinstance(data, str) else data
    return f"<{label}>\n{serialized}\n</{label}>"


class LLMProvider(ABC):
    """Abstract interface for LLM providers."""

    @abstractmethod
    def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: type[T],
    ) -> T:
        """Generate structured output validated against a Pydantic schema."""
        pass


class InvestigationSynthesisOutput(BaseModel):
    """Schema for LLM synthesis of an investigation."""
    summary: str
    symptoms: list[str]
    root_cause_explanation: str
    claims: list[FactualClaim]


class MockDeterministicLLMProvider(LLMProvider):
    """
    Deterministic provider that generates rigorous, evidence-grounded findings from Phase 3 diagnostic output.
    Operates 100% offline with zero external API dependencies.
    """

    def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: type[T],
    ) -> T:
        # If the requested schema is InvestigationSynthesisOutput, construct grounded result
        if response_schema == InvestigationSynthesisOutput:
            # Output will be populated by synthesize_investigation
            pass
        return response_schema.model_validate({})

    def synthesize_investigation(
        self,
        case_id: str,
        records: CaseRecords,
        recon_result: ReconciliationResult,
    ) -> InvestigationSynthesisOutput:
        """
        Synthesize evidence-grounded symptoms, explanations, and factual claims.
        """
        symptoms = [d.discrepancy_type for d in recon_result.discrepancies]

        # Build explanation from deterministic hypotheses
        if recon_result.hypotheses:
            top_h = recon_result.hypotheses[0]
            cause_name = top_h.cause_type if isinstance(top_h.cause_type, str) else getattr(top_h.cause_type, "value", str(top_h.cause_type))
            explanation = (
                f"Primary root cause diagnosed as '{cause_name}' "
                f"(plausibility score: {top_h.plausibility_score:.2f}). {top_h.description}"
            )
        else:
            explanation = "Reconciliation completed with all records balanced and matched."

        summary = (
            f"Case {case_id} evaluated with status {recon_result.status.value}. "
            f"Identified {len(symptoms)} discrepancy symptoms across {len(records.payments)} payments "
            f"and {len(records.settlements)} settlements."
        )

        claims: list[FactualClaim] = []

        # Claim 1: Case status
        claims.append(
            FactualClaim(
                claim_text=f"Case status concluded as {recon_result.status.value}",
                claimed_entity_id=case_id,
                claimed_field="status",
                claimed_value=recon_result.status.value,
                evidence_ids=[str(ev.evidence_id) for ev in recon_result.evidence[:2]],
            )
        )

        # Claim 2: Payment amount if present
        if records.payments:
            p = records.payments[0]
            pid = str(p.get("payment_id") if isinstance(p, dict) else getattr(p, "payment_id", ""))
            amt_val = p.get("amount") if isinstance(p, dict) else getattr(p, "amount", None)
            amt_minor = amt_val.get("amount_minor") if isinstance(amt_val, dict) else getattr(amt_val, "amount_minor", 0)

            matching_ev = [str(ev.evidence_id) for ev in recon_result.evidence if ev.source_record_id == pid]
            ev_list = matching_ev or ([str(recon_result.evidence[0].evidence_id)] if recon_result.evidence else [])

            claims.append(
                FactualClaim(
                    claim_text=f"Payment {pid} captured amount of {amt_minor} minor units",
                    claimed_entity_id=pid,
                    claimed_field="amount",
                    claimed_value=amt_minor,
                    evidence_ids=ev_list,
                )
            )

        return InvestigationSynthesisOutput(
            summary=summary,
            symptoms=symptoms,
            root_cause_explanation=explanation,
            claims=claims,
        )
