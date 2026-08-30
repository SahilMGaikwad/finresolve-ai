"""
FinResolve AI — Dataset Generator CLI

Main entry point for synthetic dataset generation.

Usage:
    python -m data.generators.generate --seed 42 --cases 1000 --corruption-rate 0.08
    python -m data.generators.generate --seed 42 --cases 100 --difficulty easy
    python -m data.generators.generate --help
"""

from __future__ import annotations

import argparse
import json
import logging
import random
import sys
import time
from pathlib import Path

from data.generators.cases import generate_case
from data.generators.config import GeneratorConfig
from data.generators.manifest import build_manifest
from data.generators.merchants import generate_merchants
from data.schemas.case import ReconciliationCase

logger = logging.getLogger("finresolve.generator")


def _setup_logging(level: str = "INFO") -> None:
    """Configure logging for the generator."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        stream=sys.stdout,
    )


def _write_cases(cases: list[ReconciliationCase], output_dir: Path) -> dict[str, Path]:
    """
    Write generated cases to disk as JSON.

    Returns a dict mapping filenames to their paths.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Serialise all cases
    cases_data = [case.model_dump(mode="json") for case in cases]

    cases_file = output_dir / "cases.json"
    with open(cases_file, "w", encoding="utf-8") as f:
        json.dump(cases_data, f, indent=2, default=str)

    output_files = {"cases.json": cases_file}

    return output_files


def generate_dataset(config: GeneratorConfig) -> tuple[list[ReconciliationCase], dict]:
    """
    Generate a full synthetic dataset.

    Args:
        config: Generator configuration.

    Returns:
        Tuple of (cases, summary_dict).
    """
    rng = random.Random(config.seed)

    logger.info(f"Generating dataset: seed={config.seed}, cases={config.num_cases}, "
                f"corruption_rate={config.corruption_rate}, difficulty={config.difficulty}")

    # Step 1: Generate merchants
    merchants = generate_merchants(config, rng)
    logger.info(f"Generated {len(merchants)} merchant profiles")

    # Step 2: Generate cases
    cases: list[ReconciliationCase] = []
    for i in range(config.num_cases):
        merchant = merchants[i % len(merchants)]
        case = generate_case(i, merchant, config, rng)
        cases.append(case)

        if (i + 1) % 500 == 0:
            logger.info(f"  Generated {i + 1}/{config.num_cases} cases")

    logger.info(f"Generated {len(cases)} cases")

    # Step 3: Write to disk
    output_dir = config.output_path
    output_files = _write_cases(cases, output_dir)
    logger.info(f"Wrote cases to {output_dir}")

    # Step 4: Build manifest
    manifest = build_manifest(cases, config, output_files)

    # Write manifest
    manifest_file = output_dir / "manifest.json"
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest.model_dump(mode="json"), f, indent=2, default=str)
    output_files["manifest.json"] = manifest_file

    logger.info(f"Wrote manifest to {manifest_file}")

    # Build summary
    summary = {
        "seed": config.seed,
        "output_dir": str(output_dir),
        "case_count": manifest.case_count,
        "record_counts": manifest.record_counts,
        "corrupted_cases": manifest.corrupted_case_count,
        "clean_cases": manifest.clean_case_count,
        "corruption_counts": manifest.corruption_counts,
        "dataset_version": manifest.dataset_version,
        "configuration_hash": manifest.configuration_hash,
    }

    return cases, summary


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="FinResolve AI — Synthetic Dataset Generator",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--cases", type=int, default=1000, help="Number of reconciliation cases")
    parser.add_argument("--corruption-rate", type=float, default=0.08,
                        help="Fraction of cases with corruption (0.0–1.0)")
    parser.add_argument("--difficulty", type=str, default="mixed",
                        choices=["easy", "medium", "hard", "mixed"],
                        help="Case difficulty level")
    parser.add_argument("--merchants", type=int, default=10, help="Number of synthetic merchants")
    parser.add_argument("--output", type=str, default="data/generated",
                        help="Output directory (seed subdirectory created automatically)")
    parser.add_argument("--log-level", type=str, default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                        help="Logging level")

    args = parser.parse_args()

    _setup_logging(args.log_level)

    config = GeneratorConfig(
        seed=args.seed,
        num_cases=args.cases,
        corruption_rate=args.corruption_rate,
        difficulty=args.difficulty,
        merchant_count=args.merchants,
        output_dir=args.output,
    )

    start_time = time.monotonic()
    _cases, summary = generate_dataset(config)
    elapsed = time.monotonic() - start_time

    # Output summary
    print("\n" + "=" * 60)
    print("  FinResolve AI — Dataset Generation Complete")
    print("=" * 60)
    print(f"  Seed:               {summary['seed']}")
    print(f"  Output:             {summary['output_dir']}")
    print(f"  Cases:              {summary['case_count']}")
    print(f"  Corrupted cases:    {summary['corrupted_cases']}")
    print(f"  Clean cases:        {summary['clean_cases']}")
    print(f"  Dataset version:    {summary['dataset_version']}")
    print(f"  Config hash:        {summary['configuration_hash'][:16]}...")
    print(f"  Generation time:    {elapsed:.2f}s")
    print()
    print("  Record counts:")
    for record_type, count in sorted(summary["record_counts"].items()):
        print(f"    {record_type:20s} {count:>6}")
    print()
    print("  Corruption counts:")
    for corruption_type, count in sorted(summary["corruption_counts"].items()):
        if count > 0:
            print(f"    {corruption_type:30s} {count:>4}")
    print("=" * 60)


if __name__ == "__main__":
    main()
