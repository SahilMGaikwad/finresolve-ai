# Security & Hardening Architecture — FinResolve AI

## 1. Zero-Harm Financial Safety Invariant
FinResolve AI is built so that **no invalid, contradictory, or imbalanced action can ever be authorized**. Every proposed adjustment must mathematically prove double-entry conservation ($\Delta = 0.00\text{ paise}$).

---

## 2. Security Controls & Defense in Depth
- **Authentication & RBAC**: Role-based access control (`VIEWER`, `ANALYST`, `APPROVER`, `ADMIN`) with granular permissions.
- **Separation of Duties**: Proposers cannot approve their own resolution plans; sign-offs strictly require `APPROVER` or `ADMIN` roles.
- **Prompt Injection Defense**: Untrusted transaction memos quarantined inside `<untrusted_data>` enclosures and parsed strictly as data.
- **Ground-Truth Isolation**: Static AST inspection and runtime canary traps guarantee inference code never accesses evaluation ground-truth.
- **Rate Limiting & Correlation**: Token bucket rate limiting and UUID request ID correlation.
- **Secret Scanning**: Automated scanner confirms 0 exposed credentials in codebase and git history.
- **Sanitized Errors**: Global error handlers prevent stack trace or internal path leakage.
