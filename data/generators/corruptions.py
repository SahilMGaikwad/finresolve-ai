"""
FinResolve AI — Corruption Injection Engine

Applies labeled corruptions to the observed copy of case records.
Ground truth is NEVER modified.

Each corruption type maps to a real-world discrepancy scenario.
See docs/data/corruption_catalog.md for full documentation.
"""

from __future__ import annotations

import copy
import random
from uuid import UUID

from data.schemas.corruption import CorruptionLabel
from data.schemas.enums import (
    CaseDifficulty,
    CorruptionType,
    PaymentStatus,
    RecordType,
    SettlementStatus,
)
from data.schemas.money import Money


def _deterministic_uuid(rng: random.Random) -> UUID:
    """Generate deterministic UUID from the seeded RNG."""
    return UUID(int=rng.getrandbits(128))


def _deterministic_hex(rng: random.Random, length: int = 16) -> str:
    """Generate deterministic hex string from the seeded RNG."""
    return f"{rng.getrandbits(length * 4):0{length}x}"


# Corruption types available at each difficulty level
_EASY_CORRUPTIONS = [
    CorruptionType.AMOUNT_MISMATCH,
    CorruptionType.FEE_DISCREPANCY,
]

_MEDIUM_CORRUPTIONS = [
    CorruptionType.AMOUNT_MISMATCH,
    CorruptionType.FEE_DISCREPANCY,
    CorruptionType.TIMING_MISMATCH,
    CorruptionType.MISSING_RECORD,
    CorruptionType.DUPLICATE_RECORD,
]

_HARD_CORRUPTIONS = [
    CorruptionType.AMOUNT_MISMATCH,
    CorruptionType.FEE_DISCREPANCY,
    CorruptionType.TIMING_MISMATCH,
    CorruptionType.MISSING_RECORD,
    CorruptionType.DUPLICATE_RECORD,
    CorruptionType.STATUS_INCONSISTENCY,
    CorruptionType.PARTIAL_SETTLEMENT,
    CorruptionType.INCORRECT_REFERENCE,
]


def _get_corruption_pool(difficulty: CaseDifficulty) -> list[CorruptionType]:
    """Get available corruption types for a given difficulty level."""
    if difficulty == CaseDifficulty.EASY:
        return _EASY_CORRUPTIONS
    elif difficulty == CaseDifficulty.MEDIUM:
        return _MEDIUM_CORRUPTIONS
    else:
        return _HARD_CORRUPTIONS


