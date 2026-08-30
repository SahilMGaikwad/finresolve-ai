"""
FinResolve AI — Investigation State Machine & Execution Guards

Enforces strict lifecycle state transitions, loop bounds, and short-lived execution memory.
Prevents infinite tool loops, unauthorized state mutations, and runtime resource exhaustion.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

from data.schemas.investigation import AgentTraceStep, InvestigationStatus


class IllegalStateTransitionError(Exception):
    """Raised when an invalid lifecycle transition is attempted."""
    pass


class ExecutionLimitExceededError(Exception):
    """Raised when an investigation exceeds configured step or tool limits."""
    pass


class InvestigationStateMachine:
    """
    Manages the lifecycle, memory, and safety bounds of a single investigation.
    """

    ALLOWED_TRANSITIONS: dict[InvestigationStatus, set[InvestigationStatus]] = {
        InvestigationStatus.CREATED: {
            InvestigationStatus.INVESTIGATING,
            InvestigationStatus.FAILED,
        },
        InvestigationStatus.INVESTIGATING: {
            InvestigationStatus.EVIDENCE_COLLECTED,
            InvestigationStatus.FAILED,
            InvestigationStatus.HUMAN_REVIEW_REQUIRED,
        },
        InvestigationStatus.EVIDENCE_COLLECTED: {
            InvestigationStatus.DIAGNOSIS_SYNTHESIZED,
            InvestigationStatus.FAILED,
            InvestigationStatus.HUMAN_REVIEW_REQUIRED,
        },
        InvestigationStatus.DIAGNOSIS_SYNTHESIZED: {
            InvestigationStatus.PLANNING,
            InvestigationStatus.CLAIM_VALIDATION,
            InvestigationStatus.FAILED,
            InvestigationStatus.HUMAN_REVIEW_REQUIRED,
        },
        InvestigationStatus.PLANNING: {
            InvestigationStatus.SIMULATING,
            InvestigationStatus.CLAIM_VALIDATION,
            InvestigationStatus.FAILED,
            InvestigationStatus.HUMAN_REVIEW_REQUIRED,
        },
        InvestigationStatus.SIMULATING: {
            InvestigationStatus.POLICY_REVIEW,
            InvestigationStatus.FAILED,
            InvestigationStatus.BLOCKED,
        },
        InvestigationStatus.POLICY_REVIEW: {
            InvestigationStatus.CLAIM_VALIDATION,
            InvestigationStatus.FAILED,
            InvestigationStatus.BLOCKED,
            InvestigationStatus.HUMAN_REVIEW_REQUIRED,
        },
        InvestigationStatus.CLAIM_VALIDATION: {
            InvestigationStatus.COMPLETED,
            InvestigationStatus.HUMAN_REVIEW_REQUIRED,
            InvestigationStatus.BLOCKED,
            InvestigationStatus.FAILED,
        },
        # Terminal states
        InvestigationStatus.COMPLETED: set(),
        InvestigationStatus.HUMAN_REVIEW_REQUIRED: set(),
        InvestigationStatus.BLOCKED: set(),
        InvestigationStatus.FAILED: set(),
    }

    def __init__(
        self,
        case_id: str,
        max_steps: int = 8,
        max_tool_calls: int = 12,
        max_duration_seconds: float = 10.0,
    ):
        self.case_id = case_id
        self.current_state = InvestigationStatus.CREATED
        self.max_steps = max_steps
        self.max_tool_calls = max_tool_calls
        self.max_duration_seconds = max_duration_seconds

        self.step_count = 0
        self.tool_call_count = 0
        self.start_time = time.monotonic()
        self.trace: list[AgentTraceStep] = []
        self.memory: dict[str, Any] = {}

    def transition_to(
        self,
        new_state: InvestigationStatus,
        action_taken: str,
        tool_called: str | None = None,
        tool_output_summary: str | None = None,
    ) -> None:
        """
        Transition to a new lifecycle state with safety validation.
        """
        self._check_execution_limits()

        allowed = self.ALLOWED_TRANSITIONS.get(self.current_state, set())
        if new_state not in allowed:
            raise IllegalStateTransitionError(
                f"Illegal transition from {self.current_state.value} to {new_state.value} for case {self.case_id}"
            )

        self.step_count += 1
        self.current_state = new_state

        trace_step = AgentTraceStep(
            step_number=self.step_count,
            state=new_state,
            action_taken=action_taken,
            tool_called=tool_called,
            tool_output_summary=tool_output_summary,
            timestamp=datetime.now(timezone.utc),
        )
        self.trace.append(trace_step)

    def record_tool_call(self, tool_name: str) -> None:
        """Track and validate tool invocation limits."""
        self._check_execution_limits()
        self.tool_call_count += 1
        if self.tool_call_count > self.max_tool_calls:
            raise ExecutionLimitExceededError(
                f"Maximum tool calls ({self.max_tool_calls}) exceeded for case {self.case_id}"
            )

    def _check_execution_limits(self) -> None:
        """Enforce step count and execution duration ceilings."""
        if self.step_count >= self.max_steps:
            raise ExecutionLimitExceededError(
                f"Maximum steps ({self.max_steps}) exceeded for case {self.case_id}"
            )

        elapsed = time.monotonic() - self.start_time
        if elapsed > self.max_duration_seconds:
            raise ExecutionLimitExceededError(
                f"Investigation duration ({elapsed:.2f}s) exceeded limit of {self.max_duration_seconds}s"
            )

    @property
    def is_terminal(self) -> bool:
        """True if the state machine has reached a terminal state."""
        return len(self.ALLOWED_TRANSITIONS.get(self.current_state, set())) == 0
