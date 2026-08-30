# Cryptographic Audit Timeline Specification

## 1. Overview
The **Audit Timeline Explorer** (`apps/web/app/audit/page.tsx` and `AuditTimeline.tsx`) visualizes the immutable SHA-256 event blockchain maintained by `services/audit/logger.py`.

## 2. Integrity Verification
- Each audit card displays the `event_id`, timestamp, actor, role, operation (`PROPOSAL_SUBMITTED_FOR_REVIEW`, `SIMULATION_COMPLETED`, `POLICY_EVALUATED`), operation result (`SUCCESS`, `FAILURE`, `REJECTED`), and SHA-256 hash.
- A live chain integrity badge (`[ ✓ SHA-256 CHAIN VERIFIED ]`) verifies non-repudiation and detects tampering.
