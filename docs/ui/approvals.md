# Human Approval Queue & Governance Specification

## 1. Overview
The **Human Approval Queue** (`apps/web/app/approvals/page.tsx` and `ApprovalDrawer.tsx`) provides an authorization portal for high-value and high-risk resolution proposals.

## 2. Separation of Duties Invariant
- **Rule**: An analyst who triggers or proposes a resolution is strictly prohibited from signing or authorizing that proposal.
- **Role Permissions**: Authorizing a resolution requires `APPROVER` or `ADMIN` role.
- **Audit Logging**: Every sign-off or rejection decision is cryptographically chained and recorded with approver notes.
