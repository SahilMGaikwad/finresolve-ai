"""
FinResolve AI — AI Financial Investigator CLI Benchmark Runner

Evaluates evidence grounding, unsupported claim rate, multi-step plan feasibility, and safety across datasets.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from data.generators.config import GeneratorConfig
from data.generators.generate import generate_dataset
from services.investigator.evaluation.evaluator import InvestigatorBenchmarkEvaluator
from services.investigator.evaluation.metrics import InvestigatorEvaluationSummary
from services.policy_engine.engine import DeterministicPolicyEngine


def run_investigator_evaluation(
    num_cases: int = 100,
    seed: int = 42,
    auto_resolve_enabled: bool = False,
) -> InvestigatorEvaluationSummary:
    """Generate dataset and execute AI Investigator benchmark evaluation."""
    config = GeneratorConfig(seed=seed, num_cases=num_cases, corruption_rate=0.15)
    cases, _ = generate_dataset(config)

    policy_engine = DeterministicPolicyEngine(auto_resolve_enabled=auto_resolve_enabled)
    evaluator = InvestigatorBenchmarkEvaluator(policy_engine=policy_engine)

    return evaluator.evaluate_cases(cases)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate AI Financial Investigator performance.")
    parser.add_argument("--cases", type=int, default=100, help="Number of synthetic cases to evaluate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--auto-resolve", action="store_true", help="Enable auto-resolve switch (default false)")
    args = parser.parse_args()

    summary = run_investigator_evaluation(
        num_cases=args.cases,
        seed=args.seed,
        auto_resolve_enabled=args.auto_resolve,
    )
    print(summary.format_report())


if __name__ == "__main__":
    main()
