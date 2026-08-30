# Live Demo Walkthrough Script — FinResolve AI

## Prerequisites
```bash
# Terminal 1: Backend
source .venv/bin/activate
uvicorn apps.api.main:app --host 127.0.0.1 --port 8000

# Terminal 2: Frontend
cd apps/web
npm run dev
# Browser: http://localhost:3000
```

---

## 5-Minute Live Flow
1. **Executive Dashboard (`/`)**: Click **`[ ⚡ Load 50-Case FinOps Benchmark ]`** to seed live cases.
2. **Case Explorer (`/cases`)**: Filter by **"Flagged Discrepancies"** and open `CASE-000003` (Single Mismatch) or `CASE-000009` (Compound).
3. **Case Detail Workspace (`/cases/[id]`)**:
   - Inspect the **Discrepancy Alert Banner** and **Financial Records** (Payments, Settlements, Fees, Ledger).
   - Switch to **"🕸️ Evidence Graph"** to inspect node connectivity and conflicting edges.
   - Click **`[ ⚡ Run AI Investigation ]`** to watch real-time tool traces and verified claims.
   - Switch to **"🔮 Resolution Simulator"** to see the zero-sum ledger delta ($\Delta = 0.00\text{ paise}$).
   - Sign off the resolution in the **Approval Drawer** (enforcing separation of duties).
4. **Audit Timeline (`/audit`)**: Inspect the newly chained SHA-256 block with verified tamper-free status.
