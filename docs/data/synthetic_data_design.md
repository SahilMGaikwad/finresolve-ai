# FinResolve AI — Synthetic Data Design

## Purpose

This document describes the design of the synthetic data generator.
The generator produces deterministic, reproducible reconciliation datasets
with labeled ground truth for evaluation.

**This data is synthetic.** It is designed to be structurally realistic
but does not contain any real financial data, real merchants, real customers,
or real payment information.

## Architecture

```
GeneratorConfig (seed, num_cases, corruption_rate, difficulty)
       │
       ▼
generate_merchants(config, rng) → [MerchantProfile]
       │
       ▼
  for each case:
       │
       ├── build_clean_case_records(index, merchant, config, rng)
       │   └── creates: order, payment, fees, settlement, ledger entries
       │       └── all relationships valid, amounts consistent
       │
       ├── deep_copy → observed records
       │
       ├── should_corrupt? (based on corruption_rate)
       │   └── apply_corruptions(observed, internal, difficulty, rng)
       │       └── mutates observed only, produces CorruptionLabels
       │
       ├── build_expected_outcome(corruptions, difficulty)
       │
       └── ReconciliationCase(ground_truth, observed, corruptions, expected_outcome)
       │
       ▼
write to disk (cases.json) + build manifest (manifest.json)
```

## Randomization Strategy

All randomization uses `random.Random(seed)`. This ensures:

1. **Same seed + same config = same dataset.** Byte-for-byte identical.
2. **Different seed = different dataset.** Different amounts, merchants, corruptions.
3. **Adding cases does not change existing cases.** The RNG is consumed in sequence.

A single RNG instance is created from the seed and passed through the
entire generation pipeline. No global state (`random.random()`) is used.

## Distributions

| Parameter | Distribution | Range |
|-----------|-------------|-------|
| Transaction amount | Uniform | config.min_amount_minor – config.max_amount_minor |
| Payment method | Uniform | card, upi, netbanking, wallet, bank_transfer |
| Order timestamp | Uniform | config.start_date – config.end_date |
| Settlement delay | Uniform | 1–7 days (per merchant) |
| Fee rate variation | Uniform | ±50 bps around base rate |
| Refund fraction | Uniform | 20%–100% of payment |
| Corruption type | Uniform | from difficulty-specific pool |
| Difficulty (mixed) | Weighted | 40% easy, 35% medium, 25% hard |

**Limitations**: Real financial data is not uniformly distributed.
Transaction amounts follow power-law distributions, and settlement
delays depend on business type. These simplifications are acknowledged.

## Configurability

All generation parameters are captured in `GeneratorConfig`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| seed | 42 | Random seed |
| num_cases | 1000 | Number of cases |
| corruption_rate | 0.08 | Fraction of corrupted cases |
| difficulty | "mixed" | easy/medium/hard/mixed |
| merchant_count | 10 | Number of merchants |
| min_amount_minor | 10,000 | ₹100 minimum |
| max_amount_minor | 10,000,000 | ₹1,00,000 maximum |
| currency | "INR" | Default currency |
| refund_probability | 0.15 | Fraction with refunds |
| platform_fee_bps | 200 | 2% platform fee |
| gst_on_fee_bps | 1800 | 18% GST on fee |

## Record Generation Chain

For each case, the generator builds:

1. **Order** — the merchant order
2. **Payment** — customer payment for the order (same amount)
3. **Platform Fee** — fee on the payment (basis points)
4. **GST Fee** — GST on the platform fee (basis points)
5. **Settlement** — net amount after fee deduction
6. **Ledger Entries** — payment credit, fee debit, settlement debit
7. *(Optional)* **Refund** — partial or full refund with reversal ledger entry

All amounts are computed using integer arithmetic only.

## Reproducibility

To reproduce a dataset:

```bash
python -m data.generators.generate --seed 42 --cases 1000 --corruption-rate 0.08
```

The manifest contains a `configuration_hash` that uniquely identifies the
configuration parameters. Two runs with the same seed and configuration hash
will produce identical datasets.

## Limitations

1. **Uniform distributions**: Real data has heavier tails and seasonal patterns.
2. **Single payment per order**: Real orders may have multiple payment attempts.
3. **No multi-currency cases**: All records in a case use the same currency.
4. **No cascading dependencies**: Cases are independent of each other.
5. **Synthetic merchant names**: Obviously not real businesses.
6. **No payment gateway webhooks**: Real systems have event-driven data flow.

These limitations are acceptable for a Phase 2 data foundation.
Phase 3+ can enhance distributions as needed.
