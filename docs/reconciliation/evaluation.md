# FinResolve AI — Evaluation Harness & Benchmark Methodology

## Overview

The evaluation harness measures the deterministic reconciliation engine against ground-truth annotations created during synthetic dataset generation.

---

## Strict Ground-Truth Isolation

```
  ┌─────────────────────────────────────────────────────────────┐
  │                    ReconciliationCase                       │
  │  ┌───────────────────────┐       ┌───────────────────────┐  │
  │  │   case.observed       │       │   case.ground_truth   │  │
  │  └───────────┬───────────┘       └───────────┬───────────┘  │
  └──────────────┼───────────────────────────────┼──────────────┘
                 │                               │
                 ▼ (ONLY Input)                  │
  ┌───────────────────────────────┐              │
  │     ReconciliationEngine      │              │
  └──────────────┬────────────────┘              │
                 │                               │
                 ▼ Output                        ▼ Post-Inference
  ┌───────────────────────────────┐  ┌───────────────────────────┐
  │     ReconciliationResult      ├──►    BenchmarkEvaluator     │
  └───────────────────────────────┘  └───────────────────────────┘
```

1. **Inference Phase**: The engine receives `case.observed` records ONLY. It has zero knowledge of `ground_truth` or `corruptions`.
2. **Post-Inference Evaluation**: The evaluator receives both the `ReconciliationResult` and ground-truth annotations to compute unvarnished metrics.

---

## Measured Evaluation Metrics

| Metric | Definition |
| :--- | :--- |
| **Discrepancy Precision** | $\frac{\text{True Positives}}{\text{True Positives} + \text{False Positives}}$ |
| **Discrepancy Recall** | $\frac{\text{True Positives}}{\text{True Positives} + \text{False Negatives}}$ |
| **Discrepancy F1 Score** | $2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$ |
| **Classification Accuracy** | $\frac{\text{Correctly Classified Discrepancy Types}}{\text{Total Detected True Discrepancies}}$ |
| **Exact Case Accuracy** | $\frac{\text{Exact Case Outcome Matches}}{\text{Total Cases Evaluated}}$ |
| **Mean Latency per Case** | $\frac{\text{Total Execution Time (ms)}}{\text{Total Cases Evaluated}}$ |

---

## Running the Benchmark CLI

```bash
# Evaluate 100 cases with seed 42
python -m services.reconciliation.evaluate --cases 100 --seed 42

# Evaluate 500 mixed cases
python -m services.reconciliation.evaluate --cases 500 --seed 42 --difficulty mixed
```
