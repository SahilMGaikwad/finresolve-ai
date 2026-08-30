# 5-Minute Video Pitch Script — FinResolve AI

**Title**: FinResolve AI — Counterfactual Financial Reconciliation & Resolution Engine
**Presenter**: Sahil Gaikwad (Candidate for Razorpay AI Builder Internship 2026)
**Total Target Time**: 5 Minutes (300 Seconds)

---

### [0:00 – 0:30] Problem Statement
> *"At payment gateways like Razorpay, millions of transactions generate fragmented financial records daily across payments, settlements, fees, refunds, and bank ledgers. When these records fail to balance, operations teams are left with binary mismatch alerts and zero root-cause explanation. Analysts spend countless hours manually cross-referencing bank UTRs and tax invoices, while blind automated correction scripts risk catastrophic financial loss by mutating databases without proof of ledger balance."*

---

### [0:30 – 1:00] The FinResolve AI Solution
> *"We built FinResolve AI around a core principle: **AI can investigate. It cannot move money by itself.**
> FinResolve AI replaces brittle heuristics with an evidence-grounded, closed-loop financial controller. It reconciles records deterministically, constructs a multi-entity Evidence Graph, orchestrates an AI investigation agent to diagnose root causes, simulates proposed resolutions in virtual memory, and gates actions through deterministic policy rules and human sign-offs."*

---

### [1:00 – 1:45] Live Demo: The Suspicious Case
> *(Screen Share: Analyst Command Center Dashboard & Case Explorer)*
> *"Let’s look at the live Analyst Command Center. On our Executive Dashboard, we load our 50-case benchmark. In the Case Explorer, we filter for flagged discrepancies and open `CASE-000003`.
> Immediately, we see the crimson alert banner: the gateway captured ₹80,981.19, fee deducted was ₹2,197.83, but settlement net was only ₹67,107.67—leaving an unexplained variance of ₹11,675.69.
> Switching to the Evidence Graph tab, we visually trace the broken relationship edge connecting the payment and settlement entities."*

---

### [1:45 – 2:30] Evidence-Grounded AI Investigation
> *(Screen Share: AI Investigation Console & Verified Claims Table)*
> *"Now, we click **`Run AI Investigation`**.
> The AI agent executes its bounded finite state machine, calling typed inspection tools across the Evidence Graph. In seconds, it synthesizes the root cause: an arithmetic omission in the merchant’s fee deduction tranche.
> Crucially, look at the Verified Factual Claims table. Every statement made by the AI is independently validated by our `ClaimValidator` against observable records. In our 500-case evaluation, FinResolve achieved a **0.00% unsupported claim rate**."*

---

### [2:30 – 3:30] Counterfactual Resolution Simulation
> *(Screen Share: Resolution Simulator & Before/After Table)*
> *"Instead of blindly executing a fix, the agent generates a multi-step resolution plan and passes it to our **Counterfactual Simulator**.
> The simulator deep-clones the financial state in isolated memory and applies a settlement balance adjustment. It then re-runs closed-loop reconciliation and verifies the double-entry accounting conservation law:
> $\Delta \text{Merchant} + \Delta \text{Fee} + \Delta \text{Tax} + \Delta \text{Customer} = 0.00\text{ paise}$.
> Because the simulation proves that zero residual discrepancies remain, the plan is marked valid."*

---

### [3:30 – 4:15] Deterministic Policy Gate & Human Approval
> *(Screen Share: Policy Gate & Approval Drawer)*
> *"Next, the plan enters the **Deterministic Policy Engine**.
> Under Rule `POL-003`, automated resolution is permitted only for low-risk adjustments up to ₹5,000. Because this adjustment is ₹11,675.69, the policy engine gates the proposal to **`HUMAN_REVIEW_REQUIRED`**.
> Furthermore, our approval workflow strictly enforces **separation of duties**: as the analyst who proposed the investigation, I cannot self-approve. An authorized approver reviews the simulation, enters an audit note, and signs off."*

---

### [4:15 – 4:40] Cryptographic Audit Trail
> *(Screen Share: Audit Timeline)*
> *"Finally, we navigate to the **Audit Timeline**.
> Every single event—the investigation start, tool execution, simulation result, and approver signature—is cryptographically chained using SHA-256 blocks, ensuring complete compliance, tamper-resistance, and non-repudiation."*

---

### [4:40 – 5:00] Closing Statement
> *"To summarize:
> **AI investigates. Evidence verifies. Simulation tests. Policy governs. Humans approve when necessary.**
> FinResolve AI provides the explainability, mathematical rigor, and safety controls required for real-world enterprise financial operations.
> Thank you for considering my submission for the Razorpay AI Builder Internship 2026."*
