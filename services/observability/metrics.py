"""
FinResolve AI — Observability & Metrics Foundation

Lightweight in-memory metrics registry tracking throughput, errors, latency, and reconciliation outcomes.
Designed for export to OpenTelemetry / Prometheus.
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict
from typing import Any


class MetricsRegistry:
    """Thread-safe application metrics registry."""

    def __init__(self):
        self._lock = threading.Lock()
        self._counters: dict[str, int] = defaultdict(int)
        self._latencies: dict[str, list[float]] = defaultdict(list)
        self._start_time = time.time()

    def increment(self, metric_name: str, value: int = 1, labels: dict[str, str] | None = None) -> None:
        """Increment a named counter."""
        lbl_str = f"{{{','.join(f'{k}={v}' for k, v in sorted((labels or {}).items()))}}}" if labels else ""
        key = f"{metric_name}{lbl_str}"
        with self._lock:
            self._counters[key] += value

    def observe_latency(self, metric_name: str, duration_seconds: float) -> None:
        """Record latency duration."""
        with self._lock:
            self._latencies[metric_name].append(duration_seconds)
            # Keep rolling window of last 1000 observations
            if len(self._latencies[metric_name]) > 1000:
                self._latencies[metric_name].pop(0)

    def get_summary(self) -> dict[str, Any]:
        """Generate structured snapshot of all application metrics."""
        with self._lock:
            latency_summary = {}
            for k, v in self._latencies.items():
                if v:
                    sorted_v = sorted(v)
                    p50 = sorted_v[len(sorted_v) // 2]
                    p95 = sorted_v[int(len(sorted_v) * 0.95)]
                    mean = sum(v) / len(v)
                    latency_summary[k] = {
                        "count": len(v),
                        "mean_ms": round(mean * 1000, 2),
                        "p50_ms": round(p50 * 1000, 2),
                        "p95_ms": round(p95 * 1000, 2),
                    }

            return {
                "uptime_seconds": int(time.time() - self._start_time),
                "counters": dict(self._counters),
                "latencies": latency_summary,
            }

    def reset(self) -> None:
        """Reset metrics (useful in unit tests)."""
        with self._lock:
            self._counters.clear()
            self._latencies.clear()
            self._start_time = time.time()


# Global metrics registry
global_metrics = MetricsRegistry()
