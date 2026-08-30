"""
FinResolve AI — Evidence Grounding & Factual Claim Validator

Validates every factual claim made by the AI investigator against observable records and the Evidence Graph.
Detects and rejects ungrounded statements, fabricated amounts, or hallucinated record references.
"""

from __future__ import annotations

from typing import Any

from data.schemas.case import CaseRecords
from data.schemas.investigation import ClaimVerificationStatus, FactualClaim
from data.schemas.reconciliation_result import ReconciliationResult


def _extract_record_val(rec: dict[str, Any] | Any, field: str) -> Any:
    if isinstance(rec, dict):
        val = rec.get(field)
    else:
        val = getattr(rec, field, None)

    if isinstance(val, dict) and "amount_minor" in val:
        return val["amount_minor"]
    elif hasattr(val, "amount_minor"):
        return val.amount_minor
    return val


class ClaimValidator:
    """
    Validates factual claims against the ground-truth isolated observed records and evidence pool.
    """

    def __init__(self, records: CaseRecords, recon_result: ReconciliationResult):
        self.records = records
        self.recon_result = recon_result

        # Build index of observable records
        self.record_index: dict[str, tuple[str, Any]] = {}
        for p in records.payments:
            pid = str(p.get("payment_id") if isinstance(p, dict) else getattr(p, "payment_id", ""))
            if pid:
                self.record_index[pid] = ("payment", p)
        for s in records.settlements:
            sid = str(s.get("settlement_id") if isinstance(s, dict) else getattr(s, "settlement_id", ""))
            if sid:
                self.record_index[sid] = ("settlement", s)
        for f in records.fees:
            fid = str(f.get("fee_id") if isinstance(f, dict) else getattr(f, "fee_id", ""))
            if fid:
                self.record_index[fid] = ("fee", f)
        for r in records.refunds:
            rid = str(r.get("refund_id") if isinstance(r, dict) else getattr(r, "refund_id", ""))
            if rid:
                self.record_index[rid] = ("refund", r)
        for l in records.ledger_entries:
            lid = str(l.get("entry_id") if isinstance(l, dict) else getattr(l, "entry_id", ""))
            if lid:
                self.record_index[lid] = ("ledger_entry", l)

        # Build index of valid evidence IDs
        self.valid_evidence_ids = {str(ev.evidence_id) for ev in recon_result.evidence}

    def validate_claim(self, claim: FactualClaim) -> FactualClaim:
        """
        Evaluate a single factual claim against observable state and evidence.
        """
        # Check 1: Entity Existence
        entity_id = claim.claimed_entity_id
        if entity_id not in self.record_index and entity_id != self.recon_result.case_id:
            claim.verification_status = ClaimVerificationStatus.UNSUPPORTED
            claim.verification_reason = f"Referenced entity '{entity_id}' not found in observable records."
            return claim

        # Check 2: Evidence Linkage (if evidence IDs are cited, all must be valid)
        for ev_id in claim.evidence_ids:
            if ev_id not in self.valid_evidence_ids:
                claim.verification_status = ClaimVerificationStatus.UNSUPPORTED
                claim.verification_reason = f"Cited evidence ID '{ev_id}' does not exist in verified evidence pool."
                return claim

        # Check 3: Field Value Verification
        actual_val = None
        if entity_id == self.recon_result.case_id and claim.claimed_field == "status":
            actual_val = self.recon_result.status.value
        elif entity_id in self.record_index and claim.claimed_field:
            _, rec_obj = self.record_index[entity_id]
            actual_val = _extract_record_val(rec_obj, claim.claimed_field)

        if actual_val is not None:
            # Compare value with minor-unit tolerance or exact match
            if str(actual_val) != str(claim.claimed_value):
                claim.verification_status = ClaimVerificationStatus.CONTRADICTED
                claim.verification_reason = (
                    f"Claimed value '{claim.claimed_value}' for field '{claim.claimed_field}' "
                    f"contradicts observable record value '{actual_val}'."
                )
                return claim

        # All checks passed
        claim.verification_status = ClaimVerificationStatus.VERIFIED
        claim.verification_reason = "Verified against observable record and evidence graph."
        return claim

    def validate_all(self, claims: list[FactualClaim]) -> tuple[list[FactualClaim], int]:
        """Validate a list of claims and return validated list + unsupported count."""
        validated_claims = [self.validate_claim(c) for c in claims]
        unsupported_count = sum(
            1 for c in validated_claims if c.verification_status != ClaimVerificationStatus.VERIFIED
        )
        return validated_claims, unsupported_count
