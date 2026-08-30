"""
FinResolve AI — Counterfactual State Manager

Provides isolated, deep-cloned virtual state for counterfactual simulation.
Applies candidate resolution actions strictly to in-memory projections without mutating source records.
"""

from __future__ import annotations

import copy
from typing import Any

from data.schemas.case import CaseRecords
from data.schemas.enums import RecordType
from data.schemas.resolution import CounterfactualState, ResolutionAction, ResolutionActionType


def create_counterfactual_state(case_id: str, records: CaseRecords) -> CounterfactualState:
    """Create an isolated deep copy of CaseRecords for virtual simulation."""
    cloned_records = CaseRecords(
        payments=[copy.deepcopy(p) for p in records.payments],
        orders=[copy.deepcopy(o) for o in records.orders],
        settlements=[copy.deepcopy(s) for s in records.settlements],
        fees=[copy.deepcopy(f) for f in records.fees],
        refunds=[copy.deepcopy(r) for r in records.refunds],
        ledger_entries=[copy.deepcopy(l) for l in records.ledger_entries],
        payouts=[copy.deepcopy(p) for p in records.payouts],
    )
    return CounterfactualState(
        case_id=case_id,
        projected_records=cloned_records,
        mutated_record_ids=[],
        reconstructed_record_ids=[],
        virtual_ledger_entries=[],
    )


def _get_id(rec: dict[str, Any] | Any, id_field: str) -> str:
    if isinstance(rec, dict):
        return str(rec.get(id_field, ""))
    return str(getattr(rec, id_field, ""))


