"""
FinResolve AI — Evidence Service

Structured evidence collection and evidence graph generation.
"""

from services.evidence.collector import EvidenceCollector
from services.evidence.graph import EvidenceGraphBuilder

__all__ = [
    "EvidenceCollector",
    "EvidenceGraphBuilder",
]
