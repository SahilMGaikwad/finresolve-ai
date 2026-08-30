"""
FinResolve AI — Normalization Service

Converts validated source records into canonical internal form.

Components:
- normalizer: Record normalization (amounts, timestamps, field mapping)
- field_mappings: Source-system-specific field name mappings
"""

from services.normalization.field_mappings import (
    apply_field_mapping,
    get_field_mapping,
)
from services.normalization.normalizer import normalize_record

__all__ = [
    "apply_field_mapping",
    "get_field_mapping",
    "normalize_record",
]
