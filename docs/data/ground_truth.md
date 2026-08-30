# FinResolve AI — Ground Truth Design

## Purpose

Ground truth labels enable evaluation of the reconciliation system.
For every generated case, we know exactly what the correct answer is.

## Structure

Each `ReconciliationCase` contains:

### `ground_truth: CaseRecords`

The clean, correct version of all records. These represent what the
financial state **actually is**. Ground truth is never modified by
the corruption engine.

### `observed: CaseRecords`

The records as the reconciliation system sees them. These may have
been corrupted by the corruption engine. The system's job is to
detect and diagnose discrepancies between what it observes and
what the correct state should be.

### `corruptions: list[CorruptionLabel]`

Exact description of every corruption applied. Each label records:
- What type of corruption was applied
- Which record and field were modified
- The original (correct) and corrupted values

### `expected_outcome: ExpectedOutcome`

What a perfect reconciliation system should conclude:

| Field | Type | Description |
|-------|------|-------------|
| has_discrepancy | bool | Is there a true discrepancy? |
| discrepancy_type | str? | e.g., "settlement_amount_mismatch" |
| root_cause | str? | e.g., "incorrect_settlement_calculation" |
| correct_resolution | dict? | Actions to fix the discrepancy |
| should_escalate | bool | Should this go to human review? |

## How Evaluation Uses Ground Truth

### Detection Evaluation
```
For each case:
  system_detected = system.detect_discrepancy(case.observed)
  ground_truth = case.expected_outcome.has_discrepancy

  if system_detected == True and ground_truth == True:
      → True Positive
  if system_detected == True and ground_truth == False:
      → False Positive
  if system_detected == False and ground_truth == True:
      → False Negative (missed discrepancy)
  if system_detected == False and ground_truth == False:
      → True Negative
```

### Diagnosis Evaluation
```
For corrupted cases:
  system_diagnosis = system.diagnose(case.observed)
  correct_type = case.expected_outcome.discrepancy_type
  correct_cause = case.expected_outcome.root_cause

  → Compare system's diagnosis against ground truth labels
```

### Resolution Evaluation
```
For corrupted cases:
  system_resolution = system.resolve(case.observed)
  correct_resolution = case.expected_outcome.correct_resolution

  → Compare proposed fix against known correct fix
```

## Escalation Ground Truth

Some cases **should** be escalated to human review:
- Cases with multiple corruption types (compound discrepancies)
- Hard-difficulty cases
- Cases with ambiguous corruption types (STATUS_INCONSISTENCY, INCORRECT_REFERENCE)

A system that auto-resolves everything is not correct — it should
recognize when it cannot confidently diagnose.

## Limitations of Synthetic Ground Truth

1. **Known corruption types only**: The system is evaluated on 8 specific
   corruption types. Real-world discrepancies may be novel.

2. **Deterministic difficulty**: Difficulty is assigned, not emergent.
   Real discrepancies are difficult for contextual reasons.

3. **Single correct resolution**: In reality, multiple resolutions may
   be acceptable. Our ground truth specifies one.

4. **No temporal dynamics**: Cases are independent snapshots. Real
   reconciliation involves temporal patterns across cases.

5. **Synthetic ≠ real**: Performance on synthetic data does not guarantee
   performance on real financial data.

These limitations must be disclosed in any evaluation results.
