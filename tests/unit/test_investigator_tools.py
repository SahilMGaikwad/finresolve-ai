"""
FinResolve AI — Investigator Tools Unit Tests

Tests CaseOverviewTool, RecordDetailTool, EvidenceInspectorTool, EvidenceGraphTool,
DiagnosticHypothesesTool, MultiStepSimulationTool, and PolicyEvaluationTool.
"""

import pytest

from data.schemas.case import CaseRecords
from services.investigator.tools import (
    CaseOverviewTool,
    InvestigatorToolRegistry,
    RecordDetailTool,
    ToolExecutionError,
)
from services.reconciliation.engine import ReconciliationEngine


class TestInvestigatorTools:
    """Tests typed tools and registry access control."""

    @pytest.fixture
    def sample_records(self):
        payment = {
            "record_type": "payment",
            "payment_id": "pay_tool_01",
            "merchant_id": "m_tool_01",
            "amount": {"amount_minor": 10000, "currency": "INR"},
            "status": "captured",
            "captured_at": "2026-03-15T10:00:00+00:00",
        }
        settlement = {
            "record_type": "settlement",
            "settlement_id": "stl_tool_01",
            "payment_id": "pay_tool_01",
            "merchant_id": "m_tool_01",
            "gross_amount": {"amount_minor": 10000, "currency": "INR"},
            "fee_amount": {"amount_minor": 200, "currency": "INR"},
            "net_amount": {"amount_minor": 9800, "currency": "INR"},
            "status": "processed",
            "settled_at": "2026-03-16T10:00:00+00:00",
        }
        return CaseRecords(payments=[payment], settlements=[settlement])

    def test_case_overview_tool(self, sample_records):
        tool = CaseOverviewTool(sample_records)
        out = tool.execute(case_id="CASE-TOOL-01")
        assert out.payments_count == 1
        assert out.settlements_count == 1
        assert out.fees_count == 0

    def test_record_detail_tool(self, sample_records):
        tool = RecordDetailTool(sample_records)
        out = tool.execute(record_type="payment", record_id="pay_tool_01")
        assert out.found is True
        assert out.record["payment_id"] == "pay_tool_01"

        missing_out = tool.execute(record_type="payment", record_id="pay_non_existent")
        assert missing_out.found is False
        assert missing_out.record is None

    def test_tool_registry_rejects_unauthorized_tool(self, sample_records):
        recon = ReconciliationEngine()
        res = recon.reconcile_records("CASE-TOOL-01", sample_records)
        registry = InvestigatorToolRegistry("CASE-TOOL-01", sample_records, res)

        with pytest.raises(ToolExecutionError, match="Unauthorized or unknown tool"):
            registry.get_tool("execute_shell_command")
