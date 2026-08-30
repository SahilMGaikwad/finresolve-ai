"""
FinResolve AI — Claim Validator Unit Tests

Tests verification of evidence-grounded factual statements and detection of hallucinations.
"""

import pytest

from data.schemas.case import CaseRecords
from data.schemas.investigation import ClaimVerificationStatus, FactualClaim
from services.investigator.validator import ClaimValidator
from services.reconciliation.engine import ReconciliationEngine


class TestClaimValidator:
    """Tests factual claim validation logic."""

    @pytest.fixture
    def setup_case(self):
        payment = {
            "record_type": "payment",
            "payment_id": "pay_val_01",
            "amount": {"amount_minor": 75000, "currency": "INR"},
            "status": "captured",
        }
        settlement = {
            "record_type": "settlement",
            "settlement_id": "stl_val_01",
            "payment_id": "pay_val_01",
            "gross_amount": {"amount_minor": 75000, "currency": "INR"},
            "fee_amount": {"amount_minor": 1500, "currency": "INR"},
            "net_amount": {"amount_minor": 73500, "currency": "INR"},
            "status": "processed",
        }
        records = CaseRecords(payments=[payment], settlements=[settlement])
        recon = ReconciliationEngine()
        res = recon.reconcile_records("CASE-VAL-01", records)
        return records, res

    def test_valid_evidence_grounded_claim(self, setup_case):
        records, res = setup_case
        validator = ClaimValidator(records, res)

        valid_claim = FactualClaim(
            claim_text="Payment pay_val_01 captured 75000 minor units",
            claimed_entity_id="pay_val_01",
            claimed_field="amount",
            claimed_value=75000,
            evidence_ids=[str(res.evidence[0].evidence_id)] if res.evidence else ["ev_mock_01"],
        )
        if not res.evidence:
            validator.valid_evidence_ids.add("ev_mock_01")

        result = validator.validate_claim(valid_claim)
        assert result.verification_status == ClaimVerificationStatus.VERIFIED

    def test_unsupported_claim_non_existent_entity(self, setup_case):
        records, res = setup_case
        validator = ClaimValidator(records, res)

        phantom_claim = FactualClaim(
            claim_text="Phantom payment exists",
            claimed_entity_id="pay_phantom_99",
            claimed_field="amount",
            claimed_value=10000,
            evidence_ids=[],
        )
        result = validator.validate_claim(phantom_claim)
        assert result.verification_status == ClaimVerificationStatus.UNSUPPORTED
        assert "not found" in result.verification_reason

    def test_contradicted_claim_wrong_amount(self, setup_case):
        records, res = setup_case
        validator = ClaimValidator(records, res)
        ev_id = str(res.evidence[0].evidence_id) if res.evidence else "ev_01"
        validator.valid_evidence_ids.add(ev_id)

        contradictory_claim = FactualClaim(
            claim_text="Payment pay_val_01 captured 99999 minor units",
            claimed_entity_id="pay_val_01",
            claimed_field="amount",
            claimed_value=99999,  # Observable value is 75000!
            evidence_ids=[ev_id],
        )
        result = validator.validate_claim(contradictory_claim)
        assert result.verification_status == ClaimVerificationStatus.CONTRADICTED
        assert "contradicts observable record value" in result.verification_reason
