"""
FinResolve AI — Reconciliation Evaluation Metrics

Evaluates ReconciliationResult objects against ground truth (strictly post-inference).
Calculates actual precision, recall, classification accuracy, and false positive/negative counts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from data.schemas.case import ReconciliationCase
from data.schemas.reconciliation_result import (
    ReconciliationResult,
    ReconciliationStatus,
)


@dataclass
class EvaluationReport:
    """
    Comprehensive evaluation metrics calculated across a benchmark dataset.
    """

    total_cases: int = 0
    clean_cases: int = 0
    corrupted_cases: int = 0

    # Discrepancy Detection Performance
    true_positives: int = 0     # Correctly identified discrepancy
    false_positives: int = 0    # Clean case flagged as discrepancy
    true_negatives: int = 0     # Correctly identified clean case
    false_negatives: int = 0    # Corrupted case missed (flagged clean)

    # Classification & Exact Match
    correct_classifications: int = 0   # Discrepancy type matched ground truth exactly
    exact_case_matches: int = 0        # Entire case outcome perfectly aligned with ground truth
    ambiguous_count: int = 0           # Flagged as ambiguous / insufficient evidence
    unresolved_count: int = 0          # Flagged as unresolved

    # Matching Quality
    matching_tp: int = 0
    matching_fp: int = 0
    matching_fn: int = 0

    # Measured Performance
    total_execution_time_ms: float = 0.0

    @property
    def discrepancy_precision(self) -> float:
        denom = self.true_positives + self.false_positives
        return round(self.true_positives / denom, 4) if denom > 0 else 1.0

    @property
    def discrepancy_recall(self) -> float:
        denom = self.true_positives + self.false_negatives
        return round(self.true_positives / denom, 4) if denom > 0 else 1.0

    @property
    def discrepancy_f1(self) -> float:
        p = self.discrepancy_precision
        r = self.discrepancy_recall
        return round(2 * (p * r) / (p + r), 4) if (p + r) > 0 else 0.0

    @property
    def classification_accuracy(self) -> float:
        denom = self.true_positives
        return round(self.correct_classifications / denom, 4) if denom > 0 else 1.0

    @property
    def exact_case_accuracy(self) -> float:
        return round(self.exact_case_matches / self.total_cases, 4) if self.total_cases > 0 else 0.0

    @property
    def matching_precision(self) -> float:
        denom = self.matching_tp + self.matching_fp
        return round(self.matching_tp / denom, 4) if denom > 0 else 1.0

    @property
    def matching_recall(self) -> float:
        denom = self.matching_tp + self.matching_fn
        return round(self.matching_tp / denom, 4) if denom > 0 else 1.0

    @property
    def mean_latency_ms(self) -> float:
        return round(self.total_execution_time_ms / self.total_cases, 2) if self.total_cases > 0 else 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert report to serializable dictionary."""
        return {
            "total_cases": self.total_cases,
            "clean_cases": self.clean_cases,
            "corrupted_cases": self.corrupted_cases,
            "discrepancy_detection": {
                "precision": self.discrepancy_precision,
                "recall": self.discrepancy_recall,
                "f1_score": self.discrepancy_f1,
                "true_positives": self.true_positives,
                "false_positives": self.false_positives,
                "true_negatives": self.true_negatives,
                "false_negatives": self.false_negatives,
            },
            "matching": {
                "precision": self.matching_precision,
                "recall": self.matching_recall,
            },
            "classification_accuracy": self.classification_accuracy,
            "exact_case_accuracy": self.exact_case_accuracy,
            "ambiguous_cases": self.ambiguous_count,
            "unresolved_cases": self.unresolved_count,
            "mean_latency_ms": self.mean_latency_ms,
        }


class BenchmarkEvaluator:
    """
    Compares ReconciliationResults against ground-truth annotations in ReconciliationCase.
    """

    def evaluate_case(
        self,
        case: ReconciliationCase,
        result: ReconciliationResult,
        report: EvaluationReport,
    ) -> None:
        """
        Evaluate a single case result against its ground truth.
        """
        report.total_cases += 1
        gt_has_discrepancy = case.expected_outcome.has_discrepancy
        gt_discrepancy_type = case.expected_outcome.discrepancy_type

        if gt_has_discrepancy:
            report.corrupted_cases += 1
        else:
            report.clean_cases += 1

        engine_detected = len(result.discrepancies) > 0 or result.status in (
            ReconciliationStatus.DISCREPANCY,
            ReconciliationStatus.UNRESOLVED,
            ReconciliationStatus.INSUFFICIENT_EVIDENCE,
        )

        # 1. Detection Confusion Matrix
        if engine_detected and gt_has_discrepancy:
            report.true_positives += 1
        elif engine_detected and not gt_has_discrepancy:
            report.false_positives += 1
        elif not engine_detected and not gt_has_discrepancy:
            report.true_negatives += 1
        elif not engine_detected and gt_has_discrepancy:
            report.false_negatives += 1

        # 2. Ambiguity tracking
        if result.status == ReconciliationStatus.INSUFFICIENT_EVIDENCE:
            report.ambiguous_count += 1
        elif result.status == ReconciliationStatus.UNRESOLVED:
            report.unresolved_count += 1

        # 3. Discrepancy Type Classification
        if engine_detected and gt_has_discrepancy and result.discrepancies:
            detected_types = {d.discrepancy_type for d in result.discrepancies}
            if gt_discrepancy_type in detected_types or (
                gt_discrepancy_type == "compound_discrepancy" and len(detected_types) > 1
            ):
                report.correct_classifications += 1

        # 4. Exact Case Level Match
        exact_match = (
            (not gt_has_discrepancy and result.status == ReconciliationStatus.RECONCILED)
            or (gt_has_discrepancy and result.status in (ReconciliationStatus.DISCREPANCY, ReconciliationStatus.UNRESOLVED))
        )
        if exact_match:
            report.exact_case_matches += 1

        # 5. Matching Record Evaluation
        total_observed_count = (
            len(case.observed.orders)
            + len(case.observed.settlements)
            + len(case.observed.fees)
            + len(case.observed.refunds)
            + len(case.observed.ledger_entries)
        )
        total_unmatched_count = sum(len(v) for v in result.unmatched_records.values())

        if not gt_has_discrepancy:
            # In clean cases, all observed records should be matched
            matched_count = total_observed_count - total_unmatched_count
            report.matching_tp += max(0, matched_count)
            report.matching_fn += total_unmatched_count
        else:
            # In corrupted cases, count matched components
            for group in result.matched_groups:
                if group.order_id:
                    report.matching_tp += 1
                if group.settlement_ids:
                    report.matching_tp += len(group.settlement_ids)
                if group.fee_ids:
                    report.matching_tp += len(group.fee_ids)
