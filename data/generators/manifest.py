"""
FinResolve AI — Dataset Manifest Generator

Computes checksums and metadata for a generated dataset.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from data.generators.config import GeneratorConfig
from data.schemas.case import ReconciliationCase
from data.schemas.enums import CorruptionType
from data.schemas.manifest import DatasetManifest


def _compute_file_checksum(filepath: Path) -> str:
    """Compute SHA-256 checksum of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def _count_records(cases: list[ReconciliationCase]) -> dict[str, int]:
    """Count observed records by type across all cases."""
    counts: dict[str, int] = {
        "payments": 0,
        "orders": 0,
        "settlements": 0,
        "refunds": 0,
        "fees": 0,
        "ledger_entries": 0,
        "payouts": 0,
    }
    for case in cases:
        counts["payments"] += len(case.observed.payments)
        counts["orders"] += len(case.observed.orders)
        counts["settlements"] += len(case.observed.settlements)
        counts["refunds"] += len(case.observed.refunds)
        counts["fees"] += len(case.observed.fees)
        counts["ledger_entries"] += len(case.observed.ledger_entries)
        counts["payouts"] += len(case.observed.payouts)
    return counts


def _count_corruptions(cases: list[ReconciliationCase]) -> dict[str, int]:
    """Count corruptions by type across all cases."""
    counts: dict[str, int] = {ct.value: 0 for ct in CorruptionType}
    for case in cases:
        for corruption in case.corruptions:
            counts[corruption.corruption_type.value] += 1
    return counts


def build_manifest(
    cases: list[ReconciliationCase],
    config: GeneratorConfig,
    output_files: dict[str, Path],
) -> DatasetManifest:
    """
    Build a dataset manifest with checksums and statistics.

    Args:
        cases: The generated reconciliation cases.
        config: Generator configuration used.
        output_files: Mapping of file names to their paths.

    Returns:
        A DatasetManifest instance.
    """
    file_checksums = {}
    for name, filepath in output_files.items():
        if filepath.exists():
            file_checksums[name] = _compute_file_checksum(filepath)

    corruption_counts = _count_corruptions(cases)
    corrupted_count = sum(1 for c in cases if c.corruptions)
    clean_count = len(cases) - corrupted_count

    return DatasetManifest(
        dataset_version=config.dataset_version,
        generator_version=config.generator_version,
        seed=config.seed,
        configuration=config.to_dict(),
        configuration_hash=config.configuration_hash(),
        schema_version=config.schema_version,
        record_counts=_count_records(cases),
        case_count=len(cases),
        corruption_counts=corruption_counts,
        corrupted_case_count=corrupted_count,
        clean_case_count=clean_count,
        file_checksums=file_checksums,
        generated_at=datetime.now(timezone.utc),
    )
