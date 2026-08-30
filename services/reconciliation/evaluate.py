"""
FinResolve AI — Deterministic Reconciliation Evaluation CLI

Runs deterministic reconciliation across a synthetic benchmark dataset,
evaluates results against ground truth, and outputs true performance metrics.

Usage:
    python -m services.reconciliation.evaluate --cases 100 --seed 42
    python -m services.reconciliation.evaluate --cases 500 --difficulty mixed
"""

from __future__ import annotations

import argparse
import logging
import sys
import time

from data.generators.config import GeneratorConfig
from data.generators.generate import generate_dataset
from services.reconciliation.engine import ReconciliationEngine
from services.reconciliation.evaluation.metrics import (
    BenchmarkEvaluator,
    EvaluationReport,
)

logger = logging.getLogger("finresolve.reconciliation.evaluator")


def run_benchmark(config: GeneratorConfig) -> EvaluationReport:
    """
    Generate dataset and run post-inference evaluation.
    """
    cases, summary = generate_dataset(config)
    engine = ReconciliationEngine()
    evaluator = BenchmarkEvaluator()
    report = EvaluationReport()

    start_time = time.monotonic()
    for case in cases:
        case_start = time.monotonic()
        
        # INFERENCE (Strictly receives observed records, 0 ground truth)
        result = engine.reconcile_case(case)
        
        case_elapsed = (time.monotonic() - case_start) * 1000.0
        report.total_execution_time_ms += case_elapsed

        # EVALUATION (Post-inference verification against ground truth)
        evaluator.evaluate_case(case, result, report)

    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="FinResolve AI — Deterministic Reconciliation Benchmark Evaluator",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--cases", type=int, default=100, help="Number of benchmark cases")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--corruption-rate", type=float, default=0.15, help="Corruption rate")
    parser.add_argument("--difficulty", type=str, default="mixed", choices=["easy", "medium", "hard", "mixed"])
    parser.add_argument("--log-level", type=str, default="WARNING", choices=["DEBUG", "INFO", "WARNING", "ERROR"])

    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper()))

    config = GeneratorConfig(
        seed=args.seed,
        num_cases=args.cases,
        corruption_rate=args.corruption_rate,
        difficulty=args.difficulty,
    )

    report = run_benchmark(config)

    print("\n" + "=" * 65)
    print("  FinResolve AI — Deterministic Reconciliation Evaluation")
    print("=" * 65)
    print(f"  Total Cases Evaluated:       {report.total_cases}")
    print(f"  Clean Cases:                 {report.clean_cases}")
    print(f"  Corrupted Cases:             {report.corrupted_cases}")
    print(f"  Mean Latency per Case:       {report.mean_latency_ms:.2f} ms")
    print("-" * 65)
    print("  Discrepancy Detection Performance:")
    print(f"    Precision:                 {report.discrepancy_precision * 100:.2f}% ({report.true_positives}/{report.true_positives + report.false_positives})")
    print(f"    Recall:                    {report.discrepancy_recall * 100:.2f}% ({report.true_positives}/{report.true_positives + report.false_negatives})")
    print(f"    F1 Score:                  {report.discrepancy_f1 * 100:.2f}%")
    print(f"    True Positives:            {report.true_positives}")
    print(f"    False Positives:           {report.false_positives}")
    print(f"    True Negatives:            {report.true_negatives}")
    print(f"    False Negatives:           {report.false_negatives}")
    print("-" * 65)
    print("  Root-Cause Classification & Case Correctness:")
    print(f"    Classification Accuracy:   {report.classification_accuracy * 100:.2f}%")
    print(f"    Exact Case Accuracy:       {report.exact_case_accuracy * 100:.2f}%")
    print(f"    Ambiguous / Low-Evidence:  {report.ambiguous_count}")
    print(f"    Unresolved Cases:          {report.unresolved_count}")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
