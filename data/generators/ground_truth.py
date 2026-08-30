"""
FinResolve AI — Ground Truth Construction

Builds expected outcome labels for each reconciliation case
based on the corruptions applied.
"""

from __future__ import annotations

from data.schemas.case import ExpectedOutcome
from data.schemas.corruption import CorruptionLabel
from data.schemas.enums import CaseDifficulty, CorruptionType


def build_expected_outcome(
    corruptions: list[CorruptionLabel],
    difficulty: CaseDifficulty,
) -> ExpectedOutcome:
    """
    Construct the ground-truth expected outcome for a case.

    Args:
        corruptions: List of corruption labels applied to this case.
        difficulty: Case difficulty level.

    Returns:
        ExpectedOutcome describing what a correct system should conclude.
    """
    if not corruptions:
        return ExpectedOutcome(
            has_discrepancy=False,
            discrepancy_type=None,
            root_cause=None,
            correct_resolution=None,
            should_escalate=False,
        )

    # Determine discrepancy type and root cause from corruptions
    corruption_types = [c.corruption_type for c in corruptions]
    primary_corruption = corruptions[0]

    # Multiple different corruption types → compound, should escalate
    unique_types = set(corruption_types)
    is_compound = len(unique_types) > 1

    # Map corruption type to discrepancy description
    discrepancy_type = _corruption_to_discrepancy(primary_corruption.corruption_type)
    if is_compound:
        discrepancy_type = "compound_discrepancy"

    root_cause = _corruption_to_root_cause(primary_corruption.corruption_type)
    if is_compound:
        root_cause = "multiple_causes"

    # Build correct resolution
    correct_resolution = _build_resolution(corruptions)

    # Determine escalation
    should_escalate = _should_escalate(corruptions, difficulty)

    return ExpectedOutcome(
        has_discrepancy=True,
        discrepancy_type=discrepancy_type,
        root_cause=root_cause,
        correct_resolution=correct_resolution,
        should_escalate=should_escalate,
    )


def _corruption_to_discrepancy(corruption_type: CorruptionType) -> str:
    """Map a corruption type to its expected discrepancy type label."""
    mapping = {
        CorruptionType.AMOUNT_MISMATCH: "settlement_amount_mismatch",
        CorruptionType.MISSING_RECORD: "missing_record",
        CorruptionType.DUPLICATE_RECORD: "duplicate_record",
        CorruptionType.FEE_DISCREPANCY: "fee_calculation_error",
        CorruptionType.TIMING_MISMATCH: "settlement_timing_anomaly",
        CorruptionType.STATUS_INCONSISTENCY: "status_sync_failure",
        CorruptionType.PARTIAL_SETTLEMENT: "partial_settlement",
        CorruptionType.INCORRECT_REFERENCE: "broken_reference",
    }
    return mapping.get(corruption_type, "unknown_discrepancy")


def _corruption_to_root_cause(corruption_type: CorruptionType) -> str:
    """Map a corruption type to its expected root cause label."""
    mapping = {
        CorruptionType.AMOUNT_MISMATCH: "incorrect_settlement_calculation",
        CorruptionType.MISSING_RECORD: "record_missing_from_source",
        CorruptionType.DUPLICATE_RECORD: "duplicate_submission",
        CorruptionType.FEE_DISCREPANCY: "fee_rate_miscalculation",
        CorruptionType.TIMING_MISMATCH: "settlement_delay",
        CorruptionType.STATUS_INCONSISTENCY: "cross_system_sync_failure",
        CorruptionType.PARTIAL_SETTLEMENT: "incomplete_settlement",
        CorruptionType.INCORRECT_REFERENCE: "reference_id_error",
    }
    return mapping.get(corruption_type, "unknown_cause")


def _build_resolution(corruptions: list[CorruptionLabel]) -> dict:
    """Build a ground-truth resolution describing how to fix the corruptions."""
    actions = []
    for corruption in corruptions:
        action = {
            "corruption_type": corruption.corruption_type.value,
            "action": _corruption_to_action(corruption.corruption_type),
            "target_record_id": corruption.target_record_id,
            "target_field": corruption.target_field,
            "correct_value": corruption.original_value,
        }
        actions.append(action)

    return {"actions": actions, "action_count": len(actions)}


def _corruption_to_action(corruption_type: CorruptionType) -> str:
    """Map a corruption type to the corrective action."""
    mapping = {
        CorruptionType.AMOUNT_MISMATCH: "correct_amount",
        CorruptionType.MISSING_RECORD: "flag_missing_record",
        CorruptionType.DUPLICATE_RECORD: "remove_duplicate",
        CorruptionType.FEE_DISCREPANCY: "correct_fee",
        CorruptionType.TIMING_MISMATCH: "flag_timing_anomaly",
        CorruptionType.STATUS_INCONSISTENCY: "reconcile_status",
        CorruptionType.PARTIAL_SETTLEMENT: "flag_partial_settlement",
        CorruptionType.INCORRECT_REFERENCE: "correct_reference",
    }
    return mapping.get(corruption_type, "investigate")


def _should_escalate(
    corruptions: list[CorruptionLabel],
    difficulty: CaseDifficulty,
) -> bool:
    """
    Determine if this case should be escalated to human review.

    Escalation is the correct outcome when:
    - Multiple different corruption types (compound discrepancy)
    - Hard difficulty cases (by design)
    - Certain ambiguous corruption types
    """
    unique_types = {c.corruption_type for c in corruptions}

    # Compound discrepancies should always escalate
    if len(unique_types) > 1:
        return True

    # Hard difficulty should often escalate
    if difficulty == CaseDifficulty.HARD:
        return True

    # Certain types are inherently ambiguous
    ambiguous_types = {
        CorruptionType.STATUS_INCONSISTENCY,
        CorruptionType.INCORRECT_REFERENCE,
    }
    if unique_types & ambiguous_types:
        return True

    return False
