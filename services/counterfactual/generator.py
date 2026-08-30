"""
FinResolve AI — Candidate Resolution Action Generator

Deterministically maps detected discrepancies and diagnostic root causes into
concrete candidate ResolutionAction proposals.
Operates strictly on observed records and diagnostic evidence (zero ground-truth access).
"""

from __future__ import annotations

from typing import Any

from data.schemas.case import CaseRecords
from data.schemas.discrepancy import Discrepancy, RootCauseHypothesis
from data.schemas.enums import RecordType
from data.schemas.resolution import ResolutionAction, ResolutionActionType


def _get_val(rec: dict[str, Any] | Any, key: str, default: Any = None) -> Any:
    """Safely extract field from dict or object."""
    if isinstance(rec, dict):
        return rec.get(key, default)
    return getattr(rec, key, default)


def _get_amount_minor(rec: dict[str, Any] | Any, field: str = "amount") -> int:
    """Extract minor currency unit integer from Money dict or object."""
    val = _get_val(rec, field)
    if isinstance(val, dict):
        return int(val.get("amount_minor", 0))
    elif hasattr(val, "amount_minor"):
        return int(val.amount_minor)
    elif isinstance(val, int):
        return val
    return 0


class CandidateActionGenerator:
    """
    Generates structured candidate resolution actions for detected financial discrepancies.
    """

    def generate_candidate_actions(
        self,
        case_id: str,
        records: CaseRecords,
        discrepancies: list[Discrepancy],
        hypotheses: list[RootCauseHypothesis] | None = None,
    ) -> list[ResolutionAction]:
        """Generate candidate resolution actions for all discrepancies in a case."""
        actions: list[ResolutionAction] = []

        for disc in discrepancies:
            candidate = self._generate_action_for_discrepancy(disc, records)
            if candidate:
                actions.append(candidate)

        return actions

    def _generate_action_for_discrepancy(
        self,
        disc: Discrepancy,
        records: CaseRecords,
    ) -> ResolutionAction | None:
        dtype = disc.discrepancy_type

        # 1. Settlement Amount Mismatch
        if dtype in ("settlement_amount_mismatch", "incorrect_settlement_calculation"):
            target_s = records.settlements[0] if records.settlements else None
            if target_s and records.payments:
                target_p = records.payments[0]
                p_gross = _get_amount_minor(target_p, "amount")
                total_fees = sum(_get_amount_minor(f, "amount") for f in records.fees) if records.fees else _get_amount_minor(target_s, "fee_amount")
                expected_net = p_gross - total_fees
                s_id = _get_val(target_s, "settlement_id")

                return ResolutionAction(
                    action_type=ResolutionActionType.SETTLEMENT_ADJUSTMENT,
                    target_record_id=s_id,
                    target_record_type=RecordType.SETTLEMENT,
                    parameters={
                        "adjusted_gross_amount_minor": p_gross,
                        "adjusted_fee_amount_minor": total_fees,
                        "adjusted_net_amount_minor": expected_net,
                    },
                    justification=(
                        f"Adjust settlement net to {expected_net} paise (Payment gross {p_gross} "
                        f"minus Total Fees {total_fees}) to resolve settlement amount discrepancy."
                    ),
                )

        # 2. Fee Rate Miscalculation / Fee Mismatch
        elif dtype in ("fee_rate_miscalculation", "fee_calculation_error", "fee_amount_mismatch"):
            # Target the platform fee or primary fee
            target_f = next((f for f in records.fees if _get_val(f, "fee_type") == "platform_fee"), None) or (records.fees[0] if records.fees else None)
            if target_f and records.payments:
                target_p = records.payments[0]
                p_gross = _get_amount_minor(target_p, "amount")
                raw_rate = _get_val(target_f, "rate_bps", 200)
                rate_bps = raw_rate if (raw_rate and raw_rate > 0) else 200
                expected_fee = (p_gross * rate_bps) // 10000
                f_id = _get_val(target_f, "fee_id")

                # If GST fee exists, compute corresponding 18% GST (1800 bps)
                gst_fee = next((f for f in records.fees if _get_val(f, "fee_type") == "gst"), None)
                gst_adj = (expected_fee * 1800) // 10000 if gst_fee else 0

                params: dict[str, Any] = {
                    "adjusted_amount_minor": expected_fee,
                    "adjusted_rate_bps": rate_bps,
                }
                if gst_fee:
                    params["gst_fee_id"] = _get_val(gst_fee, "fee_id")
                    params["adjusted_gst_minor"] = gst_adj
                    params["adjusted_total_fees"] = expected_fee + gst_adj
                    params["adjusted_net_amount_minor"] = p_gross - (expected_fee + gst_adj)

                return ResolutionAction(
                    action_type=ResolutionActionType.FEE_ADJUSTMENT,
                    target_record_id=f_id,
                    target_record_type=RecordType.FEE,
                    parameters=params,
                    justification=(
                        f"Recalculate platform fee to {expected_fee} paise (rate {rate_bps} bps) and synchronize settlement net."
                    ),
                )

        # 3. Missing Settlement / Split Settlement Incompletion
        elif dtype in ("missing_settlement", "record_missing_from_source", "missing_record", "partial_settlement"):
            if records.payments:
                target_p = records.payments[0]
                p_gross = _get_amount_minor(target_p, "amount")
                p_id = _get_val(target_p, "payment_id")
                m_id = _get_val(target_p, "merchant_id")
                captured_at = _get_val(target_p, "captured_at", "2026-03-16T10:00:00+00:00")

                settled_total = sum(_get_amount_minor(s, "net_amount") for s in records.settlements)
                total_fees = sum(_get_amount_minor(f, "amount") for f in records.fees)
                remaining_net = p_gross - total_fees - settled_total

                if remaining_net > 0 or not records.settlements:
                    target_net = remaining_net if remaining_net > 0 else (p_gross - total_fees)
                    new_settlement_id = f"stl_recon_{p_id}"
                    return ResolutionAction(
                        action_type=ResolutionActionType.MISSING_RECORD_RECONSTRUCTION,
                        target_record_id=new_settlement_id,
                        target_record_type=RecordType.SETTLEMENT,
                        parameters={
                            "record_data": {
                                "record_type": "settlement",
                                "settlement_id": new_settlement_id,
                                "payment_id": p_id,
                                "merchant_id": m_id,
                                "gross_amount": {"amount_minor": p_gross, "currency": "INR"},
                                "fee_amount": {"amount_minor": total_fees, "currency": "INR"},
                                "net_amount": {"amount_minor": target_net, "currency": "INR"},
                                "status": "processed",
                                "settled_at": captured_at,
                            },
                        },
                        justification=f"Reconstruct missing settlement record with net {target_net} paise for payment {p_id}.",
                    )

        # 4. Reference ID Error / Broken Reference
        elif dtype in ("reference_id_error", "broken_reference", "foreign_reference_conflict"):
            if records.payments:
                target_p = records.payments[0]
                p_id = _get_val(target_p, "payment_id")

                if records.settlements and _get_val(records.settlements[0], "payment_id") != p_id:
                    s = records.settlements[0]
                    s_id = _get_val(s, "settlement_id")
                    return ResolutionAction(
                        action_type=ResolutionActionType.REFERENCE_CORRECTION,
                        target_record_id=s_id,
                        target_record_type=RecordType.SETTLEMENT,
                        parameters={
                            "reference_field": "payment_id",
                            "corrected_id": p_id,
                        },
                        justification=f"Correct settlement payment_id reference from '{_get_val(s, 'payment_id')}' to '{p_id}'.",
                    )
                elif records.fees and _get_val(records.fees[0], "payment_id") != p_id:
                    f = records.fees[0]
                    f_id = _get_val(f, "fee_id")
                    return ResolutionAction(
                        action_type=ResolutionActionType.REFERENCE_CORRECTION,
                        target_record_id=f_id,
                        target_record_type=RecordType.FEE,
                        parameters={
                            "reference_field": "payment_id",
                            "corrected_id": p_id,
                        },
                        justification=f"Correct fee payment_id reference from '{_get_val(f, 'payment_id')}' to '{p_id}'.",
                    )

        # 5. Status Synchronization Failure
        elif dtype in ("status_sync_failure", "status_inconsistency"):
            if records.settlements and records.payments:
                s = records.settlements[0]
                p = records.payments[0]
                s_status = _get_val(s, "status")
                s_status_str = s_status.value if hasattr(s_status, "value") else str(s_status)
                p_status = _get_val(p, "status")
                p_status_str = p_status.value if hasattr(p_status, "value") else str(p_status)
                p_id = _get_val(p, "payment_id")
                s_id = _get_val(s, "settlement_id")

                if s_status_str == "processed" and p_status_str != "captured":
                    return ResolutionAction(
                        action_type=ResolutionActionType.STATUS_CORRECTION,
                        target_record_id=p_id,
                        target_record_type=RecordType.PAYMENT,
                        parameters={"corrected_status": "captured"},
                        justification=f"Synchronize payment status to 'captured' in accordance with processed settlement {s_id}.",
                    )

        # 6. Duplicate Record Resolution
        elif dtype in ("duplicate_record", "duplicate_submission"):
            if len(records.settlements) > 1:
                dup_s = records.settlements[1]
                dup_id = _get_val(dup_s, "settlement_id")
                return ResolutionAction(
                    action_type=ResolutionActionType.LEDGER_CORRECTION,
                    target_record_id=dup_id,
                    target_record_type=RecordType.SETTLEMENT,
                    parameters={
                        "remove_duplicate_record_id": dup_id,
                        "duplicate_type": "settlement",
                    },
                    justification=f"Compensate and eliminate duplicate settlement {dup_id} to restore balanced ledger.",
                )
            elif len(records.payments) > 1:
                dup_p = records.payments[1]
                dup_id = _get_val(dup_p, "payment_id")
                return ResolutionAction(
                    action_type=ResolutionActionType.LEDGER_CORRECTION,
                    target_record_id=dup_id,
                    target_record_type=RecordType.PAYMENT,
                    parameters={
                        "remove_duplicate_record_id": dup_id,
                        "duplicate_type": "payment",
                    },
                    justification=f"Compensate and eliminate duplicate payment {dup_id} to restore balanced ledger.",
                )
            elif len(records.fees) > 2:
                dup_f = records.fees[-1]
                dup_id = _get_val(dup_f, "fee_id")
                return ResolutionAction(
                    action_type=ResolutionActionType.LEDGER_CORRECTION,
                    target_record_id=dup_id,
                    target_record_type=RecordType.FEE,
                    parameters={
                        "remove_duplicate_record_id": dup_id,
                        "duplicate_type": "fee",
                    },
                    justification=f"Compensate and eliminate duplicate fee {dup_id} to restore balanced ledger.",
                )

        return None
