"""
FinResolve AI — Investigation State Machine Unit Tests

Tests lifecycle state transitions, guard rails, and execution limits.
"""

import pytest

from data.schemas.investigation import InvestigationStatus
from services.investigator.state_machine import (
    ExecutionLimitExceededError,
    IllegalStateTransitionError,
    InvestigationStateMachine,
)


class TestInvestigationStateMachine:
    """Tests lifecycle transitions and safety limits."""

    def test_valid_lifecycle_transitions(self):
        sm = InvestigationStateMachine("CASE-TEST-01")
        assert sm.current_state == InvestigationStatus.CREATED

        sm.transition_to(InvestigationStatus.INVESTIGATING, "Begin investigation")
        assert sm.current_state == InvestigationStatus.INVESTIGATING

        sm.transition_to(InvestigationStatus.EVIDENCE_COLLECTED, "Collected evidence")
        assert sm.current_state == InvestigationStatus.EVIDENCE_COLLECTED

        sm.transition_to(InvestigationStatus.DIAGNOSIS_SYNTHESIZED, "Synthesized hypotheses")
        assert sm.current_state == InvestigationStatus.DIAGNOSIS_SYNTHESIZED

        sm.transition_to(InvestigationStatus.PLANNING, "Generated plan")
        assert sm.current_state == InvestigationStatus.PLANNING

        sm.transition_to(InvestigationStatus.SIMULATING, "Simulated plan")
        assert sm.current_state == InvestigationStatus.SIMULATING

        sm.transition_to(InvestigationStatus.POLICY_REVIEW, "Evaluated policy")
        assert sm.current_state == InvestigationStatus.POLICY_REVIEW

        sm.transition_to(InvestigationStatus.CLAIM_VALIDATION, "Validated claims")
        assert sm.current_state == InvestigationStatus.CLAIM_VALIDATION

        sm.transition_to(InvestigationStatus.COMPLETED, "Completed")
        assert sm.current_state == InvestigationStatus.COMPLETED
        assert sm.is_terminal is True

    def test_illegal_transition_raises_error(self):
        sm = InvestigationStateMachine("CASE-TEST-02")
        with pytest.raises(IllegalStateTransitionError, match="Illegal transition"):
            # Jumping directly from CREATED to COMPLETED is forbidden
            sm.transition_to(InvestigationStatus.COMPLETED, "Premature complete")

    def test_tool_call_limit_exceeded(self):
        sm = InvestigationStateMachine("CASE-TEST-03", max_tool_calls=3)
        sm.transition_to(InvestigationStatus.INVESTIGATING, "Start")

        sm.record_tool_call("tool_1")
        sm.record_tool_call("tool_2")
        sm.record_tool_call("tool_3")

        with pytest.raises(ExecutionLimitExceededError, match="Maximum tool calls"):
            sm.record_tool_call("tool_4")
