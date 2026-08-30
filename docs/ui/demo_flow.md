# Five-Minute Evaluator Demo Guide

This guide walks an evaluator, recruiter, or lead engineer through the FinResolve AI Command Center in under five minutes.

---

### Step 1: Launch & Ingest Live Benchmark (`/`)
1. Open the Executive Dashboard at `http://localhost:3000/`.
2. Click **`[ Load 50-Case FinOps Benchmark ]`** in the top right header.
3. Observe the KPI cards update: 50 active cases, ~85% reconciliation rate, ~8 flagged discrepancies, and 100% zero-harm safety.

---

### Step 2: Explore Ingested Cases (`/cases`)
1. Navigate to **Case Explorer** via the left sidebar.
2. Click the **"Flagged Discrepancies"** filter tab to isolate cases with reconciliation failures.
3. Select any case with discrepancies (e.g. `CASE-000010`) and click **"Inspect Workspace →"**.

---

### Step 3: Inspect Records & Discrepancies (`/cases/[id]`)
1. In the **Case Detail Workspace**, notice the crimson alert banner detailing the exact mathematical discrepancy (e.g. *"Settlement amount is short by ₹11,675.69"*).
2. Switch across the record tabs (**Payments**, **Settlements**, **Fees**, **Refunds**, **Double-Entry Ledger**) to see canonical records formatted with exact paise-to-INR precision.

---

### Step 4: Explore the Evidence Graph
1. Click the **"🕸️ Evidence Graph"** tab.
2. Observe the interactive node-link visualization showing payment, settlement, fee, and ledger relationships with red dashed discrepancy edges.
3. Click on any node to inspect its degree connectivity in the side drawer, or click **"Accessible Table View"** for screen-reader mode.

---

### Step 5: Trigger the AI Investigation
1. Click the primary **`[ ⚡ Run AI Investigation ]`** button.
2. Watch the live agent trace execute through the pipeline:
   `Inspect records → Collect evidence → Synthesize diagnosis → Generate plan → Run simulation → Evaluate policy → Validate claims`.
3. In the findings section, verify the **Root Cause Explanation** and the **Verified Factual Statements** table, confirming each claim is backed by verified evidence UUIDs.

---

### Step 6: Simulate Resolution & Review Policy
1. Click the **"🔮 Resolution Simulator"** tab.
2. Inspect the **Cumulative Financial Delta** grid verifying the zero-sum balance ($\Delta \text{System Net} = 0.00\text{ paise}$).
3. Review the **Policy Gate** badge (`HUMAN_REVIEW_REQUIRED` or `AUTO_RESOLVABLE`).
4. In the **Human Sign-Off Gate**, enter an approval note and click **`[ ✓ Approve & Authorize ]`**.

---

### Step 7: Verify Cryptographic Audit Trail (`/audit`)
1. Navigate to **Audit Timeline** in the left sidebar.
2. Observe the newly minted immutable SHA-256 event block added to the cryptographic audit chain with verified tamper-free status.
