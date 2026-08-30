"""
FinResolve AI — Investigator Agent Unit Tests

Tests full lifecycle investigation, trace recording, and deterministic fallback.
"""

from data.schemas.case import CaseRecords
from data.schemas.investigation import InvestigationStatus
from services.investigator.agent import AIInvestigatorAgent


class TestInvestigatorAgent:
    """Tests AI Financial Investigator Agent execution."""

    def test_investigate_clean_case(self):
        payment = {
            "record_type": "payment",
            "payment_id": "pay_agent_01",
            "merchant_id": "m_01",
            "amount": {"amount_minor": 50000, "currency": "INR"},
            "status": "captured",
            "captured_at": "2026-03-15T10:00:00+00:00",
        }
        settlement = {
            "record_type": "settlement",
            "settlement_id": "stl_agent_01",
            "payment_id": "pay_agent_01",
            "merchant_id": "m_01",
            "gross_amount": {"amount_minor": 50000, "currency": "INR"},
            "fee_amount": {"amount_minor": 1000, "currency": "INR"},
            "net_amount": {"amount_minor": 49000, "currency": "INR"},
            "status": "processed",
            "settled_at": "2026-03-16T10:00:00+00:00",
        }
        fee = {
            "record_type": "fee",
            "fee_id": "fee_agent_01",
            "payment_id": "pay_agent_01",
            "settlement_id": "stl_agent_01",
            "fee_type": "platform_fee",
            "amount": {"amount_minor": 1000, "currency": "INR"},
            "rate_bps": 200,
            "applied_at": "2026-03-15T10:00:00+00:00",
        }
        records = CaseRecords(payments=[payment], settlements=[settlement], fees=[fee])

        agent = AIInvestigatorAgent()
        result = agent.investigate_case("CASE-AGENT-01", records)

        assert result.case_id == "CASE-AGENT-01"
        assert result.status == InvestigationStatus.COMPLETED
        assert len(result.symptoms_identified) == 0
        assert result.unsupported_claims_count == 0
        assert len(result.investigation_trace) >= 4
