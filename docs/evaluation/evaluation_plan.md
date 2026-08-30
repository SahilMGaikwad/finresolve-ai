# FinResolve AI — Evaluation Plan

**Version**: 1.0
**Date**: 2026-08-30
**Status**: Methodology defined — no results yet

---

## Overview

This document defines the experimental methodology for evaluating FinResolve AI. All metrics will be computed from actual system execution against synthetic datasets with known ground truth. No metrics are hardcoded, fabricated, or estimated.

---

## 1. Evaluation Objectives

1. Measure the accuracy and reliability of each pipeline stage.
2. Identify failure modes and their frequency.
3. Quantify the system's ability to correctly diagnose and resolve discrepancies.
4. Measure the appropriate use of human escalation (neither too aggressive nor too passive).
5. Establish performance baselines for future improvement.

---

## 2. Metrics Definitions

### 2.1 Matching Metrics

| Metric | Formula | Target |
|--------|---------|--------|
| **Match Precision** | True Matches / (True Matches + False Matches) | TBD after baseline |
| **Match Recall** | True Matches / (True Matches + Missed Matches) | TBD after baseline |
| **Match F1** | 2 × (Precision × Recall) / (Precision + Recall) | TBD after baseline |
| **Match Rate** | Matched Records / Total Records | TBD after baseline |
| **False Match Rate** | False Matches / Total Matches | TBD after baseline |

### 2.2 Discrepancy Detection Metrics

| Metric | Formula | Target |
|--------|---------|--------|
| **Detection Precision** | True Discrepancies Detected / Total Discrepancies Flagged | TBD |
| **Detection Recall** | True Discrepancies Detected / Total True Discrepancies | TBD |
| **Detection F1** | Harmonic mean of above | TBD |

### 2.3 Diagnosis Metrics

| Metric | Formula | Target |
|--------|---------|--------|
| **Root-Cause Accuracy** | Correct Root Causes / Total Diagnosed Discrepancies | TBD |
| **Top-K Root-Cause Accuracy** | Correct Root Cause in Top K Hypotheses / Total Diagnosed | TBD |
| **Hypothesis Quality** | Average rank of correct hypothesis in hypothesis list | TBD |

### 2.4 Resolution Metrics

| Metric | Formula | Target |
|--------|---------|--------|
| **Auto-Resolution Accuracy** | Correct Auto-Resolutions / Total Auto-Resolutions | TBD |
| **Auto-Resolution Rate** | Auto-Resolved Cases / Total Resolvable Cases | TBD |
| **Human Escalation Rate** | Escalated Cases / Total Cases | TBD |
| **Appropriate Escalation Rate** | Cases Correctly Escalated / Total Escalated | TBD |
| **Unresolved Exception Rate** | Unresolved Cases / Total Cases | TBD |

### 2.5 Performance Metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| **Throughput** | Records processed per second (end-to-end) | TBD |
| **Latency P50** | Median time from ingestion to resolution | TBD |
| **Latency P95** | 95th percentile latency | TBD |
| **Latency P99** | 99th percentile latency | TBD |

---

## 3. Synthetic Dataset Requirements

### 3.1 Dataset Properties

- **Record types**: Payments, orders, settlements, refunds, fees, ledger entries, payouts
- **Scale**: Minimum 10,000 transaction groups; target 100,000 for statistical significance
- **Discrepancy rate**: Configurable; default ~15% of transaction groups contain at least one discrepancy
- **Discrepancy types**: Balanced distribution across:
  - Fee deduction discrepancy
  - Partial settlement
  - Refund adjustment
  - Timing mismatch
  - Duplicate record
  - Missing record
  - Incorrect amount
  - Multi-cause discrepancy (compound)

### 3.2 Ground Truth Labels

Every synthetic record group must include:
- `has_discrepancy: bool` — Whether a true discrepancy exists
- `discrepancy_type: str | None` — The ground-truth discrepancy type
- `root_cause: str | None` — The ground-truth root cause
- `correct_resolution: dict | None` — The correct resolution action
- `should_escalate: bool` — Whether human review is the correct action (e.g., ambiguous or multi-cause cases)

### 3.3 Dataset Variants

