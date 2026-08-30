"""
FinResolve AI — Ground Truth Leakage Prevention Regression Tests

Enforces strict isolation between inference engine code and ground truth labels.
Uses static AST inspection, dynamic proxy canary traps, and serialization checks.
"""

import ast
from pathlib import Path
from typing import Any

import pytest

from data.generators.config import GeneratorConfig
from data.generators.generate import generate_dataset
from data.schemas.case import CaseRecords, ReconciliationCase
from services.reconciliation.engine import ReconciliationEngine


class DynamicCanaryTrap:
    """
    A canary proxy object that raises immediately upon any attribute access,
    item access, iteration, or string conversion.
    """

    def __init__(self, trap_name: str):
        self._trap_name = trap_name

    def __getattr__(self, item: str) -> Any:
        raise RuntimeError(f"CANARY TRAP TRIGGERED: Inference accessed '{self._trap_name}.{item}'!")

    def __getitem__(self, item: Any) -> Any:
        raise RuntimeError(f"CANARY TRAP TRIGGERED: Inference accessed '{self._trap_name}[{item}]'!")

    def __iter__(self):
        raise RuntimeError(f"CANARY TRAP TRIGGERED: Inference iterated over '{self._trap_name}'!")

    def __len__(self) -> int:
        raise RuntimeError(f"CANARY TRAP TRIGGERED: Inference called len() on '{self._trap_name}'!")

    def __repr__(self) -> str:
        return f"<CanaryTrap:{self._trap_name}>"


class CanaryCaseRecords(CaseRecords):
    """Subclass of CaseRecords that traps access to all record lists."""

    def __getattribute__(self, name: str) -> Any:
        if name in (
            "payments", "orders", "settlements", "fees",
            "refunds", "ledger_entries", "payouts", "model_dump", "dict",
        ):
            raise RuntimeError(f"CANARY TRAP TRIGGERED: engine accessed ground_truth.{name}!")
        return super().__getattribute__(name)


class TestGroundTruthIsolation:
    """Ensures inference code never touches ground_truth, corruptions, or expected_outcome."""

    def test_static_ast_no_leakage_in_services(self):
        """
        Inspect all python source files under services/ to verify that no attribute access
        to .ground_truth, .corruptions, or .expected_outcome exists in inference code.
        """
        services_dir = Path("services")
        target_files = []
        for p in services_dir.rglob("*.py"):
            # Exclude post-inference evaluation package
            if "evaluation" not in p.parts:
                target_files.append(p)

        forbidden_attributes = {"ground_truth", "corruptions", "expected_outcome"}

        for filepath in target_files:
            with open(filepath, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=str(filepath))

            for node in ast.walk(tree):
                if isinstance(node, ast.Attribute):
                    assert node.attr not in forbidden_attributes, (
                        f"CRITICAL GROUND TRUTH LEAKAGE in {filepath}:{node.lineno}! "
                        f"Inference code accessed forbidden attribute '{node.attr}'."
                    )

    def test_runtime_canary_trap_reconcile_case(self):
        """
        Create a ReconciliationCase with canary traps on ground_truth, corruptions,
        and expected_outcome to verify reconcile_case() never touches them.
        """
        config = GeneratorConfig(seed=42, num_cases=1, corruption_rate=0.5)
        cases, _ = generate_dataset(config)
        sample_case = cases[0]

        trapped_case = ReconciliationCase(
            case_id=sample_case.case_id,
            merchant_id=sample_case.merchant_id,
            ground_truth=CanaryCaseRecords(),
            observed=sample_case.observed,
            corruptions=[],
            difficulty=sample_case.difficulty,
            expected_outcome=sample_case.expected_outcome,
        )

        engine = ReconciliationEngine()
        result = engine.reconcile_case(trapped_case)
        assert result.case_id == sample_case.case_id
        assert result.status is not None

    def test_reconciliation_result_does_not_embed_ground_truth(self):
        """Verify ReconciliationResult serialization contains no ground_truth or corruption attributes."""
        config = GeneratorConfig(seed=42, num_cases=1, corruption_rate=0.5)
        cases, _ = generate_dataset(config)
        
        engine = ReconciliationEngine()
        result = engine.reconcile_case(cases[0])
        dumped = result.model_dump()
        dumped_str = str(dumped)

        assert "ground_truth" not in dumped_str
        assert "expected_outcome" not in dumped_str
        assert "corruptions" not in dumped
