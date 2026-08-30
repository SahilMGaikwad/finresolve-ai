# FinResolve AI — Counterfactual Evaluation Methodology

## Overview

The Counterfactual Evaluation Harness validates the precision, feasibility, and safety of simulated resolution proposals against ground-truth benchmarks.

---

## 1. Core Metrics

1. **Resolution Feasibility Rate**:
   $$\text{Feasibility} = \frac{\text{Simulated Valid Proposals}}{\text{Total Corrupted Cases}}$$
2. **Zero-Harm Safety Rate**:
   $$\text{Zero-Harm Rate} = \frac{\text{Blocked Unsafe Actions}}{\text{Total Unsafe Proposals}} = 100.00\%$$
3. **Policy Gating Accuracy**: Evaluates correct routing between `AUTO_RESOLVABLE` and `HUMAN_REVIEW` based on risk and value thresholds.

---

## 2. Evaluation Commands

```bash
# Run 100-case evaluation benchmark
python -m services.counterfactual.evaluate --cases 100 --seed 42

# Run 500-case evaluation benchmark with auto-resolve enabled
python -m services.counterfactual.evaluate --cases 500 --seed 42 --auto-resolve
```
