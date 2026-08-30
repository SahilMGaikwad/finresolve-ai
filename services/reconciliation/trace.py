"""
FinResolve AI — Audit & Explanation Trace Recorder

Records an auditable, step-by-step reasoning trace during reconciliation.
"""

from __future__ import annotations

from typing import Any

from data.schemas.reconciliation_result import TraceStep


class TraceRecorder:
    """
    Helper to record observable step-by-step calculation and decision traces.
    """

    def __init__(self):
        self._steps: list[TraceStep] = []
        self._step_counter = 1

    def record_step(
        self,
        phase: str,
        description: str,
        outcome: str,
        inputs: dict[str, Any] | None = None,
        calculation: str | None = None,
    ) -> None:
        """Add an audit trace step."""
        step = TraceStep(
            step_number=self._step_counter,
            phase=phase,
            description=description,
            inputs=inputs or {},
            calculation=calculation,
            outcome=outcome,
        )
        self._steps.append(step)
        self._step_counter += 1

    def get_trace(self) -> list[TraceStep]:
        """Return the full recorded trace."""
        return list(self._steps)
