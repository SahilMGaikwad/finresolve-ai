"""
FinResolve AI — Synthetic Data Generators Package

Provides deterministic, seed-controlled generation of synthetic
financial reconciliation datasets with labeled ground truth.
"""

from data.generators.config import GeneratorConfig


def generate_dataset(*args, **kwargs):
    """Generate dataset delegating to data.generators.generate."""
    from data.generators.generate import generate_dataset as _generate
    return _generate(*args, **kwargs)


__all__ = ["GeneratorConfig", "generate_dataset"]