| Variant | Purpose |
|---------|---------|
| **Easy** | Clear single-cause discrepancies, deterministic matching | Baseline sanity check |
| **Medium** | Mix of single and multi-cause, some fuzzy matches | Primary evaluation |
| **Hard** | Multi-cause discrepancies, ambiguous matches, edge cases | Stress testing |
| **Adversarial** | Deliberately crafted to exploit known weaknesses | Security evaluation |

### 3.4 Reproducibility

All datasets must be reproducible via a seed parameter:
```
python -m data.generators.generator --seed 42 --variant medium --size 10000
```

---

## 4. Evaluation Protocol

### 4.1 Pipeline Evaluation

Each pipeline stage is evaluated independently before end-to-end evaluation:

```
Stage 1: Ingestion    → Validates record acceptance/rejection accuracy
Stage 2: Normalization → Validates field mapping correctness
Stage 3: Matching      → Computes match precision/recall/F1
Stage 4: Detection     → Computes detection precision/recall/F1
Stage 5: Diagnosis     → Computes root-cause accuracy
Stage 6: Simulation    → Validates simulation correctness against known scenarios
Stage 7: Resolution    → Computes auto-resolution accuracy and escalation rates
```

### 4.2 End-to-End Evaluation

```
Input:   Synthetic dataset (labeled)
Process: Full pipeline execution
Output:  Metrics report with per-stage and end-to-end results
```

### 4.3 Ablation Studies

To understand the contribution of each component:

| Ablation | What is removed | Measures |
|----------|----------------|----------|
| No ML | Remove anomaly detection ML | Impact of ML on diagnosis quality |
| No LLM | Remove LLM hypothesis generation | Impact of LLM on root-cause accuracy |
| No counterfactual | Remove simulation engine | Impact of simulation on resolution quality |
| Rules only | Only deterministic matching and rules | Baseline without any AI |

### 4.4 Confidence Calibration

Evaluate whether reported confidence scores are well-calibrated:
- For cases where the system reports confidence X%, approximately X% should be correct.
- Plot reliability diagrams (calibration curves).
- Compute Expected Calibration Error (ECE).

---

## 5. Statistical Rigor

### 5.1 Confidence Intervals

All metrics will be reported with 95% confidence intervals, computed via:
- Bootstrap resampling (1,000 iterations) for precision, recall, accuracy metrics.
- Direct computation for throughput and latency metrics.

### 5.2 Significance Testing

When comparing configurations (e.g., with/without LLM):
- Use paired bootstrap tests for metric comparison.
- Report p-values and effect sizes.
- Use Bonferroni correction for multiple comparisons.

### 5.3 Multiple Runs

Metrics will be computed over a minimum of 3 independent runs (different seeds) to account for non-deterministic components (LLM, ML).

---

## 6. Reporting

### 6.1 Metrics Report Structure

```
# Evaluation Report — [Date] — [Dataset Variant] — [Run ID]

## Summary
- Dataset: [variant, size, seed]
- Pipeline version: [git hash]
- Configuration: [key config parameters]

## Per-Stage Metrics
[table of metrics with confidence intervals]

## End-to-End Metrics
[table of metrics with confidence intervals]

## Failure Analysis
- Top failure modes
- Examples of incorrect resolutions
- Examples of missed discrepancies

## Confidence Calibration
[reliability diagram]
[ECE score]

## Performance
[throughput and latency distributions]
```

### 6.2 What We Will NOT Report

- Hardcoded or estimated metric values
- Metrics computed on trivially easy datasets only
- Accuracy on the training set (if applicable)
- Results without confidence intervals
- Comparisons without significance testing

---

## 7. Evaluation Schedule

| Phase | Evaluation Focus |
|-------|-----------------|
| Phase 2 | Synthetic data generator validation |
| Phase 3 | Matching and detection metrics |
| Phase 4 | End-to-end metrics with counterfactual engine |
| Phase 5 | Agent orchestration metrics |
| Phase 6 | Full evaluation with ablation studies |

---

## References

- [ARCHITECTURE.md](../../ARCHITECTURE.md) — System architecture
- [ADR-001](../decisions/ADR-001-project-architecture.md) — Architecture decisions
