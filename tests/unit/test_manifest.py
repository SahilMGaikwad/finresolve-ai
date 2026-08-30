"""
FinResolve AI — Manifest Tests

Verifies that the manifest contains all required fields and
checksums are correct.
"""

import json
from pathlib import Path

import pytest

from data.generators.config import GeneratorConfig
from data.generators.generate import generate_dataset


class TestManifest:
    """Manifest integrity tests."""

    @pytest.fixture
    def generated_dataset(self, tmp_path):
        config = GeneratorConfig(
            seed=42,
            num_cases=10,
            corruption_rate=0.3,
            output_dir=str(tmp_path / "test_output"),
        )
        cases, summary = generate_dataset(config)
        manifest_path = config.output_path / "manifest.json"
        with open(manifest_path) as f:
            manifest = json.load(f)
        return cases, manifest, config

    def test_manifest_has_required_fields(self, generated_dataset):
        _, manifest, _ = generated_dataset
        required = {
            "dataset_version", "generator_version", "seed",
            "configuration", "configuration_hash", "schema_version",
            "record_counts", "case_count", "corruption_counts",
            "corrupted_case_count", "clean_case_count",
            "file_checksums", "generated_at",
        }
        assert required.issubset(manifest.keys()), \
            f"Missing fields: {required - manifest.keys()}"

    def test_manifest_seed_matches(self, generated_dataset):
        _, manifest, config = generated_dataset
        assert manifest["seed"] == config.seed

    def test_manifest_case_count_matches(self, generated_dataset):
        cases, manifest, _ = generated_dataset
        assert manifest["case_count"] == len(cases)

    def test_manifest_record_counts_non_negative(self, generated_dataset):
        _, manifest, _ = generated_dataset
        for record_type, count in manifest["record_counts"].items():
            assert count >= 0, f"Negative count for {record_type}"

    def test_manifest_corruption_counts_sum(self, generated_dataset):
        cases, manifest, _ = generated_dataset
        expected_corrupted = sum(1 for c in cases if c.corruptions)
        assert manifest["corrupted_case_count"] == expected_corrupted
        assert manifest["clean_case_count"] == len(cases) - expected_corrupted

    def test_manifest_checksums_exist(self, generated_dataset):
        _, manifest, _ = generated_dataset
        assert "cases.json" in manifest["file_checksums"]
        checksum = manifest["file_checksums"]["cases.json"]
        assert len(checksum) == 64  # SHA-256 hex

    def test_manifest_checksum_matches_file(self, generated_dataset):
        """Verify that the checksum in the manifest matches the actual file."""
        import hashlib
        _, manifest, config = generated_dataset
        cases_file = config.output_path / "cases.json"
        sha256 = hashlib.sha256()
        with open(cases_file, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        actual_checksum = sha256.hexdigest()
        assert manifest["file_checksums"]["cases.json"] == actual_checksum

    def test_manifest_configuration_hash_deterministic(self, generated_dataset):
        _, manifest, config = generated_dataset
        assert manifest["configuration_hash"] == config.configuration_hash()
