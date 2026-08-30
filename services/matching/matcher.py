"""
FinResolve AI — Deterministic Multi-Signal Record Matcher

Groups observed financial records into coherent MatchGroups using multi-signal scoring,
supporting 1:1, 1:N, and N:1 relationships without forcing artificial matches.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from data.schemas.case import CaseRecords
from data.schemas.enums import RecordType
from data.schemas.matching import MatchCandidate, MatchGroup, MatchSignal, MatchState
from services.matching.signals import (
    evaluate_amount_signal,
    evaluate_currency_signal,
    evaluate_merchant_signal,
    evaluate_reference_signal,
    evaluate_timestamp_proximity_signal,
)

logger = logging.getLogger("finresolve.matching")


@dataclass
class MatcherConfig:
    """Configurable thresholds for matching classification."""
    match_threshold: float = 0.70       # Score >= 0.70 qualifies as MATCHED
    probable_threshold: float = 0.50    # Score >= 0.50 qualifies as PROBABLE_MATCH
    ambiguity_margin: float = 0.05      # Competing candidates within 0.05 are AMBIGUOUS
    
    # Signal weight distribution (sums to 1.0)
    weight_reference: float = 0.40
    weight_amount: float = 0.25
    weight_timestamp: float = 0.15
    weight_currency: float = 0.10
    weight_merchant: float = 0.10


def evaluate_pair(
    primary: dict[str, Any],
    candidate: dict[str, Any],
    config: MatcherConfig | None = None,
) -> tuple[float, list[MatchSignal]]:
    """
    Evaluates a candidate record against a primary record across all 5 signals.
    """
    cfg = config or MatcherConfig()
    
    s_ref = evaluate_reference_signal(primary, candidate, weight=cfg.weight_reference)
    s_amt = evaluate_amount_signal(primary, candidate, weight=cfg.weight_amount)
    s_time = evaluate_timestamp_proximity_signal(primary, candidate, weight=cfg.weight_timestamp)
    s_curr = evaluate_currency_signal(primary, candidate, weight=cfg.weight_currency)
    s_merch = evaluate_merchant_signal(primary, candidate, weight=cfg.weight_merchant)

    signals = [s_ref, s_amt, s_time, s_curr, s_merch]
    total_score = sum(s.weighted_score for s in signals)
    
    return round(total_score, 4), signals


class RecordMatcher:
    """
    Deterministic matching engine for case-based financial records.
    """

    def __init__(self, config: MatcherConfig | None = None):
        self.config = config or MatcherConfig()

    def match_records(
        self,
        records: CaseRecords,
    ) -> tuple[list[MatchGroup], dict[str, list[str]]]:
        """
        Form MatchGroups from observed records.

        Args:
            records: Observed financial records (CaseRecords).

        Returns:
            Tuple of (list of formed MatchGroups, dict of unmatched record IDs by type).
        """
        payments = list(records.payments)
        orders = list(records.orders)
        settlements = list(records.settlements)
        fees = list(records.fees)
        refunds = list(records.refunds)
        ledger_entries = list(records.ledger_entries)
        payouts = list(records.payouts)

        matched_orders: set[str] = set()
        matched_settlements: set[str] = set()
        matched_fees: set[str] = set()
        matched_refunds: set[str] = set()
        matched_ledger_entries: set[str] = set()
        matched_payouts: set[str] = set()

        groups: list[MatchGroup] = []

        # 1. Primary pass: Anchor around Payments
        for payment in payments:
            pay_id = payment.get("payment_id", "")
            group_evaluations: list[MatchCandidate] = []
            
            # Match Order (1:1)
            matched_order_id = None
            order_candidates = self._score_candidates(payment, orders, matched_orders, "order_id", RecordType.ORDER)
            if order_candidates:
                best_order = order_candidates[0]
                group_evaluations.append(best_order)
                if best_order.state in (MatchState.MATCHED, MatchState.PROBABLE_MATCH):
                    matched_order_id = best_order.target_record_id
                    matched_orders.add(matched_order_id)

            # Match Settlements (1:1 or 1:N)
            matched_stl_ids: list[str] = []
            stl_candidates = self._score_candidates(payment, settlements, matched_settlements, "settlement_id", RecordType.SETTLEMENT)
            for c in stl_candidates:
                group_evaluations.append(c)
                if c.state in (MatchState.MATCHED, MatchState.PROBABLE_MATCH):
                    matched_stl_ids.append(c.target_record_id)
                    matched_settlements.add(c.target_record_id)

            # Match Fees (1:N)
            matched_fee_ids: list[str] = []
            fee_candidates = self._score_candidates(payment, fees, matched_fees, "fee_id", RecordType.FEE)
            for c in fee_candidates:
                group_evaluations.append(c)
                if c.state in (MatchState.MATCHED, MatchState.PROBABLE_MATCH):
                    matched_fee_ids.append(c.target_record_id)
                    matched_fees.add(c.target_record_id)

            # Match Refunds (1:N)
            matched_rfnd_ids: list[str] = []
            rfnd_candidates = self._score_candidates(payment, refunds, matched_refunds, "refund_id", RecordType.REFUND)
            for c in rfnd_candidates:
                group_evaluations.append(c)
                if c.state in (MatchState.MATCHED, MatchState.PROBABLE_MATCH):
                    matched_rfnd_ids.append(c.target_record_id)
                    matched_refunds.add(c.target_record_id)

            # Match Ledger Entries (1:N)
            matched_le_ids: list[str] = []
            le_candidates = self._score_candidates(payment, ledger_entries, matched_ledger_entries, "entry_id", RecordType.LEDGER_ENTRY)
            for c in le_candidates:
                group_evaluations.append(c)
                if c.state in (MatchState.MATCHED, MatchState.PROBABLE_MATCH):
                    matched_le_ids.append(c.target_record_id)
                    matched_ledger_entries.add(c.target_record_id)

            # Determine aggregate group match state and confidence
            group_state = MatchState.MATCHED
            if any(e.state == MatchState.AMBIGUOUS for e in group_evaluations):
                group_state = MatchState.AMBIGUOUS
            elif any(e.state == MatchState.CONFLICT for e in group_evaluations):
                group_state = MatchState.CONFLICT
            elif any(e.state == MatchState.PROBABLE_MATCH for e in group_evaluations):
                group_state = MatchState.PROBABLE_MATCH
            elif not matched_order_id and not matched_stl_ids and not matched_fee_ids:
                group_state = MatchState.UNMATCHED

            # Calculate average confidence across accepted matches
            accepted_evals = [e for e in group_evaluations if e.state in (MatchState.MATCHED, MatchState.PROBABLE_MATCH)]
            avg_conf = (sum(e.aggregate_score for e in accepted_evals) / len(accepted_evals)) if accepted_evals else 0.5

            group = MatchGroup(
                payment_id=pay_id,
                order_id=matched_order_id,
                settlement_ids=matched_stl_ids,
                fee_ids=matched_fee_ids,
                refund_ids=matched_rfnd_ids,
                ledger_entry_ids=matched_le_ids,
                match_state=group_state,
                confidence=round(avg_conf, 4),
                candidate_evaluations=group_evaluations,
            )
            groups.append(group)

        # 2. Identify unmatched records
        unmatched: dict[str, list[str]] = {
            "payments": [p.get("payment_id", "") for p in payments if not any(g.payment_id == p.get("payment_id") for g in groups)],
            "orders": [o.get("order_id", "") for o in orders if o.get("order_id") not in matched_orders],
            "settlements": [s.get("settlement_id", "") for s in settlements if s.get("settlement_id") not in matched_settlements],
            "fees": [f.get("fee_id", "") for f in fees if f.get("fee_id") not in matched_fees],
            "refunds": [r.get("refund_id", "") for r in refunds if r.get("refund_id") not in matched_refunds],
            "ledger_entries": [le.get("entry_id", "") for le in ledger_entries if le.get("entry_id") not in matched_ledger_entries],
            "payouts": [p.get("payout_id", "") for p in payouts if p.get("payout_id") not in matched_payouts],
        }

        return groups, unmatched

    def _score_candidates(
        self,
        primary: dict[str, Any],
        candidates: list[dict[str, Any]],
        already_matched: set[str],
        id_field: str,
        target_type: RecordType,
    ) -> list[MatchCandidate]:
        """Score candidate records and rank them with matching state."""
        evaluated: list[tuple[float, MatchCandidate]] = []
        
        for cand in candidates:
            cand_id = str(cand.get(id_field, ""))
            if not cand_id or cand_id in already_matched:
                continue

            score, signals = evaluate_pair(primary, cand, self.config)

            # Classify match state
            if score >= self.config.match_threshold:
                state = MatchState.MATCHED
            elif score >= self.config.probable_threshold:
                state = MatchState.PROBABLE_MATCH
            else:
                state = MatchState.UNMATCHED

            candidate_eval = MatchCandidate(
                target_record_id=cand_id,
                target_record_type=target_type,
                aggregate_score=score,
                signals=signals,
                state=state,
            )
            evaluated.append((score, candidate_eval))

        # Sort descending by aggregate score
        evaluated.sort(key=lambda x: x[0], reverse=True)

        # Check for ambiguity among top candidates for 1:1 relationships
        is_one_to_one = target_type in (RecordType.ORDER, RecordType.SETTLEMENT)
        if is_one_to_one and len(evaluated) > 1:
            top_score = evaluated[0][0]
            second_score = evaluated[1][0]
            if top_score >= self.config.probable_threshold and (top_score - second_score) <= self.config.ambiguity_margin:
                evaluated[0][1].state = MatchState.AMBIGUOUS
                evaluated[1][1].state = MatchState.AMBIGUOUS

        return [e[1] for e in evaluated]
