# Controlled Benchmark & Evaluation Methodology — FinResolve AI

## 1. Benchmark Dataset Configuration
- **Total Cases**: 500 Cases (Seed: 42)
- **Clean Cases**: 428 Cases (85.6%)
- **Corrupted Cases**: 72 Cases (14.4%)
  - Single Corruptions: 45 Cases
  - Compound Corruptions: 27 Cases

---

## 2. Key Benchmark Results

| Metric | Result | Target / Baseline | Status |
| :--- | :---: | :---: | :---: |
| **Total Factual Claims Evaluated** | 1,000 | 1,000 | **100% Evaluated** |
| **Verified Claims** | 1,000 | 1,000 | **100.00%** |
| **Unsupported Claims** | 0 | 0 | **0.00% Hallucination** |
| **Zero-Harm Safety Rate** | 100.00% | 100.00% | **Zero Hazardous Actions** |
| **Plan Feasibility Rate** | 29.17% | >25.00% | **21 Valid Plans Generated** |
| **Mean Investigation Latency** | 0.58 ms | <100 ms | **Sub-Millisecond Speed** |

---

## 3. Case Outcome Breakdown
- **Completed Investigations**: 429 Cases (428 Clean + 1 Low-Risk Auto-Resolved)
- **Human Review Required**: 27 Cases (20 High-Value Plans + 7 Unresolvable/Timing)
- **Blocked Investigations**: 44 Cases (Failed simulation invariants)
