"""
FinResolve AI — Deterministic Diagnosis & Root-Cause Engine

Derives structured Discrepancies and ranked RootCauseHypotheses
purely from observable evidence and rule results without an LLM.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

from data.schemas.discrepancy import Discrepancy, RootCauseHypothesis
from data.schemas.enums import RecordType
from data.schemas.evidence import Evidence, EvidenceType, Severity
from data.schemas.matching import MatchGroup
from services.reconciliation.rules.base import RuleResult


class DeterministicDiagnoser:
    """
    Analyzes rule results and evidence to categorize discrepancies
    and generate mechanically plausible root-cause hypotheses.
    """

    def diagnose_case(
        self,
        case_id: str,
        groups: list[MatchGroup],
        unmatched_records: dict[str, list[str]],
        rule_results: list[RuleResult],
        evidence_list: list[Evidence],
        records_lookup: dict[str, dict[str, Any]],
    ) -> list[Discrepancy]:
        """
        Produce a list of Discrepancies with ranked candidate hypotheses.
        """
        discrepancies: list[Discrepancy] = []

        # 1. Unmatched / Missing records discrepancies
        if unmatched_records.get("settlements"):
            for stl_id in unmatched_records["settlements"]:
                stl = records_lookup.get(stl_id, {})
                ev_ids = [e.evidence_id for e in evidence_list if e.source_record_id == stl_id]
                
                # Check if it has a broken reference or is orphaned
                payment_ref = stl.get("payment_id", "")
                if payment_ref and payment_ref not in records_lookup:
                    hypo1 = RootCauseHypothesis(
                        cause_type="reference_id_error",
                        title="Invalid or Non-Existent Payment Reference",
                        description=f"Settlement references payment '{payment_ref}' which does not exist in ingested records",
                        supporting_evidence_ids=ev_ids,
                        plausibility_score=0.90,
                        is_primary=True,
                    )
                    hypo2 = RootCauseHypothesis(
                        cause_type="record_missing_from_source",
                        title="Payment Record Missing From Gateway",
                        description="Payment occurred but its record was not delivered or ingested",
                        supporting_evidence_ids=ev_ids,
                        plausibility_score=0.60,
                        is_primary=False,
                    )
                    discrepancies.append(
                        Discrepancy(
                            case_id=case_id,
                            discrepancy_type="broken_reference",
                            title=f"Unmatched Settlement {stl_id} with Invalid Reference",
                            severity=Severity.HIGH,
                            affected_record_ids=[stl_id],
                            evidence_ids=ev_ids,
                            candidate_hypotheses=[hypo1, hypo2],
                        )
                    )
                else:
                    hypo = RootCauseHypothesis(
                        cause_type="record_missing_from_source",
                        title="Orphaned Settlement Record",
                        description="Settlement exists without corresponding captured payment",
                        supporting_evidence_ids=ev_ids,
                        plausibility_score=0.85,
                        is_primary=True,
                    )
                    discrepancies.append(
                        Discrepancy(
                            case_id=case_id,
                            discrepancy_type="missing_record",
                            title=f"Orphaned Settlement {stl_id}",
                            severity=Severity.HIGH,
                            affected_record_ids=[stl_id],
                            evidence_ids=ev_ids,
                            candidate_hypotheses=[hypo],
                        )
                    )

        # Check for duplicate records in observed records
        for r_type, r_list, id_key in [
            (RecordType.PAYMENT, records_lookup.get("_all_payments", []), "payment_id"),
            (RecordType.SETTLEMENT, records_lookup.get("_all_settlements", []), "settlement_id"),
            (RecordType.FEE, records_lookup.get("_all_fees", []), "fee_id"),
        ]:
            ids = [r.get(id_key) for r in r_list if r.get(id_key)]
            if len(ids) > len(set(ids)):
                seen = set()
                duplicates = [pid for pid in ids if pid in seen or seen.add(pid)]
                ev = [e.evidence_id for e in evidence_list if e.source_record_id in duplicates]
                hypo = RootCauseHypothesis(
                    cause_type="duplicate_submission",
                    title=f"Duplicate {r_type.value.capitalize()} Submission or Replay",
                    description=f"Multiple identical {r_type.value} records detected ({duplicates})",
                    supporting_evidence_ids=ev,
                    plausibility_score=0.95,
                    is_primary=True,
                )
                discrepancies.append(
                    Discrepancy(
                        case_id=case_id,
                        discrepancy_type="duplicate_record",
                        title=f"Duplicate {r_type.value.capitalize()} Records Detected",
                        severity=Severity.HIGH,
                        affected_record_ids=duplicates,
                        evidence_ids=ev,
                        candidate_hypotheses=[hypo],
                    )
                )

        # 2. Analyze Rule Results per group
        for group in groups:
            group_ev = [e for e in evidence_list if e.source_record_id in (
                [group.payment_id] + group.settlement_ids + group.fee_ids + group.refund_ids + group.ledger_entry_ids
            )]
            group_ev_ids = [e.evidence_id for e in group_ev]

            # A. Amount Rule
            for res in rule_results:
                if res.rule_id == "RULE-AMT-001" and not res.passed:
                    diff_data = res.difference or {}
                    diff_val = diff_data.get("difference_minor", 0)
                    
                    if not group.settlement_ids:
                        hypo1 = RootCauseHypothesis(
                            cause_type="record_missing_from_source",
                            title="Missing Settlement Record",
                            description="Payment was captured but no settlement record was generated or ingested",
                            supporting_evidence_ids=group_ev_ids,
                            plausibility_score=0.90,
                            is_primary=True,
                        )
                        hypo2 = RootCauseHypothesis(
                            cause_type="settlement_delay",
                            title="Settlement In Transit or Delayed",
                            description="Settlement cycle is still pending or delayed by banking rails",
                            supporting_evidence_ids=group_ev_ids,
                            plausibility_score=0.70,
                            is_primary=False,
                        )
                        discrepancies.append(
                            Discrepancy(
                                case_id=case_id,
                                discrepancy_type="missing_record",
                                title="Missing Settlement for Captured Payment",
                                severity=Severity.HIGH,
                                affected_record_ids=[group.payment_id or ""] if group.payment_id else [],
                                evidence_ids=group_ev_ids,
                                candidate_hypotheses=[hypo1, hypo2],
                            )
                        )
                    elif diff_val != 0:
                        # Check if partial settlement vs calculation error
                        obs_stl = records_lookup.get(group.settlement_ids[0]) if group.settlement_ids else {}
                        gross_amt = obs_stl.get("gross_amount", {}).get("amount_minor", 0) if isinstance(obs_stl.get("gross_amount"), dict) else 0
                        pay_amt = records_lookup.get(group.payment_id or {}, {}).get("amount", {}).get("amount_minor", 0) if group.payment_id else 0

                        is_partial = gross_amt > 0 and pay_amt > 0 and gross_amt < pay_amt

                        if is_partial:
                            hypo_primary = RootCauseHypothesis(
                                cause_type="incomplete_settlement",
                                title="Partial Settlement Without Corresponding Split Record",
                                description=f"Settlement gross ({gross_amt}) is less than payment amount ({pay_amt})",
                                supporting_evidence_ids=group_ev_ids,
                                plausibility_score=0.95,
                                is_primary=True,
                            )
                            discrepancies.append(
                                Discrepancy(
                                    case_id=case_id,
                                    discrepancy_type="partial_settlement",
                                    title=f"Partial Settlement ({gross_amt}/{pay_amt} paise)",
                                    severity=Severity.HIGH,
                                    affected_record_ids=group.settlement_ids,
                                    evidence_ids=group_ev_ids,
                                    candidate_hypotheses=[hypo_primary],
                                )
                            )
                        else:
                            hypo_calc = RootCauseHypothesis(
                                cause_type="incorrect_settlement_calculation",
                                title="Settlement Amount Calculation Error",
                                description=f"Settlement net amount diverges from expected net by {diff_val} paise",
                                supporting_evidence_ids=group_ev_ids,
                                plausibility_score=0.90,
                                is_primary=True,
                            )
                            hypo_fee = RootCauseHypothesis(
                                cause_type="fee_omitted",
                                title="Unrecorded Fee or Holdback",
                                description="Difference may represent an unrecorded intermediary fee or merchant reserve",
                                supporting_evidence_ids=group_ev_ids,
                                plausibility_score=0.65,
                                is_primary=False,
                            )
                            discrepancies.append(
                                Discrepancy(
                                    case_id=case_id,
                                    discrepancy_type="settlement_amount_mismatch",
                                    title=f"Settlement Net Mismatch (Delta: {diff_val} paise)",
                                    severity=Severity.HIGH,
                                    affected_record_ids=group.settlement_ids,
                                    evidence_ids=group_ev_ids,
                                    candidate_hypotheses=[hypo_calc, hypo_fee],
                                )
                            )

                # B. Fee Rule
                elif res.rule_id == "RULE-FEE-001" and not res.passed:
                    hypo_fee = RootCauseHypothesis(
                        cause_type="fee_rate_miscalculation",
                        title="Fee Rate Miscalculation",
                        description="Fee amount does not match stated basis-point rate applied to payment base",
                        supporting_evidence_ids=group_ev_ids,
                        plausibility_score=0.95,
                        is_primary=True,
                    )
                    discrepancies.append(
                        Discrepancy(
                            case_id=case_id,
                            discrepancy_type="fee_calculation_error",
                            title="Fee Rate Calculation Discrepancy",
                            severity=Severity.MEDIUM,
                            affected_record_ids=group.fee_ids,
                            evidence_ids=group_ev_ids,
                            candidate_hypotheses=[hypo_fee],
                        )
                    )

                # C. Temporal Rule
                elif res.rule_id == "RULE-TIME-001" and not res.passed:
                    hypo_time = RootCauseHypothesis(
                        cause_type="settlement_delay",
                        title="Settlement Processing Delay or Out-of-Sequence Posting",
                        description="Event timestamps violate standard lifecycle sequence or settlement delay bounds",
                        supporting_evidence_ids=group_ev_ids,
                        plausibility_score=0.90,
                        is_primary=True,
                    )
                    discrepancies.append(
                        Discrepancy(
                            case_id=case_id,
                            discrepancy_type="settlement_timing_anomaly",
                            title="Temporal Timing Anomaly",
                            severity=Severity.MEDIUM,
                            affected_record_ids=group.settlement_ids,
                            evidence_ids=group_ev_ids,
                            candidate_hypotheses=[hypo_time],
                        )
                    )

                # D. Status Rule
                elif res.rule_id == "RULE-STAT-001" and not res.passed:
                    hypo_stat = RootCauseHypothesis(
                        cause_type="cross_system_sync_failure",
                        title="Cross-System Status Synchronisation Failure",
                        description="Payment and settlement exhibit mutually contradictory status states",
                        supporting_evidence_ids=group_ev_ids,
                        plausibility_score=0.95,
                        is_primary=True,
                    )
                    discrepancies.append(
                        Discrepancy(
                            case_id=case_id,
                            discrepancy_type="status_sync_failure",
                            title="Status Inconsistency Violation",
                            severity=Severity.HIGH,
                            affected_record_ids=[group.payment_id or ""] + group.settlement_ids,
                            evidence_ids=group_ev_ids,
                            candidate_hypotheses=[hypo_stat],
                        )
                    )

        # Remove potential duplicate discrepancy registrations
        deduped: list[Discrepancy] = []
        seen_disc_types = set()
        for d in discrepancies:
            key = f"{d.discrepancy_type}:{sorted(d.affected_record_ids)}"
            if key not in seen_disc_types:
                seen_disc_types.add(key)
                deduped.append(d)

        return deduped
