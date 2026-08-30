# Data — Generators

This directory will contain the synthetic data generator for creating
financial records with known ground truth.

## Planned Components (Phase 2)

- `generator.py` — Main data generation orchestrator
- `merchants.py` — Synthetic merchant profile generation
- `transactions.py` — Transaction generation with configurable distributions
- `discrepancies.py` — Controlled discrepancy injection with labeled causes
- `ground_truth.py` — Ground truth label generation for evaluation

## Design Principles

- All generated data must have ground-truth labels for every discrepancy
- Discrepancy types must cover: fee deductions, partial settlements, refund adjustments,
  timing mismatches, duplicate records, incorrect amounts, missing records
- Data must be realistic enough to exercise all system components
- Generation must be reproducible via seed parameters
