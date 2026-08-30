from __future__ import annotations

import platform
import sys
import time
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data.generators.config import GeneratorConfig
from data.generators.generate import generate_dataset
from services.reconciliation.engine import ReconciliationEngine


def run_smoke_test(num_cases: int = 500, seed: int = 42) -> None:
    print(f"Generating {num_cases} synthetic cases (seed={seed})...")
    config = GeneratorConfig(seed=seed, num_cases=num_cases, corruption_rate=0.15)
    cases, _ = generate_dataset(config)

    engine = ReconciliationEngine()
    latencies_ms: list[float] = []

    print(f"Benchmarking deterministic reconciliation engine across {num_cases} cases...")
    overall_start = time.perf_counter()

    for case in cases:
        case_start = time.perf_counter()
        _ = engine.reconcile_case(case)
        case_end = time.perf_counter()
        latencies_ms.append((case_end - case_start) * 1000.0)

    overall_elapsed = time.perf_counter() - overall_start
    throughput = num_cases / overall_elapsed

    latencies_ms.sort()
    mean_lat = sum(latencies_ms) / len(latencies_ms)
    p50_lat = latencies_ms[int(len(latencies_ms) * 0.50)]
    p90_lat = latencies_ms[int(len(latencies_ms) * 0.90)]
    p95_lat = latencies_ms[int(len(latencies_ms) * 0.95)]
    p99_lat = latencies_ms[int(len(latencies_ms) * 0.99)]

    print("\n" + "=" * 65)
    print("  FinResolve AI — Performance Smoke Test Report")
    print("=" * 65)
    print(f"  Environment:        {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"  Python Version:     {sys.version.split()[0]}")
    print(f"  Cases Processed:    {num_cases}")
    print(f"  Total Duration:     {overall_elapsed:.3f} s")
    print(f"  Throughput:         {throughput:.1f} cases/sec")
    print("-" * 65)
    print(f"  Mean Latency:       {mean_lat:.2f} ms")
    print(f"  p50 (Median):       {p50_lat:.2f} ms")
    print(f"  p90 Latency:        {p90_lat:.2f} ms")
    print(f"  p95 Latency:        {p95_lat:.2f} ms")
    print(f"  p99 Latency:        {p99_lat:.2f} ms")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    run_smoke_test()