def _apply_amount_mismatch(
    observed: dict,
    internal: dict,
    rng: random.Random,
) -> CorruptionLabel | None:
    """Modify settlement net_amount to create an amount mismatch."""
    settlements = observed.get("settlements", [])
    if not settlements:
        return None

    settlement = settlements[0]
    original_net = settlement["net_amount"]
    original_minor = original_net["amount_minor"]

    # Offset by 1%–15% of the amount
    offset_bps = rng.randint(100, 1500)
    direction = rng.choice([-1, 1])
    offset = max(1, (original_minor * offset_bps) // 10000)
    corrupted_minor = original_minor + (direction * offset)

    settlement["net_amount"] = {
        "amount_minor": corrupted_minor,
        "currency": original_net["currency"],
    }

    return CorruptionLabel(
        corruption_id=_deterministic_uuid(rng),
        case_id=internal["case_id"],
        corruption_type=CorruptionType.AMOUNT_MISMATCH,
        target_record_type=RecordType.SETTLEMENT,
        target_record_id=settlement["settlement_id"],
        target_field="net_amount",
        original_value=str(original_minor),
        corrupted_value=str(corrupted_minor),
        description=f"Settlement net_amount modified by {direction * offset} paise "
                    f"({offset_bps/100:.1f}% of original). "
                    f"Simulates incorrect settlement calculation.",
    )


def _apply_fee_discrepancy(
    observed: dict,
    internal: dict,
    rng: random.Random,
) -> CorruptionLabel | None:
    """Modify a fee amount to create a fee discrepancy."""
    fees = observed.get("fees", [])
    if not fees:
        return None

    fee = rng.choice(fees)
    original_amount = fee["amount"]
    original_minor = original_amount["amount_minor"]

    # Offset by 10%–50% of the fee
    offset_bps = rng.randint(1000, 5000)
    direction = rng.choice([-1, 1])
    offset = max(1, (original_minor * offset_bps) // 10000)
    corrupted_minor = max(0, original_minor + (direction * offset))

    fee["amount"] = {
        "amount_minor": corrupted_minor,
        "currency": original_amount["currency"],
    }

    return CorruptionLabel(
        corruption_id=_deterministic_uuid(rng),
        case_id=internal["case_id"],
        corruption_type=CorruptionType.FEE_DISCREPANCY,
        target_record_type=RecordType.FEE,
        target_record_id=fee["fee_id"],
        target_field="amount",
        original_value=str(original_minor),
        corrupted_value=str(corrupted_minor),
        description=f"Fee amount modified by {direction * offset} paise. "
                    f"Simulates incorrect fee calculation or unexpected fee.",
    )


def _apply_timing_mismatch(
    observed: dict,
    internal: dict,
    rng: random.Random,
) -> CorruptionLabel | None:
    """Shift a settlement timestamp beyond acceptable tolerance."""
    settlements = observed.get("settlements", [])
    if not settlements:
        return None

    settlement = settlements[0]
    original_time = settlement["settled_at"]

    # Shift by 3–30 days
    shift_days = rng.randint(3, 30)
    direction = rng.choice([-1, 1])

    from datetime import datetime, timedelta
    original_dt = datetime.fromisoformat(original_time)
    corrupted_dt = original_dt + timedelta(days=shift_days * direction)
    corrupted_time = corrupted_dt.isoformat()

    settlement["settled_at"] = corrupted_time

    return CorruptionLabel(
        corruption_id=_deterministic_uuid(rng),
        case_id=internal["case_id"],
        corruption_type=CorruptionType.TIMING_MISMATCH,
        target_record_type=RecordType.SETTLEMENT,
        target_record_id=settlement["settlement_id"],
        target_field="settled_at",
        original_value=original_time,
        corrupted_value=corrupted_time,
        description=f"Settlement timestamp shifted by {direction * shift_days} days. "
                    f"Simulates delayed or backdated settlement.",
    )


def _apply_missing_record(
    observed: dict,
    internal: dict,
    rng: random.Random,
) -> CorruptionLabel | None:
    """Remove a settlement or fee from observed records."""
    # Choose what to remove
    candidates = []
    if observed.get("settlements"):
        candidates.append("settlements")
    if observed.get("fees"):
        candidates.append("fees")
    if not candidates:
        return None

    target_type = rng.choice(candidates)
    record_list = observed[target_type]
    removed_index = rng.randint(0, len(record_list) - 1)
    removed = record_list.pop(removed_index)

    if target_type == "settlements":
        record_type = RecordType.SETTLEMENT
        record_id = removed["settlement_id"]
    else:
        record_type = RecordType.FEE
        record_id = removed["fee_id"]

    return CorruptionLabel(
        corruption_id=_deterministic_uuid(rng),
        case_id=internal["case_id"],
        corruption_type=CorruptionType.MISSING_RECORD,
        target_record_type=record_type,
        target_record_id=record_id,
        target_field="(entire record)",
        original_value="present",
        corrupted_value="missing",
        description=f"Removed {target_type[:-1]} record {record_id}. "
                    f"Simulates missing record in source system.",
    )


def _apply_duplicate_record(
    observed: dict,
    internal: dict,
    rng: random.Random,
) -> CorruptionLabel | None:
    """Duplicate a payment or settlement record."""
    candidates = []
    if observed.get("payments"):
        candidates.append("payments")
    if observed.get("settlements"):
        candidates.append("settlements")
    if not candidates:
        return None

    target_type = rng.choice(candidates)
    record_list = observed[target_type]
    original = record_list[0]
    duplicate = copy.deepcopy(original)
    record_list.append(duplicate)

    if target_type == "payments":
        record_id = original["payment_id"]
        record_type = RecordType.PAYMENT
    else:
        record_id = original["settlement_id"]
        record_type = RecordType.SETTLEMENT

    return CorruptionLabel(
        corruption_id=_deterministic_uuid(rng),
        case_id=internal["case_id"],
        corruption_type=CorruptionType.DUPLICATE_RECORD,
        target_record_type=record_type,
        target_record_id=record_id,
        target_field="(entire record)",
        original_value="1 instance",
        corrupted_value="2 instances",
        description=f"Duplicated {target_type[:-1]} record {record_id}. "
                    f"Simulates duplicate submission or replay.",
    )


def _apply_status_inconsistency(
    observed: dict,
    internal: dict,
    rng: random.Random,
) -> CorruptionLabel | None:
    """Make payment status inconsistent with presence of settlement."""
    payments = observed.get("payments", [])
    if not payments:
        return None

    payment = payments[0]
    original_status = payment["status"]
    # Set to a contradictory status
    corrupted_status = PaymentStatus.FAILED.value

    payment["status"] = corrupted_status

    return CorruptionLabel(
        corruption_id=_deterministic_uuid(rng),
        case_id=internal["case_id"],
        corruption_type=CorruptionType.STATUS_INCONSISTENCY,
        target_record_type=RecordType.PAYMENT,
        target_record_id=payment["payment_id"],
        target_field="status",
        original_value=original_status,
        corrupted_value=corrupted_status,
        description=f"Payment status changed to '{corrupted_status}' while settlement exists. "
                    f"Simulates status sync failure between systems.",
    )


def _apply_partial_settlement(
    observed: dict,
    internal: dict,
    rng: random.Random,
) -> CorruptionLabel | None:
    """Reduce settlement to a fraction of expected amount without explanation."""
    settlements = observed.get("settlements", [])
    if not settlements:
        return None

    settlement = settlements[0]
    original_gross = settlement["gross_amount"]
    original_minor = original_gross["amount_minor"]

    # Settle only 40%–80% of the gross
    fraction_bps = rng.randint(4000, 8000)
    corrupted_minor = (original_minor * fraction_bps) // 10000

    settlement["gross_amount"] = {
        "amount_minor": corrupted_minor,
        "currency": original_gross["currency"],
    }

    # Also adjust net_amount proportionally
    original_net = settlement["net_amount"]["amount_minor"]
    corrupted_net = (original_net * fraction_bps) // 10000
    settlement["net_amount"] = {
        "amount_minor": corrupted_net,
        "currency": settlement["net_amount"]["currency"],
    }

    return CorruptionLabel(
        corruption_id=_deterministic_uuid(rng),
        case_id=internal["case_id"],
        corruption_type=CorruptionType.PARTIAL_SETTLEMENT,
        target_record_type=RecordType.SETTLEMENT,
        target_record_id=settlement["settlement_id"],
        target_field="gross_amount",
        original_value=str(original_minor),
        corrupted_value=str(corrupted_minor),
        description=f"Settlement reduced to {fraction_bps/100:.0f}% of payment. "
                    f"Simulates partial settlement without matching second installment.",
    )


def _apply_incorrect_reference(
    observed: dict,
    internal: dict,
    rng: random.Random,
) -> CorruptionLabel | None:
    """Set wrong payment_id on a settlement."""
    settlements = observed.get("settlements", [])
    if not settlements:
        return None

    settlement = settlements[0]
    original_ref = settlement["payment_id"]
    fake_ref = f"pay_{_deterministic_hex(rng)}"

    settlement["payment_id"] = fake_ref

    return CorruptionLabel(
        corruption_id=_deterministic_uuid(rng),
        case_id=internal["case_id"],
        corruption_type=CorruptionType.INCORRECT_REFERENCE,
        target_record_type=RecordType.SETTLEMENT,
        target_record_id=settlement["settlement_id"],
        target_field="payment_id",
        original_value=original_ref,
        corrupted_value=fake_ref,
        description=f"Settlement payment_id changed to a non-existent payment. "
                    f"Simulates cross-reference error between systems.",
    )


# Map corruption types to their implementation functions
_CORRUPTION_HANDLERS: dict[CorruptionType, callable] = {
    CorruptionType.AMOUNT_MISMATCH: _apply_amount_mismatch,
    CorruptionType.FEE_DISCREPANCY: _apply_fee_discrepancy,
    CorruptionType.TIMING_MISMATCH: _apply_timing_mismatch,
    CorruptionType.MISSING_RECORD: _apply_missing_record,
    CorruptionType.DUPLICATE_RECORD: _apply_duplicate_record,
    CorruptionType.STATUS_INCONSISTENCY: _apply_status_inconsistency,
    CorruptionType.PARTIAL_SETTLEMENT: _apply_partial_settlement,
    CorruptionType.INCORRECT_REFERENCE: _apply_incorrect_reference,
}


def apply_corruptions(
    observed: dict,
    internal: dict,
    difficulty: CaseDifficulty,
    rng: random.Random,
) -> list[CorruptionLabel]:
    """
    Apply one or more corruptions to observed records.

    Args:
        observed: The observed records dict (will be mutated).
        internal: Internal metadata from case construction.
        difficulty: Case difficulty (controls available corruption types).
        rng: Seeded Random instance.

    Returns:
        List of CorruptionLabel instances describing what was corrupted.
    """
    pool = _get_corruption_pool(difficulty)

    # Number of corruptions: easy=1, medium=1-2, hard=1-3
    if difficulty == CaseDifficulty.EASY:
        num_corruptions = 1
    elif difficulty == CaseDifficulty.MEDIUM:
        num_corruptions = rng.randint(1, 2)
    else:
        num_corruptions = rng.randint(1, 3)

    # Select distinct corruption types to avoid mutually-cancelling or duplicate operations
    selected = rng.sample(pool, k=min(num_corruptions, len(pool)))
    if CorruptionType.DUPLICATE_RECORD in selected and CorruptionType.MISSING_RECORD in selected:
        selected.remove(CorruptionType.MISSING_RECORD)

    labels: list[CorruptionLabel] = []
    for corruption_type in selected:
        handler = _CORRUPTION_HANDLERS[corruption_type]
        label = handler(observed, internal, rng)
        if label is not None:
            labels.append(label)

    return labels