def apply_action_to_state(
    state: CounterfactualState,
    action: ResolutionAction,
) -> CounterfactualState:
    """
    Apply a proposed ResolutionAction to the CounterfactualState.
    Returns the modified state with mutated record tracking.
    """
    params = action.parameters
    records = state.projected_records

    if action.action_type == ResolutionActionType.SETTLEMENT_ADJUSTMENT:
        target_s = next((s for s in records.settlements if _get_id(s, "settlement_id") == action.target_record_id), None)
        if target_s is not None:
            if isinstance(target_s, dict):
                if "adjusted_net_amount_minor" in params:
                    target_s["net_amount"] = {"amount_minor": params["adjusted_net_amount_minor"], "currency": "INR"}
                if "adjusted_fee_amount_minor" in params:
                    target_s["fee_amount"] = {"amount_minor": params["adjusted_fee_amount_minor"], "currency": "INR"}
                if "adjusted_gross_amount_minor" in params:
                    target_s["gross_amount"] = {"amount_minor": params["adjusted_gross_amount_minor"], "currency": "INR"}
            state.mutated_record_ids.append(action.target_record_id)

        elif "create_settlement" in params and params["create_settlement"]:
            new_settlement = params["settlement_data"]
            records.settlements.append(new_settlement)
            state.reconstructed_record_ids.append(_get_id(new_settlement, "settlement_id"))

    elif action.action_type == ResolutionActionType.FEE_ADJUSTMENT:
        target_f = next((f for f in records.fees if _get_id(f, "fee_id") == action.target_record_id), None)
        if target_f is not None:
            if isinstance(target_f, dict):
                if "adjusted_amount_minor" in params:
                    target_f["amount"] = {"amount_minor": params["adjusted_amount_minor"], "currency": "INR"}
                if "adjusted_rate_bps" in params:
                    target_f["rate_bps"] = params["adjusted_rate_bps"]
                if "adjusted_tax_minor" in params:
                    target_f["tax_amount"] = {"amount_minor": params["adjusted_tax_minor"], "currency": "INR"}
            state.mutated_record_ids.append(action.target_record_id)

        # Synchronize associated GST fee if present
        if "gst_fee_id" in params and "adjusted_gst_minor" in params:
            gst_f = next((f for f in records.fees if _get_id(f, "fee_id") == params["gst_fee_id"]), None)
            if gst_f and isinstance(gst_f, dict):
                gst_f["amount"] = {"amount_minor": params["adjusted_gst_minor"], "currency": "INR"}
                state.mutated_record_ids.append(params["gst_fee_id"])

        # Synchronize settlement net and fee amounts
        if records.settlements and ("adjusted_total_fees" in params or "adjusted_net_amount_minor" in params):
            s = records.settlements[0]
            if isinstance(s, dict):
                if "adjusted_total_fees" in params:
                    s["fee_amount"] = {"amount_minor": params["adjusted_total_fees"], "currency": "INR"}
                if "adjusted_net_amount_minor" in params:
                    s["net_amount"] = {"amount_minor": params["adjusted_net_amount_minor"], "currency": "INR"}
                state.mutated_record_ids.append(_get_id(s, "settlement_id"))

    elif action.action_type == ResolutionActionType.REFERENCE_CORRECTION:
        field_to_correct = params.get("reference_field", "payment_id")
        corrected_value = params.get("corrected_id")

        if action.target_record_type == RecordType.SETTLEMENT:
            for s in records.settlements:
                if _get_id(s, "settlement_id") == action.target_record_id:
                    if isinstance(s, dict):
                        s[field_to_correct] = corrected_value
                    state.mutated_record_ids.append(action.target_record_id)
        elif action.target_record_type == RecordType.FEE:
            for f in records.fees:
                if _get_id(f, "fee_id") == action.target_record_id:
                    if isinstance(f, dict):
                        f[field_to_correct] = corrected_value
                    state.mutated_record_ids.append(action.target_record_id)
        elif action.target_record_type == RecordType.REFUND:
            for r in records.refunds:
                if _get_id(r, "refund_id") == action.target_record_id:
                    if isinstance(r, dict):
                        r[field_to_correct] = corrected_value
                    state.mutated_record_ids.append(action.target_record_id)

    elif action.action_type == ResolutionActionType.STATUS_CORRECTION:
        target_status = params.get("corrected_status")
        if action.target_record_type == RecordType.PAYMENT:
            for p in records.payments:
                if _get_id(p, "payment_id") == action.target_record_id:
                    if isinstance(p, dict):
                        p["status"] = target_status
                    state.mutated_record_ids.append(action.target_record_id)
        elif action.target_record_type == RecordType.SETTLEMENT:
            for s in records.settlements:
                if _get_id(s, "settlement_id") == action.target_record_id:
                    if isinstance(s, dict):
                        s["status"] = target_status
                    state.mutated_record_ids.append(action.target_record_id)

    elif action.action_type == ResolutionActionType.MISSING_RECORD_RECONSTRUCTION:
        rec_type = action.target_record_type
        record_data = params.get("record_data", {})
        
        if rec_type == RecordType.SETTLEMENT and record_data:
            records.settlements.append(record_data)
            state.reconstructed_record_ids.append(_get_id(record_data, "settlement_id"))
        elif rec_type == RecordType.FEE and record_data:
            records.fees.append(record_data)
            state.reconstructed_record_ids.append(_get_id(record_data, "fee_id"))
        elif rec_type == RecordType.PAYMENT and record_data:
            records.payments.append(record_data)
            state.reconstructed_record_ids.append(_get_id(record_data, "payment_id"))

    elif action.action_type == ResolutionActionType.LEDGER_CORRECTION:
        # Check if action is duplicate removal
        dup_id = params.get("remove_duplicate_record_id")
        if dup_id:
            records.settlements = [s for s in records.settlements if _get_id(s, "settlement_id") != dup_id]
            records.payments = [p for p in records.payments if _get_id(p, "payment_id") != dup_id]
            records.fees = [f for f in records.fees if _get_id(f, "fee_id") != dup_id]
            state.mutated_record_ids.append(dup_id)
        else:
            entry_data = params.get("ledger_entry", {})
            if entry_data:
                records.ledger_entries.append(entry_data)
                state.virtual_ledger_entries.append(entry_data)
                state.reconstructed_record_ids.append(_get_id(entry_data, "entry_id"))

    return state
