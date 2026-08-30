"""
FinResolve AI — Dataset Manifest Schema

Captures full metadata about a generated dataset for reproducibility
and integrity verification.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class DatasetManifest(BaseModel):
    """
    Manifest for a generated synthetic dataset.

    Contains all information needed to reproduce the dataset
    and verify its integrity.
    """

    dataset_version: str = Field(
        default="1.0.0",
        description="Semantic version of the dataset format",
    )
    generator_version: str = Field(
        default="1.0.0",
        description="Version of the generator code that produced this dataset",
    )
    seed: int = Field(description="Random seed used for generation")
    configuration: dict[str, Any] = Field(
        description="Full generator configuration used"
    )
    configuration_hash: str = Field(
        description="SHA-256 hash of the serialised configuration for quick comparison"
    )
    schema_version: str = Field(
        default="1.0.0",
        description="Version of the data schemas used",
    )
    record_counts: dict[str, int] = Field(
        description="Count of records per type (e.g., {'payments': 1000, 'settlements': 980})"
    )
    case_count: int = Field(description="Total number of reconciliation cases")
    corruption_counts: dict[str, int] = Field(
        description="Count of corruptions per type"
    )
    corrupted_case_count: int = Field(
        description="Number of cases that have at least one corruption"
    )
    clean_case_count: int = Field(
        description="Number of cases with no corruptions"
    )
    file_checksums: dict[str, str] = Field(
        description="SHA-256 checksums of all output files for integrity verification"
    )
    generated_at: datetime = Field(description="When the dataset was generated (UTC)")

    model_config = {"from_attributes": True}
