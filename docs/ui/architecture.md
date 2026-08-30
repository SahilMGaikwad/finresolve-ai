# FinResolve Analyst Command Center — Frontend Architecture

## 1. Overview & Philosophy
The **FinResolve Analyst Command Center** (`apps/web/`) is an enterprise-grade financial operations dashboard and investigation console built with Next.js 14+ (App Router), React, and strict TypeScript.

It is purpose-built for financial operations controllers, risk analysts, and authorized approvers. It is strictly designed as an **operations command console, not an AI chatbot**.

---

## 2. Technology Stack & Design System
- **Framework**: Next.js 14+ with React Server Components & Client Components.
- **Styling**: Vanilla CSS Modules and Tokens (`apps/web/styles/tokens.css` and `globals.css`).
  - Dark Theme: Deep Slate palette (`#080c14`, `#0e1626`, `#131d31`).
  - Status Accents: Reconciled (`#10b981`), Discrepancy (`#ef4444`), Review (`#f59e0b`), Info (`#6366f1`).
  - Typography: `Inter` for interface typography and `JetBrains Mono` for currency and record identifiers.
- **Visualizations**: Lightweight SVG canvas for Evidence Graph with accessibility HTML table fallback.

---

## 3. Screen Structure
1. **Executive Dashboard (`/`)**: High-level FinOps KPIs, fleet reconciliation rates, discrepancy counts, and quick case ingestion loader.
2. **Case Explorer (`/cases`)**: Filterable, searchable data grid of canonical financial cases with difficulty badges and discrepancy counters.
3. **Case Detail Workspace (`/cases/[id]`)**: Comprehensive multi-tab inspector (Payments, Settlements, Fees, Refunds, Ledger), interactive evidence graph, AI investigation console, and counterfactual simulation viewer.
4. **Human Approval Queue (`/approvals`)**: Gated proposal sign-off enforcing Role-Based Access Control and separation of duties.
5. **Cryptographic Audit Timeline (`/audit`)**: Immutable SHA-256 event chaining visualizer.
6. **System Health & Observability (`/health`)**: Live telemetry from `/health`, `/ready`, and `/metrics`.
