# FinResolve AI — Financial Delta Accounting & Conservation Laws

## Overview

Every candidate resolution produces a structured [`FinancialDelta`](file:///Users/sahilgaikwad/finresolve-ai/data/schemas/resolution.py) that models the exact balance shifts across all system accounts in integer minor currency units (paise).

---

## 1. Closed-System Conservation Law

In a closed financial system, money is neither created nor destroyed:
$$\Delta \text{Merchant} + \Delta \text{Fee} + \Delta \text{Tax} + \Delta \text{Customer} = 0$$

- **Merchant Balance Delta**: $\Delta \text{Settlement Net}$
- **Platform Fee Delta**: $\Delta \text{Platform Fee Amount}$
- **Tax Liability Delta**: $\Delta \text{GST Tax Amount}$
- **Customer Refund Delta**: $\Delta \text{Customer Refund Amount}$

---

## 2. Example Delta Calculation

### Scenario: Fee Overcharge Reversal
- **Observed**: Fee charged was ₹300 (30,000 paise).
- **Expected**: Agreed fee rate produces ₹200 (20,000 paise).
- **Corrective Action**: Fee adjustment of -₹100 (-10,000 paise) + Tax adjustment of -₹18 (-1,800 paise).
- **Financial Delta**:
  - $\Delta \text{Merchant} = +11,800\text{ paise}$ (+₹118.00)
  - $\Delta \text{Fee} = -10,000\text{ paise}$ (-₹100.00)
  - $\Delta \text{Tax} = -1,800\text{ paise}$ (-₹18.00)
  - $\Delta \text{Customer} = 0\text{ paise}$
  - **Net System Delta**: $+11,800 - 10,000 - 1,800 + 0 = 0\text{ paise}$ (**Balanced**)
