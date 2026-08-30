"""
FinResolve AI — Ingestion Service

Responsible for:
- Accepting raw financial records (payments, orders, settlements, refunds, etc.)
- Validating record structure and required fields
- Rejecting malformed or suspicious records
- Assigning ingestion metadata (timestamps, source identifiers, ingestion IDs)
- Forwarding validated records to the normalization service

Status: NOT IMPLEMENTED (Phase 2+)
"""

# TODO(phase-2): Implement record ingestion pipeline
# TODO(phase-2): Add input validation with Pydantic schemas
# TODO(phase-2): Add structured logging for ingestion events
# TODO(phase-2): Add malformed-record rejection and quarantine
