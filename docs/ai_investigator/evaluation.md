# FinResolve AI — AI Investigator Evaluation Methodology

## 1. Core Evaluation Metrics

1. **Unsupported Claim Rate**:
   $$\text{Unsupported Claim Rate} = \frac{\text{Unsupported Claims}}{\text{Total Factual Claims}} = 0.00\% \text{ (Target)}$$
2. **Grounding Accuracy Rate**:
   $$\text{Grounding Accuracy} = \frac{\text{Verified Evidence-Grounded Claims}}{\text{Total Claims}} = 100.00\%$$
3. **Multi-Step Plan Feasibility**:
   $$\text{Plan Feasibility} = \frac{\text{Simulated Valid Composite Plans}}{\text{Total Corrupted Cases}}$$
4. **Zero-Harm Safety Rate**:
   $$\text{Zero-Harm Rate} = 100.00\% \text{ (0 Imbalanced Plans Approved)}$$

---

## 2. Benchmark CLI Commands

```bash
# Run 100-case AI Investigator evaluation
python -m services.investigator.evaluate --cases 100 --seed 42

# Run 500-case evaluation with auto-resolve enabled
python -m services.investigator.evaluate --cases 500 --seed 42 --auto-resolve
```
